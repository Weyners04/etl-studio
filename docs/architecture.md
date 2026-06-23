# Architecture

## Vue d'ensemble

Le système découple **l'autorat** (comment un job est créé) de **l'exécution** (comment il est
lancé) au moyen d'un contrat unique : la représentation intermédiaire (IR) en JSON.

```
Autorat (producteurs d'IR)            Exécution (consommateur d'IR)
┌────────────────┐                    ┌──────────────────────────────┐
│ Éditeur visuel │──┐              ┌──│ validate → interpret → execute│
│ Couche IA      │──┴──► IR JSON ──┴──│ nœuds Polars / DuckDB         │
└────────────────┘                    └──────────────────────────────┘
```

Conséquence : ajouter un nouveau mode d'autorat (import depuis un autre outil, API, etc.)
ne touche jamais l'exécution, tant qu'il produit une IR valide. Inversement, optimiser
l'exécution n'impacte jamais l'édition.

## Les trois décisions structurantes

### 1. L'IR comme contrat universel
Tout job est un graphe `{ nodes, edges }` sérialisé en JSON. C'est la seule chose que les
producteurs émettent et que l'exécution consomme. Le schéma fait foi (`packages/ir-schema`).

### 2. Interprétation directe, pas de génération de code
Le backend **interprète** l'IR (parcours du graphe + appels aux implémentations de nœuds)
plutôt que de générer puis exécuter du code. La génération de code (vers un script Polars
lisible, par ex.) est offerte comme **preview / transparence**, jamais comme chemin d'exécution.

### 3. IA contrainte au structured output
Le LLM ne renvoie jamais de code. Il est forcé, via function calling / structured output,
à émettre une IR conforme au schéma. Le même schéma sert donc à la fois :
- de validation de l'IR entrante,
- de contrainte de sortie pour le LLM.

## Pipeline d'exécution

```
IR JSON
  │
  ├─ validate    structure + schéma + graphe acyclique + types de nœuds connus + params valides
  │
  ├─ interpret   tri topologique → plan d'exécution ordonné
  │
  └─ execute     parcours du plan ; chaque nœud reçoit ses frames d'entrée, produit sa sortie
                 (sources → transforms → sinks), en s'appuyant sur Polars / DuckDB
```

## Registre de nœuds

Chaque type de nœud (`source.csv`, `transform.filter`, `sink.parquet`, ...) est enregistré
avec : son schéma de paramètres, ses ports d'entrée/sortie, et son implémentation `run()`.
Ajouter une capacité = ajouter une entrée au registre, côté backend, et son rendu côté éditeur.

## Frontières des packages

| Package      | Responsabilité                                   | Ne fait pas              |
|--------------|--------------------------------------------------|--------------------------|
| `ir-schema`  | Définit l'IR (source de vérité partagée)         | Aucune logique métier    |
| `frontend`   | Édite/visualise l'IR, appelle l'API              | N'exécute pas de pipeline|
| `backend`    | Valide, interprète, exécute ; héberge la couche IA | Ne définit pas l'UX      |
