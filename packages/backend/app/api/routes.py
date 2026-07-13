"""Routes FastAPI : surface unique sur le pipeline validate -> interpret -> execute + IA."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.ai import generate_ir
from app.ir import IRGraph
from app.interpreter import (
    DebugExecutionError,
    ExecutionError,
    ValidationError,
    build_plan,
    execute,
    execute_debug,
    resolve_schemas,
    validate,
)
from app.nodes.registry import get_node_descriptor, registered_types

router = APIRouter()


class GeneratePayload(BaseModel):
    prompt: str


class NodeInfo(BaseModel):
    type: str
    category: str
    label: str
    description: str
    params_schema: dict[str, Any]


@router.get("/nodes")
def list_nodes() -> list[NodeInfo]:
    """Types de nœuds connus avec leur catégorie, métadonnées d'affichage et schéma params."""
    return [
        NodeInfo(
            type=node_type,
            category=node_type.split(".")[0],
            label=desc.label,
            description=desc.description,
            params_schema=desc.params_model.model_json_schema(),
        )
        for node_type in registered_types()
        for desc in [get_node_descriptor(node_type)]
    ]


@router.post("/jobs/validate")
def validate_job(graph: IRGraph) -> dict[str, str]:
    try:
        validate(graph)
    except ValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "error_type": "validation_error",
                "message": str(exc),
                "node_id": exc.node_id,
                "node_type": exc.node_type,
            },
        ) from exc
    return {"status": "ok"}


@router.post("/jobs/run")
def run_job(graph: IRGraph) -> dict[str, object]:
    try:
        validate(graph)
    except ValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "error_type": "validation_error",
                "message": str(exc),
                "node_id": exc.node_id,
                "node_type": exc.node_type,
            },
        ) from exc
    plan = build_plan(graph)
    try:
        outputs = execute(plan)
    except ExecutionError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "error_type": "execution_error",
                "message": str(exc),
                "node_id": exc.node_id,
                "node_type": exc.node_type,
                "category": exc.category.value,
            },
        ) from exc
    sink_outputs = [
        {"node_id": node_id, **value}
        for node_id, value in outputs.items()
        if isinstance(value, dict)
    ]
    return {"status": "ok", "outputs": sink_outputs}


@router.post("/jobs/debug")
def debug_job(graph: IRGraph) -> dict[str, object]:
    try:
        validate(graph)
    except ValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "error_type": "validation_error",
                "message": str(exc),
                "node_id": exc.node_id,
                "node_type": exc.node_type,
            },
        ) from exc
    plan = build_plan(graph)
    try:
        results = execute_debug(plan)
    except DebugExecutionError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "error_type": "execution_error",
                "message": str(exc.cause),
                "node_id": exc.cause.node_id,
                "node_type": exc.cause.node_type,
                "category": exc.cause.category.value,
                "partial_nodes": [
                    {"node_id": r.node_id, "row_count": r.row_count, "sample": r.sample}
                    for r in exc.partial
                ],
            },
        ) from exc
    nodes_out = [
        {"node_id": r.node_id, "row_count": r.row_count, "sample": r.sample} for r in results
    ]
    sink_outputs = [
        {"node_id": r.node_id, "written": r.written} for r in results if r.written is not None
    ]
    return {"status": "ok", "nodes": nodes_out, "outputs": sink_outputs}


@router.post("/jobs/schema")
def schema_job(graph: IRGraph) -> dict[str, object]:
    """Résout et propage les schémas de colonnes sans exécuter le job.

    Sources inaccessibles → schéma indéterminé (columns: null) propagé en aval.
    Ne lève jamais d'erreur pour cause de fichier manquant.
    """
    plan = build_plan(graph)
    results = resolve_schemas(plan)
    nodes_out: dict[str, object] = {}
    for node_id, resolution in results.items():
        entry: dict[str, object] = {
            "columns": (
                [{"name": c.name, "dtype": c.dtype} for c in resolution.schema]
                if resolution.schema is not None
                else None
            )
        }
        if resolution.warnings:
            entry["warnings"] = resolution.warnings
        nodes_out[node_id] = entry
    return {"status": "ok", "nodes": nodes_out}


@router.post("/ai/generate")
def ai_generate(payload: GeneratePayload) -> IRGraph:
    return generate_ir(payload.prompt)
