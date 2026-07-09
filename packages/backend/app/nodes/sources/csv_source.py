"""source.csv — construit un plan de lecture CSV (LazyFrame Polars).

L'exécution effective est déclenchée par le sink en aval (lazy evaluation).
"""

from __future__ import annotations

from typing import Any, Literal

import polars as pl
from pydantic import BaseModel

from app.nodes.base import PortCardinality
from app.nodes.registry import register


class CsvSourceParams(BaseModel):
    path: str
    has_header: bool = True
    separator: Literal[",", ";"] = ","


@register(
    "source.csv",
    params_model=CsvSourceParams,
    ports=PortCardinality(min_in=0, max_in=0, min_out=0, max_out=None),
    label="CSVReader",
    description="Lit un fichier CSV et charge ses lignes dans le pipeline.",
)
class CsvSource:
    def run(self, params: CsvSourceParams, inputs: list[Any]) -> pl.LazyFrame:
        return pl.scan_csv(
            params.path,
            has_header=params.has_header,
            separator=params.separator,
        )
