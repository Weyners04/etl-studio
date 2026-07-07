"""Routes FastAPI : surface unique sur le pipeline validate -> interpret -> execute + IA."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.ai import generate_ir
from app.ir import IRGraph
from app.interpreter import ValidationError, build_plan, execute, validate
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
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    plan = build_plan(graph)
    outputs = execute(plan)  # NotImplementedError tant que les nœuds ne sont pas branchés
    return {"status": "ok", "node_count": len(outputs)}


@router.post("/ai/generate")
def ai_generate(payload: GeneratePayload) -> IRGraph:
    return generate_ir(payload.prompt)
