"""transform.filter — filtre les lignes sur une condition simple.

La condition est structurée (column / operator / value) : aucun eval, jamais.
L'expression Polars est construite via le module operator standard.
Phase 1 scope : une colonne, un opérateur binaire, une valeur scalaire.
"""

from __future__ import annotations

import operator as op
from typing import Any, Callable, Literal

import polars as pl
from pydantic import BaseModel

from app.nodes.base import PortCardinality
from app.nodes.registry import register

_OPS: dict[str, Callable[[pl.Expr, Any], pl.Expr]] = {
    "==": op.eq,
    "!=": op.ne,
    ">": op.gt,
    ">=": op.ge,
    "<": op.lt,
    "<=": op.le,
}


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
    def run(self, params: FilterTransformParams, inputs: list[Any]) -> pl.LazyFrame:
        lf: pl.LazyFrame = inputs[0]
        predicate = _OPS[params.operator](pl.col(params.column), params.value)
        return lf.filter(predicate)
