# Roadmap

Progression par phases, avec checkpoints de validation explicites. Coche au fur et à mesure.

## Phase 0 — Foundation  *(socle : le contrat existe et tient debout)*
- [x] Définir l'IR (nodes/edges) et son JSON Schema — `packages/ir-schema`
- [x] Exemple d'IR exécutable de référence
- [x] Modèles IR côté backend (Pydantic) = validation + base du structured output
- [x] Types IR côté frontend (TypeScript)
- [x] Validation structurelle complète : params via modèles Pydantic du registre, cardinalité des ports, DAG, références d'arêtes.
- [ ] Squelette FastAPI (`/jobs/validate`, `/jobs/run`)
- [ ] Tests sur l'exemple de référence (round-trip parse/valide)
- [x] CI : ruff lint, ruff format, pytest, mypy — 15 tests.

## Phase 1 — V1  *(éditeur visuel + autorat manuel de l'IR)*
- [ ] Canvas React Flow : ajout/suppression/déplacement de nœuds et arêtes
- [ ] Panneau de paramètres par type de nœud (formulaires pilotés par le schéma)
- [ ] Sérialisation canvas → IR et IR → canvas (le contrat dans les deux sens)
- [x] Registre de nœuds backend : sources/transforms/sinks de base
- [x] Interpréteur : tri topologique → plan d'exécution
- [x] Exécution : sources (scan_csv), transforms (filter structuré column/operator/value, select), sink (collect + write_parquet) — pas de texte libre.
- [x] Gestion des erreurs d'exécution : ExecutionError (catégorie RESOURCE/DATA, attribution au nœud précis via rejeu diagnostic — sonde collect_schema par nœud, sonde d'écriture pour les sinks).
  - *Limite connue :* la sonde sink appelle `mkdir` réellement (léger effet de bord) ; à reconcevoir pour les sinks distants (bases, cloud) où « sonder l'écriture » devient une vraie question.
- [ ] Bouton « Run » de bout en bout sur un job construit à la main
- [ ] **Checkpoint :** un job non trivial s'édite visuellement puis s'exécute

## Phase 2 — V2  *(génération IA)*
- [ ] Couche IA : prompt → IR via structured output / function calling
- [ ] Validation systématique de l'IR générée avant tout rendu/exécution
- [ ] Endpoint `/ai/generate` + intégration dans l'UI (prompt → graphe affiché)
- [ ] Boucle de réparation : si l'IR générée est invalide, renvoyer l'erreur au LLM
  - *Décision reportée :* passer `validate()` d'un mode fail-fast (arrêt à la première erreur)
    à un mode collecte de toutes les erreurs, pour alimenter cette boucle en renvoyant tous
    les problèmes d'un coup au LLM.
- [ ] **Checkpoint :** un prompt produit un job valide, éditable ensuite à la main

## Phase 3 — V3  *(fonctionnalités avancées)*
- [ ] Génération de code (preview Polars lisible) — transparence, pas exécution
- [ ] Nœuds avancés (join multi-clés, fenêtres, pivots, SQL DuckDB libre)
- [ ] Aperçu de données par nœud (échantillon en sortie de chaque étape)
- [ ] Versioning / diff de jobs
- [ ] Édition assistée par IA d'un job existant (patch d'IR plutôt que régénération)

---

### Principe transverse
À chaque phase, valider le *pourquoi* avant le *comment*, et garder l'IA contrainte au
structured output. Aucune étape ne doit introduire un chemin d'exécution qui contourne l'IR.
