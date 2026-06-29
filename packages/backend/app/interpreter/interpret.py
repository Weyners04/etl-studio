"""Étape 2 — interprétation : IR validée -> plan d'exécution ordonné.

Produit un tri topologique des nœuds. Aucune génération de code : on construit l'ordre
dans lequel les implémentations de nœuds seront appelées.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from app.ir import IRGraph, Node


@dataclass
class PlanStep:
    node: Node
    inputs: list[str] = field(default_factory=list)  # ids des nœuds amont


@dataclass
class ExecutionPlan:
    steps: list[PlanStep]


def build_plan(graph: IRGraph) -> ExecutionPlan:
    indeg: dict[str, int] = {n.id: 0 for n in graph.nodes}
    upstream: dict[str, list[str]] = {n.id: [] for n in graph.nodes}
    adj: dict[str, list[str]] = {n.id: [] for n in graph.nodes}

    for e in graph.edges:
        indeg[e.target] += 1
        upstream[e.target].append(e.source)
        adj[e.source].append(e.target)

    queue = deque(nid for nid, d in indeg.items() if d == 0)
    order: list[str] = []
    while queue:
        nid = queue.popleft()
        order.append(nid)
        for nxt in adj[nid]:
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                queue.append(nxt)

    by_id = {n.id: n for n in graph.nodes}
    steps = [PlanStep(node=by_id[nid], inputs=upstream[nid]) for nid in order]
    return ExecutionPlan(steps=steps)
