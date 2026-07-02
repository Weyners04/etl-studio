"""Point d'entrée FastAPI."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.nodes  # noqa: F401  (effet de bord : enregistre les nœuds)
from app.api import router

api_app = FastAPI(title="ETL Studio", version="0.1.0")

api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # éditeur en dev (Vite)
    allow_methods=["*"],
    allow_headers=["*"],
)

api_app.include_router(router)


@api_app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
