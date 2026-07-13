"""Résolution de schéma sans exécution de données.

resolve_schemas parcourt le plan en ordre topologique (produit par build_plan),
appelle le schema_resolver de chaque nœud avec les schémas de ses entrées, et
propage l'état indéterminé (None) à tous les descendants d'une source inaccessible.

Règles du moteur :
  - Sinks (ports.max_out == 0) : résultat forcé à None (pas de sortie à propager).
  - Nœud avec au moins une entrée indéterminée : résultat forcé à None (propagation).
  - Autres : appel du schema_resolver déclaré par le nœud.

Aucune donnée n'est lue — seuls les en-têtes / métadonnées des sources sont accédés,
via collect_schema() dans les resolvers des nœuds sources.
"""

from __future__ import annotations

from app.interpreter.interpret import ExecutionPlan
from app.nodes.registry import get_node_descriptor
from app.schema_types import SchemaList, SchemaResolution


def resolve_schemas(plan: ExecutionPlan) -> dict[str, SchemaResolution]:
    """Résout et propage les schémas pour chaque nœud du plan.

    Returns:
        dict node_id -> SchemaResolution. Les sinks et les nœuds dont l'entrée
        est indéterminée ont schema=None.
    """
    schema_outputs: dict[str, SchemaList] = {}
    results: dict[str, SchemaResolution] = {}

    for step in plan.steps:
        desc = get_node_descriptor(step.node.type)
        node_id = step.node.id

        # Sinks n'ont pas de sortie de schéma à propager.
        if desc.ports.max_out == 0:
            results[node_id] = SchemaResolution(schema=None)
            schema_outputs[node_id] = None
            continue

        input_schemas: list[SchemaList] = [schema_outputs[src] for src in step.inputs]

        # Propagation de l'indéterminé : si une entrée est inconnue, la sortie l'est aussi.
        if step.inputs and any(s is None for s in input_schemas):
            results[node_id] = SchemaResolution(schema=None)
            schema_outputs[node_id] = None
            continue

        parsed_params = desc.params_model.model_validate(step.node.params)
        resolution = desc.schema_resolver(parsed_params, input_schemas)
        results[node_id] = resolution
        schema_outputs[node_id] = resolution.schema

    return results
