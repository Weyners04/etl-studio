"""Contrat d'une implémentation de nœud."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from pydantic import BaseModel


class NodeImpl(Protocol):
    """Toute implémentation de nœud expose run(params, inputs) -> sortie."""

    def run(self, params: dict[str, Any], inputs: list[Any]) -> Any: ...


@dataclass(frozen=True)
class PortCardinality:
    """Contraintes sur le nombre d'arêtes entrantes/sortantes d'un nœud.

    None signifie « non borné ». Exemples :
      source  → min_in=0, max_in=0  (aucune entrée)
      sink    → min_out=0, max_out=0 (aucune sortie)
      transform → min_in=1, max_in=None (au moins une entrée)
    """

    min_in: int
    max_in: int | None
    min_out: int
    max_out: int | None


@dataclass(frozen=True)
class NodeDescriptor:
    """Entrée du registre : regroupe impl, modèle de params et cardinalité."""

    impl: NodeImpl
    params_model: type[BaseModel]
    ports: PortCardinality
