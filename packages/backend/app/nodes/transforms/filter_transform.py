"""transform.filter — garde les lignes satisfaisant une condition simple.

La condition est structurée (column / operator / value) : aucun eval, jamais.
Phase 1 scope : une colonne, un opérateur binaire, une valeur scalaire.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel

from app.nodes.base import PortCardinality
from app.nodes.registry import register


class FilterTransformParams(BaseModel):
    column: str
    operator: Literal["==", "!=", ">", ">=", "<", "<="]
    value: int | float | str | bool


@register(
    "transform.filter",
    params_model=FilterTransformParams,
    ports=PortCardinality(min_in=1, max_in=None, min_out=0, max_out=None),
)
class FilterTransform:
    def run(self, params: dict[str, Any], inputs: list[Any]) -> Any:
        raise NotImplementedError("transform.filter non encore implémenté.")
