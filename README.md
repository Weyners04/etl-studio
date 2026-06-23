# ETL Studio

Outil ETL combinant un **éditeur de flux visuel** et une **génération de pipelines par IA**.
Un seul prompt en langage naturel produit un graphe de job complet — l'éditeur visuel et l'IA
sont deux producteurs d'un même contrat de données : la **représentation intermédiaire (IR) JSON**.

```
        ┌─────────────────┐        ┌─────────────────┐
        │  Éditeur visuel │        │   Couche IA     │
        │  (React Flow)   │        │ (structured out)│
        └────────┬────────┘        └────────┬────────┘
                 │      producteurs d'IR     │
                 └──────────────┬────────────┘
                                ▼
                   ┌────────────────────────┐
                   │   IR  (graphe JSON)     │  ← contrat universel
                   │   nodes + edges         │
                   └────────────┬────────────┘
                                ▼
              validate ──► interpret ──► execute
                                ▼
                      Polars / DuckDB
```

## Principes d'architecture

1. **L'IR est le contrat universel.** Chaque job est un graphe JSON de nœuds et d'arêtes.
   L'éditeur visuel comme l'IA produisent cette même IR ; l'exécution est agnostique à la source.
2. **Interprétation directe de l'IR**, pas de génération de code. La génération de code reste une
   fonctionnalité de transparence / preview uniquement.
3. **IA contrainte.** Le LLM émet de l'IR via structured output / function calling — jamais du code libre.
   Fiabilité avant flexibilité.
4. **Compiler vers l'existant.** L'exécution s'appuie sur Polars et DuckDB plutôt que de réinventer la logique ETL.

## Structure du dépôt

```
packages/
  ir-schema/     Contrat partagé : JSON Schema de l'IR + exemples (source de vérité)
  frontend/      TypeScript · React · React Flow — éditeur visuel + producteur d'IR
  backend/       Python · FastAPI — validate → interpret → execute, nœuds Polars/DuckDB, couche IA
docs/            Architecture, spécification de l'IR, roadmap par phases
```

## Démarrage rapide

### Backend
```bash
cd packages/backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

### Frontend
```bash
cd packages/frontend
npm install
npm run dev
```

## Roadmap

Voir [`docs/roadmap.md`](docs/roadmap.md) — Foundation → V1 → V2 → V3.

## Licence

MIT — voir [LICENSE](LICENSE).
