"""source.parquet — construit un plan de lecture Parquet (LazyFrame Polars).

Le Parquet est auto-descriptif (schéma embarqué) : aucun paramètre
has_header ni separator n'est nécessaire.
L'exécution effective est déclenchée par le sink en aval (lazy evaluation).
"""

from __future__ import annotations

from typing import Any

import polars as pl
from pydantic import BaseModel

from app.nodes.base import PortCardinality
from app.nodes.registry import register


class ParquetSourceParams(BaseModel):
    path: str


@register(
    "source.parquet",
    params_model=ParquetSourceParams,
    ports=PortCardinality(min_in=0, max_in=0, min_out=0, max_out=None),
    label="ParquetReader",
    description="Lit un fichier Parquet et charge ses lignes dans le pipeline.",
)
class ParquetSource:
    def run(self, params: ParquetSourceParams, inputs: list[Any]) -> pl.LazyFrame:
        return pl.scan_parquet(params.path)
