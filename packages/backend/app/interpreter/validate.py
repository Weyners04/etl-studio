"""Étape 1 — validation de l'IR.

Vérifie, au-delà du parsing Pydantic :
  - les arêtes référencent des nœuds existants ;
  - le graphe est acyclique (DAG) ;
  - chaque type de nœud est connu du registre ;
  - les params respectent le schéma du type de nœud ;
  - la cardinalité des ports est respectée.
"""

from __future__ import annotations

from collections import Counter

from pydantic import ValidationError as PydanticValidationError

from app.ir import IRGraph
from app.nodes.registry import get_node_descriptor, is_registered


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

    in_deg: Counter[str] = Counter(e.target for e in graph.edges)
    out_deg: Counter[str] = Counter(e.source for e in graph.edges)

    for node in graph.nodes:
        desc = get_node_descriptor(node.type)

        try:
            desc.params_model.model_validate(node.params)
        except PydanticValidationError as exc:
            details = "; ".join(
                f"'{'.'.join(str(loc) for loc in e['loc'])}' : {e['msg']}" for e in exc.errors()
            )
            raise ValidationError(
                f"Nœud {node.id!r} ({node.type}) : params invalides — {details}."
            ) from exc

        p = desc.ports
        n_in = in_deg[node.id]
        n_out = out_deg[node.id]

        if n_in < p.min_in or (p.max_in is not None and n_in > p.max_in):
            expected = f"min {p.min_in}" if p.max_in is None else f"{p.min_in}..{p.max_in}"
            raise ValidationError(
                f"Nœud {node.id!r} ({node.type}) : {n_in} arête(s) entrante(s), attendu {expected}."
            )

        if n_out < p.min_out or (p.max_out is not None and n_out > p.max_out):
            expected = f"min {p.min_out}" if p.max_out is None else f"{p.min_out}..{p.max_out}"
            raise ValidationError(
                f"Nœud {node.id!r} ({node.type}) : {n_out} arête(s) sortante(s),"
                f" attendu {expected}."
            )


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
