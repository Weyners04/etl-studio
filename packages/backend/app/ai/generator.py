"""Couche IA (V2) — prompt en langage naturel -> IR contrainte.

Principe : le LLM n'émet jamais de code. Il est forcé, via structured output / function
calling, à produire un objet conforme au schéma IRGraph. La sortie est ensuite validée ;
si elle est invalide, on renvoie l'erreur au modèle pour réparation (boucle V2).
"""
from __future__ import annotations

from app.ir import IRGraph
from app.interpreter import ValidationError, validate

# Le schéma de contrainte du LLM EST le schéma de l'IR : une seule source de vérité.
IR_TOOL_SCHEMA = IRGraph.model_json_schema()

SYSTEM_PROMPT = (
    "Tu es un générateur de pipelines ETL. À partir de la demande de l'utilisateur, produis "
    "UNIQUEMENT un graphe IR (nodes/edges) conforme au schéma fourni. N'émets jamais de code."
)


def generate_ir(prompt: str, *, max_repairs: int = 2) -> IRGraph:
    """Génère une IR valide à partir d'un prompt.

    TODO (Phase 2) :
      - appeler le LLM avec IR_TOOL_SCHEMA en function calling / structured output ;
      - parser la réponse en IRGraph ;
      - valider via validate(); en cas d'échec, renvoyer l'erreur au modèle (max_repairs).
    """
    raise NotImplementedError("Couche IA prévue en Phase 2 (voir docs/roadmap.md).")


def _validate_or_raise(graph: IRGraph) -> IRGraph:
    try:
        validate(graph)
    except ValidationError:
        raise
    return graph
