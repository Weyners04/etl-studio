"""Étape 3b — exécution pas-à-pas en mode debug.

Matérialise la sortie de chaque nœud intermédiaire pour rapporter le nombre de
lignes et un échantillon. Le mode normal (execute) reste strictement inchangé.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

import polars as pl
import polars.exceptions as pl_exc

from app.interpreter.errors import ExecutionError, _categorize, _translate
from app.interpreter.interpret import ExecutionPlan
from app.nodes.registry import get_node_descriptor

DEBUG_SAMPLE_SIZE = 10


@dataclass
class NodeDebugResult:
    """Résultat d'exécution d'un nœud en mode debug.

    Attributes:
        node_id: identifiant du nœud.
        row_count: nombre de lignes produites ; None pour les sinks (pas de frame sortante).
        sample: premières lignes (max DEBUG_SAMPLE_SIZE), JSON-sérialisables ; vide pour les sinks.
        written: chemin du fichier écrit pour les sinks ; None sinon.
    """

    node_id: str
    row_count: int | None
    sample: list[dict[str, object]] = field(default_factory=list)
    written: str | None = None


class DebugExecutionError(Exception):
    """Levée quand execute_debug rencontre une erreur pendant l'exécution.

    Transporte la cause (ExecutionError attribuée au nœud précis, sans rejeu diagnostic
    car le pas-à-pas donne l'attribution gratuitement) et les résultats partiels des
    nœuds exécutés avant l'échec.
    """

    def __init__(self, cause: ExecutionError, partial: list[NodeDebugResult]) -> None:
        super().__init__(str(cause))
        self.cause = cause
        self.partial = partial


def execute_debug(plan: ExecutionPlan) -> list[NodeDebugResult]:
    """Exécute le plan pas-à-pas en matérialisant la sortie de chaque nœud.

    Contrairement à execute(), brise la fusion Polars à chaque étape : chaque
    LazyFrame est collecté (→ DataFrame), mesuré, échantillonné, puis reconverti
    en LazyFrame (.lazy()) pour le passer au nœud suivant. Ce faisant, chaque
    nœud devient observable sans coût quadratique (l'amont n'est pas ré-exécuté).

    Les sinks ne produisent pas de LazyFrame (ils écrivent et renvoient un dict) ;
    leur row_count est None et leur sample est vide.

    Raises:
        DebugExecutionError: si un nœud échoue, avec les résultats partiels inclus.
    """
    outputs: dict[str, Any] = {}
    results: list[NodeDebugResult] = []

    for step in plan.steps:
        desc = get_node_descriptor(step.node.type)
        parsed_params = desc.params_model.model_validate(step.node.params)
        inputs = [outputs[src] for src in step.inputs]
        node_id = step.node.id
        node_type = step.node.type

        with _node_guard(node_id, node_type, results):
            raw = desc.impl.run(params=parsed_params, inputs=inputs)

        if isinstance(raw, pl.LazyFrame):
            with _node_guard(node_id, node_type, results):
                df = raw.collect()
            results.append(
                NodeDebugResult(
                    node_id=node_id,
                    row_count=df.height,
                    sample=_safe_sample(df, DEBUG_SAMPLE_SIZE),
                )
            )
            outputs[node_id] = df.lazy()
        else:
            # Sink : renvoie {"written": path} ; row_count et sample non applicables.
            written = raw.get("written") if isinstance(raw, dict) else None
            results.append(
                NodeDebugResult(
                    node_id=node_id,
                    row_count=None,
                    sample=[],
                    written=written,
                )
            )
            outputs[node_id] = raw

    return results


@contextmanager
def _node_guard(
    node_id: str,
    node_type: str,
    partial: list[NodeDebugResult],
) -> Iterator[None]:
    """Attrape OSError/PolarsError et les relève en DebugExecutionError attribuée au nœud."""
    try:
        yield
    except (OSError, pl_exc.PolarsError) as exc:
        raise DebugExecutionError(
            ExecutionError(
                f"Nœud {node_id!r} ({node_type}) : {_translate(exc)}",
                category=_categorize(exc),
                node_id=node_id,
                node_type=node_type,
            ),
            partial=partial,
        ) from exc


def _safe_sample(df: pl.DataFrame, n: int) -> list[dict[str, object]]:
    """Extrait les n premières lignes sous forme JSON-sérialisable.

    to_dicts() produit des objets Python natifs : date et datetime ne sont pas
    JSON-sérialisables directement. On les convertit en chaîne ISO 8601.
    Les autres types Polars (int, float, str, bool, None) passent sans conversion.
    """
    rows = df.head(n).to_dicts()
    return [
        {k: v.isoformat() if isinstance(v, (date, datetime)) else v for k, v in row.items()}
        for row in rows
    ]
