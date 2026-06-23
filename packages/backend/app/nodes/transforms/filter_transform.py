"""transform.filter — garde les lignes satisfaisant une expression.

TODO (Phase 1) : parser params['expr'] vers une expression Polars sûre (pas d'eval libre).
"""
from __future__ import annotations

from typing import Any

from app.nodes.registry import register


@register("transform.filter")
class FilterTransform:
    def run(self, params: dict[str, Any], inputs: list[Any]) -> Any:
        (frame,) = inputs
        expr = params["expr"]
        # return frame.filter(parse_expr(expr))
        raise NotImplementedError(f"transform.filter non encore implémenté (expr={expr}).")
