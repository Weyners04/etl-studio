"""Registre type de nœud -> implémentation.

Ajouter une capacité = enregistrer un type ici (généralement via le décorateur @register).
La validation et l'exécution interrogent toutes deux ce registre.
"""

from __future__ import annotations

from typing import Callable

from app.nodes.base import NodeImpl

_REGISTRY: dict[str, NodeImpl] = {}


def register(node_type: str) -> Callable[[type], type]:
    def deco(cls: type) -> type:
        _REGISTRY[node_type] = cls()  # instance unique partagée
        return cls

    return deco


def is_registered(node_type: str) -> bool:
    return node_type in _REGISTRY


def get_node_impl(node_type: str) -> NodeImpl:
    try:
        return _REGISTRY[node_type]
    except KeyError as exc:
        raise KeyError(f"Aucune implémentation enregistrée pour '{node_type}'.") from exc


def registered_types() -> list[str]:
    return sorted(_REGISTRY)
