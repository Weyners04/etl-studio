"""Étape 3 — exécution du plan.

Parcourt les étapes dans l'ordre ; chaque nœud reçoit les frames de ses entrées et produit
sa sortie. Les implémentations s'appuient sur Polars / DuckDB (voir app/nodes).
"""
from __future__ import annotations

from typing import Any

from app.interpreter.interpret import ExecutionPlan
from app.nodes.registry import get_node_impl


def execute(plan: ExecutionPlan) -> dict[str, Any]:
    """Exécute le plan et renvoie les sorties par id de nœud.

    Les sources renvoient un frame, les transforms le transforment, les sinks l'écrivent
    (et renvoient typiquement None / un récapitulatif).
    """
    outputs: dict[str, Any] = {}

    for step in plan.steps:
        impl = get_node_impl(step.node.type)
        inputs = [outputs[src] for src in step.inputs]
        outputs[step.node.id] = impl.run(params=step.node.params, inputs=inputs)

    return outputs
