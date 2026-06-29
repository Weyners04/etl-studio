"""sink.parquet — matérialise le plan lazy et écrit le résultat en Parquet.

collect() déclenche l'exécution de tout le plan lazy en amont, puis
write_parquet() sérialise le DataFrame résultant. Fiable et sans contrainte
sur les opérations du plan (vs sink_parquet streaming, réservé à Phase 3).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel

from app.nodes.base import PortCardinality
from app.nodes.registry import register


class ParquetSinkParams(BaseModel):
    path: str


@register(
    "sink.parquet",
    params_model=ParquetSinkParams,
    ports=PortCardinality(min_in=1, max_in=None, min_out=0, max_out=0),
)
class ParquetSink:
    def run(self, params: ParquetSinkParams, inputs: list[Any]) -> dict[str, Any]:
        (lf,) = inputs
        Path(params.path).parent.mkdir(parents=True, exist_ok=True)
        lf.collect().write_parquet(params.path)
        return {"written": params.path}
