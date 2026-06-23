# Spécification de l'IR

L'IR est un graphe orienté acyclique sérialisé en JSON. Le schéma normatif est
[`packages/ir-schema/schema/ir.schema.json`](../packages/ir-schema/schema/ir.schema.json).

## Forme générale

```json
{
  "version": "0.1.0",
  "id": "job_7f3c",
  "name": "Nettoyage clients",
  "nodes": [ /* ... */ ],
  "edges": [ /* ... */ ]
}
```

## Nœud

```json
{
  "id": "n1",
  "type": "source.csv",
  "params": { "path": "clients.csv", "has_header": true },
  "position": { "x": 0, "y": 0 }
}
```

- `id` — identifiant unique dans le graphe.
- `type` — type namespacé `categorie.nom` : `source.*`, `transform.*`, `sink.*`.
- `params` — paramètres propres au type (validés par le schéma du nœud côté backend).
- `position` — optionnel, purement visuel (ignoré à l'exécution).

## Arête

```json
{ "id": "e1", "source": "n1", "target": "n2", "sourcePort": "out", "targetPort": "in" }
```

- `source` / `target` — `id` des nœuds reliés.
- `sourcePort` / `targetPort` — ports nommés (défaut `out` / `in`), utiles pour les nœuds
  multi-entrées (join) ou multi-sorties (split).

## Conventions de types de nœuds

| Catégorie    | Exemples                                  | Entrées | Sorties |
|--------------|-------------------------------------------|---------|---------|
| `source.*`   | `source.csv`, `source.parquet`, `source.sql` | 0       | 1       |
| `transform.*`| `transform.filter`, `transform.select`, `transform.join`, `transform.aggregate` | 1+ | 1 |
| `sink.*`     | `sink.parquet`, `sink.csv`, `sink.table`  | 1       | 0       |

## Invariants validés

- Tous les `source`/`target` d'arêtes référencent des nœuds existants.
- Le graphe est acyclique (DAG).
- Chaque `type` est connu du registre.
- Les `params` respectent le schéma du type de nœud.
- Cardinalité des ports respectée (une source n'a pas d'entrée, etc.).

Un exemple complet exécutable : [`packages/ir-schema/examples/sample-job.json`](../packages/ir-schema/examples/sample-job.json).
