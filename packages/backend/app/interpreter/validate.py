"""Étape 1 — validation de l'IR.

Vérifie, au-delà du parsing Pydantic :
  - les arêtes référencent des nœuds existants ;
  - le graphe est acyclique (DAG) ;
  - chaque type de nœud est connu du registre ;
  - (TODO) les params respectent le schéma du type de nœud ;
  - (TODO) la cardinalité des ports est respectée.
"""
from __future__ import annotations

from app.ir import IRGraph
from app.nodes.registry import is_registered


class ValidationError(Exception):
    """Levée quand l'IR est structurellement invalide."""


def validate(graph: IRGraph) -> None:
    ids = {n.id for n in graph.nodes}

    for edge in graph.edges:
        if edge.source not in ids:
            raise ValidationError(f"Arête {edge.id} : source inconnue '{edge.source}'.")
        if edge.target not in ids:
            raise ValidationError(f"Arête {edge.id} : cible inconnue '{edge.target}'.")

    for node in graph.nodes:
        if not is_registered(node.type):
            raise ValidationError(f"Nœud {node.id} : type inconnu '{node.type}'.")

    _assert_acyclic(graph)
    # TODO (Phase 0) : valider node.params contre le schéma du type via le registre.
    # TODO (Phase 1) : valider la cardinalité des ports (source = 0 entrée, sink = 0 sortie...).


def _assert_acyclic(graph: IRGraph) -> None:
    adj: dict[str, list[str]] = {n.id: [] for n in graph.nodes}
    for e in graph.edges:
        adj[e.source].append(e.target)

    WHITE, GRAY, BLACK = 0, 1, 2
    color = {nid: WHITE for nid in adj}

    def visit(nid: str) -> None:
        color[nid] = GRAY
        for nxt in adj[nid]:
            if color[nxt] == GRAY:
                raise ValidationError("Cycle détecté dans le graphe : l'IR doit être un DAG.")
            if color[nxt] == WHITE:
                visit(nxt)
        color[nid] = BLACK

    for nid in adj:
        if color[nid] == WHITE:
            visit(nid)
