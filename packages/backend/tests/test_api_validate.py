"""Tests du contrat HTTP de POST /jobs/validate.

La validation continue du frontend dépend de cette route en permanence :
couvrir le contrat complet évite qu'une régression silencieuse casse l'UI.

Cas couverts :
- succès : job valide → 200 {"status": "ok"}
- erreur nœud-spécifique : params invalides → 422, error_type + node_id attribué
- erreur globale : arête vers nœud inexistant → 422, node_id == null
  (le frontend ne colore aucun nœud dans ce cas)
"""

from __future__ import annotations

from fastapi.testclient import TestClient

import app.nodes  # noqa: F401  (enregistre les nœuds)
from app.main import api_app

client = TestClient(api_app)


def _body(**kwargs) -> dict:  # type: ignore[type-arg]
    """Graph IR minimal ; les champs passés en kwargs surchargent les défauts."""
    base: dict = {
        "version": "0.1.0",
        "id": "t",
        "name": "t",
        "nodes": [],
        "edges": [],
    }
    return {**base, **kwargs}


def test_validate_valid_job_returns_200_ok() -> None:
    """Un job structurellement valide renvoie 200 {"status": "ok"}."""
    body = _body(
        nodes=[
            {"id": "n1", "type": "source.csv", "params": {"path": "data/in.csv"}},
            {"id": "n2", "type": "sink.parquet", "params": {"path": "data/out.parquet"}},
        ],
        edges=[{"id": "e1", "source": "n1", "target": "n2"}],
    )
    response = client.post("/jobs/validate", json=body)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_validate_invalid_params_returns_structured_error_with_node_id() -> None:
    """Params invalides (path manquant) → 422 avec error_type et node_id attribué.

    C'est le contrat sur lequel le frontend s'appuie pour colorer le nœud fautif.
    """
    body = _body(
        nodes=[
            {"id": "n1", "type": "source.csv", "params": {}},  # path obligatoire absent
        ],
    )
    response = client.post("/jobs/validate", json=body)
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["error_type"] == "validation_error"
    assert "message" in detail
    assert detail["node_id"] == "n1"
    assert detail["node_type"] == "source.csv"


def test_validate_unknown_edge_target_returns_null_node_id() -> None:
    """Arête vers un nœud inexistant → 422 avec node_id == null.

    C'est le contrat sur lequel le frontend s'appuie pour ne colorer AUCUN nœud
    quand l'erreur n'est pas attribuable à un nœud précis.
    """
    body = _body(
        nodes=[
            {"id": "n1", "type": "source.csv", "params": {"path": "data/in.csv"}},
        ],
        edges=[{"id": "e1", "source": "n1", "target": "ghost"}],  # "ghost" n'existe pas
    )
    response = client.post("/jobs/validate", json=body)
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["error_type"] == "validation_error"
    assert detail["node_id"] is None
