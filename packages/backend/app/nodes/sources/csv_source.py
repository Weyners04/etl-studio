"""source.csv — lit un CSV en LazyFrame Polars.

TODO (Phase 1) : brancher réellement sur Polars une fois les chemins/IO arrêtés.
"""

from __future__ import annotations

from typing import Any

from app.nodes.registry import register


@register("source.csv")
class CsvSource:
    def run(self, params: dict[str, Any], inputs: list[Any]) -> Any:
        path = params["path"]
        # import polars as pl
        # return pl.scan_csv(path, has_header=params.get("has_header", True))
        raise NotImplementedError(f"source.csv non encore implémenté (path={path}).")
