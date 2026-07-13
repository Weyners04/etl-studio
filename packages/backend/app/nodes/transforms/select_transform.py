"""transform.select — projette un sous-ensemble de colonnes."""

from __future__ import annotations

from typing import Any

import polars as pl
from pydantic import BaseModel

from app.nodes.base import PortCardinality
from app.nodes.registry import register
from app.schema_types import SchemaList, SchemaResolution


class SelectTransformParams(BaseModel):
    columns: list[str]


def _resolve_select_schema(
    params: SelectTransformParams, input_schemas: list[SchemaList]
) -> SchemaResolution:
    if not input_schemas or input_schemas[0] is None:
        return SchemaResolution(schema=None)
    by_name = {col.name: col for col in input_schemas[0]}
    missing = [c for c in params.columns if c not in by_name]
    output = [by_name[c] for c in params.columns if c in by_name]
    warnings = [f"Colonne '{c}' absente du schéma d'entrée" for c in missing]
    return SchemaResolution(schema=output, warnings=warnings)


@register(
    "transform.select",
    params_model=SelectTransformParams,
    ports=PortCardinality(min_in=1, max_in=None, min_out=0, max_out=None),
    label="ColumnFilter",
    description="Ne conserve que les colonnes sélectionnées, dans l'ordre choisi.",
    schema_resolver=_resolve_select_schema,
)
class SelectTransform:
    def run(self, params: SelectTransformParams, inputs: list[Any]) -> pl.LazyFrame:
        lf: pl.LazyFrame = inputs[0]
        return lf.select(params.columns)
