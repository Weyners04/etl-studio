"""Registre type de nœud -> descripteur complet (impl + params + cardinalité).

Ajouter une capacité = enregistrer un type ici via le décorateur @register.
La validation et l'exécution interrogent toutes deux ce registre.
"""

from __future__ import annotations

from typing import Callable

from pydantic import BaseModel

from app.schema_types import NodeSchemaResolver, _passthrough_resolver
from app.nodes.base import NodeDescriptor, NodeImpl, PortCardinality

_REGISTRY: dict[str, NodeDescriptor] = {}


def register(
    node_type: str,
    *,
    params_model: type[BaseModel],
    ports: PortCardinality,
    label: str,
    description: str,
    schema_resolver: NodeSchemaResolver = _passthrough_resolver,
) -> Callable[[type], type]:
    def deco(cls: type) -> type:
        _REGISTRY[node_type] = NodeDescriptor(
            impl=cls(),  # instance unique partagée
            params_model=params_model,
            ports=ports,
            label=label,
            description=description,
            schema_resolver=schema_resolver,
        )
        return cls

    return deco


def is_registered(node_type: str) -> bool:
    return node_type in _REGISTRY


def get_node_impl(node_type: str) -> NodeImpl:
    try:
        return _REGISTRY[node_type].impl
    except KeyError as exc:
        raise KeyError(f"Aucune implémentation enregistrée pour '{node_type}'.") from exc


def get_node_descriptor(node_type: str) -> NodeDescriptor:
    try:
        return _REGISTRY[node_type]
    except KeyError as exc:
        raise KeyError(f"Aucune implémentation enregistrée pour '{node_type}'.") from exc


def registered_types() -> list[str]:
    return sorted(_REGISTRY)
