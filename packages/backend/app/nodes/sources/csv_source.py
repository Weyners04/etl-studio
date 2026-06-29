"""source.csv — lit un CSV en LazyFrame Polars.

TODO (Phase 1) : brancher réellement sur Polars une fois les chemins/IO arrêtés.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from app.nodes.base import PortCardinality
from app.nodes.registry import register


class CsvSourceParams(BaseModel):
    path: str
    has_header: bool = True


@register(
    "source.csv",
    params_model=CsvSourceParams,
    ports=PortCardinality(min_in=0, max_in=0, min_out=0, max_out=None),
)
class CsvSource:
    def run(self, params: dict[str, Any], inputs: list[Any]) -> Any:
        path = params["path"]
        # import polars as pl
        # return pl.scan_csv(path, has_header=params.get("has_header", True))
        raise NotImplementedError(f"source.csv non encore implémenté (path={path}).")
