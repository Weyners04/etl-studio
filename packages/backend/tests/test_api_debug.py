"""Tests de la route POST /jobs/debug : structure de réponse et erreurs."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

import app.nodes  # noqa: F401  (enregistre les nœuds)
from app.main import api_app

client = TestClient(api_app)


def _body(csv_path: str, out_path: str) -> dict:  # type: ignore[type-arg]
    return {
        "version": "0.1.0",
        "id": "test_debug",
        "name": "Test debug",
        "nodes": [
            {"id": "n1", "type": "source.csv", "params": {"path": csv_path}},
            {"id": "n2", "type": "sink.parquet", "params": {"path": out_path}},
        ],
        "edges": [{"id": "e1", "source": "n1", "target": "n2"}],
    }


def test_debug_success_returns_nodes_and_outputs(tmp_path: Path) -> None:
    """Un job valide → 200 avec nodes (row_count + sample) et outputs (written)."""
    csv = tmp_path / "in.csv"
    csv.write_text("id,name\n1,Alice\n2,Bob\n")
    out = tmp_path / "out.parquet"

    response = client.post("/jobs/debug", json=_body(str(csv), str(out)))
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"

    by_id = {n["node_id"]: n for n in data["nodes"]}
    assert by_id["n1"]["row_count"] == 2
    assert len(by_id["n1"]["sample"]) == 2
    assert by_id["n2"]["row_count"] is None
    assert by_id["n2"]["sample"] == []

    assert data["outputs"] == [{"node_id": "n2", "written": str(out)}]


def test_debug_execution_error_includes_partial_nodes(tmp_path: Path) -> None:
    """Un CSV manquant → 422 structuré avec partial_nodes des nœuds déjà exécutés."""
    missing = str(tmp_path / "missing.csv")
    out = str(tmp_path / "out.parquet")

    response = client.post("/jobs/debug", json=_body(missing, out))
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["error_type"] == "execution_error"
    assert detail["node_id"] == "n1"
    assert detail["node_type"] == "source.csv"
    assert detail["category"] == "resource"
    assert isinstance(detail["partial_nodes"], list)
    # n1 a échoué immédiatement → aucun résultat partiel
    assert detail["partial_nodes"] == []


def test_debug_validation_error_is_structured() -> None:
    """Un graphe invalide (param manquant) → 422 avec error_type validation_error."""
    body = {
        "version": "0.1.0",
        "id": "t",
        "name": "t",
        "nodes": [{"id": "n1", "type": "source.csv", "params": {}}],
        "edges": [],
    }
    response = client.post("/jobs/debug", json=body)
    assert response.status_code == 422
    assert response.json()["detail"]["error_type"] == "validation_error"
