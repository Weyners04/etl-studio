"""Tests de la route POST /jobs/run : réponse succès enrichie et erreurs structurées."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

import app.nodes  # noqa: F401  (enregistre les nœuds)
from app.main import api_app

client = TestClient(api_app)


def _job_body(csv_path: str, out_path: str) -> dict:
    return {
        "version": "0.1.0",
        "id": "test_run",
        "name": "Test run",
        "nodes": [
            {"id": "n1", "type": "source.csv", "params": {"path": csv_path}},
            {"id": "n2", "type": "sink.parquet", "params": {"path": out_path}},
        ],
        "edges": [{"id": "e1", "source": "n1", "target": "n2"}],
    }


def test_run_success_returns_status_ok(tmp_path: Path) -> None:
    """La réponse succès contient status == 'ok' et une liste outputs."""
    csv = tmp_path / "in.csv"
    csv.write_text("id,name\n1,Alice\n")
    out = tmp_path / "out.parquet"

    response = client.post("/jobs/run", json=_job_body(str(csv), str(out)))
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert isinstance(data["outputs"], list)


def test_run_success_exposes_sink_outputs(tmp_path: Path) -> None:
    """La réponse succès liste les fichiers écrits par les sinks (node_id + written)."""
    csv = tmp_path / "in.csv"
    csv.write_text("id,name\n1,Alice\n")
    out = tmp_path / "out.parquet"

    response = client.post("/jobs/run", json=_job_body(str(csv), str(out)))
    assert response.status_code == 200

    outputs = response.json()["outputs"]
    assert len(outputs) == 1
    assert outputs[0]["node_id"] == "n2"
    assert outputs[0]["written"] == str(out)


def test_run_validation_error_is_structured(tmp_path: Path) -> None:
    """Un graphe invalide (paramètre manquant) retourne une erreur 422 structurée."""
    body = {
        "version": "0.1.0",
        "id": "t",
        "name": "t",
        "nodes": [
            {"id": "n1", "type": "source.csv", "params": {}},  # path manquant
        ],
        "edges": [],
    }
    response = client.post("/jobs/run", json=body)
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["error_type"] == "validation_error"
    assert "message" in detail
    assert "node_id" in detail
    assert "node_type" in detail


def test_run_execution_error_is_structured(tmp_path: Path) -> None:
    """Un CSV manquant déclenche une ExecutionError structurée (422, pas 500)."""
    missing = str(tmp_path / "missing.csv")
    out = str(tmp_path / "out.parquet")

    response = client.post("/jobs/run", json=_job_body(missing, out))
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["error_type"] == "execution_error"
    assert "message" in detail
    assert detail["node_id"] == "n1"
    assert detail["node_type"] == "source.csv"
    assert detail["category"] == "resource"


def test_run_error_types_are_distinguishable(tmp_path: Path) -> None:
    """validation_error ≠ execution_error : les deux cas sont différenciables par error_type."""
    body_invalid = {
        "version": "0.1.0",
        "id": "t",
        "name": "t",
        "nodes": [{"id": "n1", "type": "source.csv", "params": {}}],
        "edges": [],
    }
    resp_validation = client.post("/jobs/run", json=body_invalid)

    missing = str(tmp_path / "missing.csv")
    out = str(tmp_path / "out.parquet")
    resp_execution = client.post("/jobs/run", json=_job_body(missing, out))

    assert resp_validation.json()["detail"]["error_type"] == "validation_error"
    assert resp_execution.json()["detail"]["error_type"] == "execution_error"
    assert (
        resp_validation.json()["detail"]["error_type"]
        != resp_execution.json()["detail"]["error_type"]
    )
