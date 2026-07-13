"""sink.csv — matérialise le plan lazy et écrit le résultat en CSV.

collect() déclenche l'exécution de tout le plan lazy en amont, puis
write_csv() sérialise le DataFrame résultant.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import polars as pl
from pydantic import BaseModel

from app.nodes.base import PortCardinality
from app.nodes.registry import register


class CsvSinkParams(BaseModel):
    path: str
    separator: Literal[",", ";"] = ","


@register(
    "sink.csv",
    params_model=CsvSinkParams,
    ports=PortCardinality(min_in=1, max_in=None, min_out=0, max_out=0),
    label="CSVWriter",
    description="Écrit les données dans un fichier CSV.",
)
class CsvSink:
    def run(self, params: CsvSinkParams, inputs: list[Any]) -> dict[str, Any]:
        lf: pl.LazyFrame = inputs[0]
        Path(params.path).parent.mkdir(parents=True, exist_ok=True)
        lf.collect().write_csv(params.path, separator=params.separator)
        return {"written": params.path}
