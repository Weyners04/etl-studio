"""Types partagés pour la résolution de schéma.

Module autonome (aucun import app.*) placé à la racine du package app pour
éviter tout cycle d'import entre app.nodes et app.interpreter.

ColumnSchema      : une colonne (nom + dtype Polars en texte).
SchemaList        : schéma connu (liste de colonnes) ou indéterminé (None).
SchemaResolution  : résultat du resolver d'un nœud — schéma + avertissements.
NodeSchemaResolver: signature du callable que chaque nœud peut déclarer.
_passthrough_resolver : comportement par défaut — transmet l'entrée inchangée.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(frozen=True)
class ColumnSchema:
    """Une colonne avec son type Polars sérialisé en texte (ex. 'Int64', 'String')."""

    name: str
    dtype: str


@dataclass
class SchemaResolution:
    """Résultat de la résolution de schéma d'un nœud.

    schema   : colonnes produites par ce nœud ; None = schéma indéterminé
                (source inaccessible ou entrée indéterminée propagée).
    warnings : incohérences non bloquantes (ex. colonne demandée mais absente).
    """

    schema: list[ColumnSchema] | None
    warnings: list[str] = field(default_factory=list)


# Alias de commodité pour les signatures.
SchemaList = list[ColumnSchema] | None
NodeSchemaResolver = Callable[[Any, list[SchemaList]], SchemaResolution]


def _passthrough_resolver(params: Any, input_schemas: list[SchemaList]) -> SchemaResolution:
    """Resolver par défaut : transmet le schéma de la première entrée sans modification.

    Retourne indéterminé si le nœud n'a aucune entrée (cas des sources sans resolver
    explicite) ou si la première entrée est elle-même indéterminée.
    """
    if not input_schemas:
        return SchemaResolution(schema=None)
    return SchemaResolution(schema=input_schemas[0])
