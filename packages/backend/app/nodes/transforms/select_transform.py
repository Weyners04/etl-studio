"""transform.select — projette un sous-ensemble de colonnes."""

from __future__ import annotations

from typing import Any

import polars as pl
from pydantic import BaseModel

from app.nodes.base import PortCardinality
from app.nodes.registry import register


class SelectTransformParams(BaseModel):
    columns: list[str]


@register(
    "transform.select",
    params_model=SelectTransformParams,
    ports=PortCardinality(min_in=1, max_in=None, min_out=0, max_out=None),
)
class SelectTransform:
    def run(self, params: SelectTransformParams, inputs: list[Any]) -> pl.LazyFrame:
        (lf,) = inputs
        return lf.select(params.columns)
