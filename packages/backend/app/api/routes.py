"""Routes FastAPI : surface unique sur le pipeline validate -> interpret -> execute + IA."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.ai import generate_ir
from app.ir import IRGraph
from app.interpreter import ExecutionError, ValidationError, build_plan, execute, validate
from app.nodes.registry import get_node_descriptor, registered_types

router = APIRouter()


class GeneratePayload(BaseModel):
    prompt: str


class NodeInfo(BaseModel):
    type: str
    category: str
    params_schema: dict[str, Any]


@router.get("/nodes")
def list_nodes() -> list[NodeInfo]:
    """Types de nœuds connus avec leur catégorie et le schéma JSON de leurs params."""
    return [
        NodeInfo(
            type=node_type,
            category=node_type.split(".")[0],
            params_schema=get_node_descriptor(node_type).params_model.model_json_schema(),
        )
        for node_type in registered_types()
    ]


@router.post("/jobs/validate")
def validate_job(graph: IRGraph) -> dict[str, str]:
    try:
        validate(graph)
    except ValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail={"message": str(exc), "node_id": exc.node_id, "node_type": exc.node_type},
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


@router.post("/ai/generate")
def ai_generate(payload: GeneratePayload) -> IRGraph:
    return generate_ir(payload.prompt)
