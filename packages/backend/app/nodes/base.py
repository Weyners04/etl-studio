"""Contrat d'une implémentation de nœud."""
from __future__ import annotations

from typing import Any, Protocol


class NodeImpl(Protocol):
    """Toute implémentation de nœud expose run(params, inputs) -> sortie."""

    def run(self, params: dict[str, Any], inputs: list[Any]) -> Any:
        ...
