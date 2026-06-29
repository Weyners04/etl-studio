"""sink.parquet — matérialise le frame en Parquet."""

from __future__ import annotations

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
    def run(self, params: dict[str, Any], inputs: list[Any]) -> Any:
        (frame,) = inputs
        path = params["path"]
        # frame.collect().write_parquet(path)
        # return {"written": path}
        raise NotImplementedError(f"sink.parquet non encore implémenté (path={path}).")
