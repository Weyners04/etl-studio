"""Étape 3 — exécution du plan.

Parcourt les étapes dans l'ordre ; chaque nœud reçoit les frames de ses entrées et produit
sa sortie. Les implémentations s'appuient sur Polars / DuckDB (voir app/nodes).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import polars as pl
import polars.exceptions as pl_exc

from app.interpreter.errors import ExecutionError, _categorize, _translate
from app.interpreter.interpret import ExecutionPlan
from app.nodes.registry import get_node_descriptor


def execute(plan: ExecutionPlan) -> dict[str, Any]:
    """Exécute le plan et renvoie les sorties par id de nœud.

    Les sources renvoient un LazyFrame, les transforms l'enrichissent, les sinks
    déclenchent la matérialisation (collect) et renvoient un récapitulatif.
    """
    outputs: dict[str, Any] = {}

    try:
        for step in plan.steps:
            desc = get_node_descriptor(step.node.type)
            parsed_params = desc.params_model.model_validate(step.node.params)
            inputs = [outputs[src] for src in step.inputs]
            outputs[step.node.id] = desc.impl.run(params=parsed_params, inputs=inputs)
    except (OSError, pl_exc.PolarsError) as exc:
        raise _diagnose(plan, exc) from exc

    return outputs


def _diagnose(plan: ExecutionPlan, original_exc: BaseException) -> ExecutionError:
    """Re-joue le plan pas à pas pour identifier le nœud culpable.

    Chaque nœud — source, transform et sink — est sondé indépendamment.
    Le premier dont la sonde lève est retourné comme culpable.
    """
    diag_outputs: dict[str, Any] = {}

    for step in plan.steps:
        desc = get_node_descriptor(step.node.type)
        parsed = desc.params_model.model_validate(step.node.params)
        inputs = [diag_outputs[src] for src in step.inputs]
        is_sink = step.node.type.startswith("sink.")

        try:
            if is_sink:
                # Sonde sink :
                # (1) résoudre le schéma de l'entrée sans lire la donnée,
                # (2) vérifier l'accès au chemin d'écriture sans matérialiser.
                for inp in inputs:
                    if isinstance(inp, pl.LazyFrame):
                        inp.collect_schema()
                write_path = getattr(parsed, "path", None)
                if write_path is not None:
                    Path(write_path).parent.mkdir(parents=True, exist_ok=True)
                diag_outputs[step.node.id] = None
            else:
                # Sonde non-sink : exécuter puis résoudre le schéma du résultat.
                result = desc.impl.run(params=parsed, inputs=inputs)
                if isinstance(result, pl.LazyFrame):
                    result.collect_schema()
                diag_outputs[step.node.id] = result
        except Exception as probe_exc:
            node_id = step.node.id
            node_type = step.node.type
            return ExecutionError(
                f"Nœud {node_id!r} ({node_type}) : {_translate(probe_exc)}",
                category=_categorize(probe_exc),
                node_id=node_id,
                node_type=node_type,
            )

    # Aucune sonde n'a pu isoler le coupable.
    return ExecutionError(
        f"Erreur à l'exécution, non isolable à un nœud unique : {_translate(original_exc)}",
        category=_categorize(original_exc),
    )
