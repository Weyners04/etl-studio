"""Routes FastAPI : surface unique sur le pipeline validate -> interpret -> execute + IA."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.ai import generate_ir
from app.ir import IRGraph
from app.interpreter import ValidationError, build_plan, execute, validate
from app.nodes.registry import registered_types

router = APIRouter()


class GeneratePayload(BaseModel):
    prompt: str


@router.get("/nodes")
def list_nodes() -> dict[str, list[str]]:
    """Types de nœuds connus (pour peupler la palette de l'éditeur)."""
    return {"types": registered_types()}


@router.post("/jobs/validate")
def validate_job(graph: IRGraph) -> dict[str, str]:
    try:
        validate(graph)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
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
