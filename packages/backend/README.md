# backend

`validate → interpret → execute`, registre de nœuds (Polars/DuckDB), couche IA (structured output).

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:api_app --reload
pytest -q
```

Arborescence : `app/ir` (modèles IR) · `app/interpreter` (validate/interpret/execute) ·
`app/nodes` (registre + implémentations) · `app/ai` (génération contrainte) · `app/api` (FastAPI).
