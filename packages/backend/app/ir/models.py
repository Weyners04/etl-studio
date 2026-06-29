"""Modèles de la représentation intermédiaire (IR).

Ces modèles Pydantic ont un double rôle :
  1. valider toute IR entrante (éditeur visuel ou IA) ;
  2. servir de schéma de contrainte pour le structured output du LLM (couche IA, V2).

C'est la traduction Python du contrat défini dans packages/ir-schema/schema/ir.schema.json.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Position(BaseModel):
    """Position visuelle d'un nœud. Ignorée à l'exécution."""

    x: float = 0.0
    y: float = 0.0


class Node(BaseModel):
    id: str
    type: str = Field(
        ...,
        pattern=r"^(source|transform|sink)\.[a-z0-9_]+$",
        description="Type namespacé : categorie.nom (ex. source.csv, transform.filter).",
    )
    params: dict[str, Any] = Field(default_factory=dict)
    position: Position | None = None


class Edge(BaseModel):
    id: str
    source: str
    target: str
    source_port: str = Field(default="out", alias="sourcePort")
    target_port: str = Field(default="in", alias="targetPort")

    model_config = {"populate_by_name": True}


class IRGraph(BaseModel):
    version: str = "0.1.0"
    id: str
    name: str
    nodes: list[Node] = Field(default_factory=list)
    edges: list[Edge] = Field(default_factory=list)

    model_config = {"populate_by_name": True}

    def node_by_id(self, node_id: str) -> Node | None:
        return next((n for n in self.nodes if n.id == node_id), None)
