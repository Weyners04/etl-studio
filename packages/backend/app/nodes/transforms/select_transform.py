"""transform.select — projette un sous-ensemble de colonnes."""

from __future__ import annotations

from typing import Any

from app.nodes.registry import register


@register("transform.select")
class SelectTransform:
    def run(self, params: dict[str, Any], inputs: list[Any]) -> Any:
        (frame,) = inputs
        columns = params["columns"]
        # return frame.select(columns)
        raise NotImplementedError(f"transform.select non encore implémenté (columns={columns}).")
