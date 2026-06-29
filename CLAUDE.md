# CLAUDE.md — ETL Studio

Instructions de projet lues par Claude Code au début de chaque session.
Garder ce fichier **court, à jour et à fort signal** : il n'est pas une doc, il est un guide.

## Le projet en une phrase

Outil ETL combinant un éditeur de flux visuel (React Flow) et une génération de pipelines
par IA, où une **représentation intermédiaire (IR) JSON** sert de contrat unique entre
l'autorat (édition) et l'exécution.

## Principes d'architecture — NON NÉGOCIABLES

Ces décisions sont structurantes. Tout changement qui les contredit doit être **refusé ou
signalé à Colin avant d'agir**, jamais contourné en silence.

1. **L'IR JSON est le contrat universel.** Tout job est un graphe `{nodes, edges}`.
   L'éditeur visuel et la couche IA sont deux *producteurs* d'IR ; l'exécution est agnostique
   à la source. Aucune fonctionnalité ne doit créer un chemin qui contourne l'IR.
2. **Interprétation directe, pas de génération de code à l'exécution.** Le backend interprète
   l'IR (parcours du graphe + implémentations de nœuds). La génération de code est réservée à
   une preview de transparence (V3), jamais au runtime.
3. **IA contrainte au structured output.** Le LLM émet de l'IR conforme au schéma via function
   calling / structured output — jamais du code libre. Les modèles Pydantic servent à la fois
   de validation et de schéma de contrainte (double usage).
4. **Compiler vers l'existant.** L'exécution s'appuie sur Polars / DuckDB, pas sur un moteur maison.

Détails : `docs/architecture.md`, `docs/ir-spec.md`.
Source de vérité de l'IR : `packages/ir-schema/schema/ir.schema.json`.

## Structure du dépôt

- `packages/ir-schema/` — contrat partagé (JSON Schema + exemples). **Toute évolution de l'IR
  commence ici.**
- `packages/backend/` — Python · FastAPI : `app/ir` (modèles Pydantic), `app/interpreter`
  (validate → interpret → execute), `app/nodes` (registre + Polars/DuckDB), `app/ai`
  (génération contrainte), `app/api` (routes FastAPI).
- `packages/frontend/` — TypeScript · React · React Flow : `src/ir` (types + sérialisation),
  `src/editor` (canvas), `src/api` (client backend).

## Commandes

Backend — depuis `packages/backend`, environnement géré par **uv** :
- Installer : `uv pip install -e ".[dev]"`
- Tests : `uv run pytest -q`
- Lint : `uv run ruff check .`  ·  Format : `uv run ruff format .`
- Typage : `uv run mypy app`
- Serveur : `uv run uvicorn app.main:app --reload`

Frontend — depuis `packages/frontend` :
- Installer : `npm install`  ·  Dev : `npm run dev`  ·  Lint/typage : `npm run lint`

## Conventions de développement

- Avant tout ajout, **lire le code existant concerné** pour rester cohérent et **ne pas
  dupliquer** logique ou fichiers.
- Code **typé** (Python : annotations + mypy ; TS : mode strict), **testé**, et passant
  **ruff / eslint** avant commit.
- Commits **petits et atomiques**, format Conventional Commits (`feat:`, `fix:`, `docs:`,
  `refactor:`, `test:`, `chore:`). Voir `CONTRIBUTING.md`.
- Toute évolution de l'IR se répercute dans **les trois représentations** : JSON Schema →
  modèles Pydantic → types TS, **plus** l'exemple de référence et les tests.
- Ne pas ajouter de dépendance sans la **justifier explicitement**.

## Façon de travailler avec Colin

- **Expliquer chaque ajout en détail** (le quoi et le pourquoi) : Colin veut *comprendre* le
  code, pas seulement le recevoir.
- **Valider l'approche avant d'implémenter** dès qu'un choix d'architecture est en jeu
  (privilégier le mode Plan).
- Avancer **phase par phase** selon `docs/roadmap.md`. Phase courante : **Phase 0 — Foundation**.

## À ne jamais faire

- Introduire un chemin d'exécution qui contourne l'IR.
- Générer du code libre depuis le LLM (toujours structured output contraint au schéma).
- Lancer `npm audit fix --force` ou toute correction destructive automatique sans revue.
- Committer du code non formaté ou qui casse les tests.
