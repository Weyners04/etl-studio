# ir-schema — contrat partagé

Source de vérité de la représentation intermédiaire (IR). Aucune logique métier ici :
uniquement le schéma et des exemples.

- `schema/ir.schema.json` — JSON Schema normatif de l'IR.
- `examples/sample-job.json` — job de référence (utilisé par les tests backend).

Le backend (`packages/backend/app/ir`) et le frontend (`packages/frontend/src/ir`) dérivent
tous deux de ce contrat. Toute évolution de l'IR commence ici.
