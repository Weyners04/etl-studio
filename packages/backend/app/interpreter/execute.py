"""Étape 3 — exécution du plan.

Parcourt les étapes dans l'ordre ; chaque nœud reçoit les frames de ses entrées et produit
sa sortie. Les implémentations s'appuient sur Polars / DuckDB (voir app/nodes).
"""

from __future__ import annotations

from typing import Any

from app.interpreter.interpret import ExecutionPlan
from app.nodes.registry import get_node_descriptor


def execute(plan: ExecutionPlan) -> dict[str, Any]:
    """Exécute le plan et renvoie les sorties par id de nœud.

    Les sources renvoient un LazyFrame, les transforms l'enrichissent, les sinks
    déclenchent la matérialisation (collect) et renvoient un récapitulatif.
    """
    outputs: dict[str, Any] = {}

    for step in plan.steps:
        desc = get_node_descriptor(step.node.type)
        parsed_params = desc.params_model.model_validate(step.node.params)
        inputs = [outputs[src] for src in step.inputs]
        outputs[step.node.id] = desc.impl.run(params=parsed_params, inputs=inputs)

    return outputs
