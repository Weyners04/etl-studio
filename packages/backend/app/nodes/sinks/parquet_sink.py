"""sink.parquet — matérialise le frame en Parquet."""

from __future__ import annotations

from typing import Any

from app.nodes.registry import register


@register("sink.parquet")
class ParquetSink:
    def run(self, params: dict[str, Any], inputs: list[Any]) -> Any:
        (frame,) = inputs
        path = params["path"]
        # frame.collect().write_parquet(path)
        # return {"written": path}
        raise NotImplementedError(f"sink.parquet non encore implémenté (path={path}).")
