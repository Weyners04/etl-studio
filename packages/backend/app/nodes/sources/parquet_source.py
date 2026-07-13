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
from app.schema_types import ColumnSchema, SchemaList, SchemaResolution


class ParquetSourceParams(BaseModel):
    path: str


def _resolve_parquet_schema(
    params: ParquetSourceParams, input_schemas: list[SchemaList]
) -> SchemaResolution:
    try:
        schema = pl.scan_parquet(params.path).collect_schema()
        return SchemaResolution(
            schema=[ColumnSchema(name=n, dtype=str(d)) for n, d in schema.items()]
        )
    except Exception:
        return SchemaResolution(schema=None)


@register(
    "source.parquet",
    params_model=ParquetSourceParams,
    ports=PortCardinality(min_in=0, max_in=0, min_out=0, max_out=None),
    label="ParquetReader",
    description="Lit un fichier Parquet et charge ses lignes dans le pipeline.",
    schema_resolver=_resolve_parquet_schema,
)
class ParquetSource:
    def run(self, params: ParquetSourceParams, inputs: list[Any]) -> pl.LazyFrame:
        return pl.scan_parquet(params.path)
