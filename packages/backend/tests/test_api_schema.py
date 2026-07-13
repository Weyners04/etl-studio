"""Tests de la route POST /jobs/schema : résolution sans exécution."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

import app.nodes  # noqa: F401  (enregistre les nœuds)
from app.main import api_app

client = TestClient(api_app)


def _body(nodes: list[dict], edges: list[dict]) -> dict:  # type: ignore[type-arg]
    return {
        "version": "0.1.0",
        "id": "test_schema",
        "name": "test",
        "nodes": nodes,
        "edges": edges,
    }


def test_schema_route_returns_columns_per_node(tmp_path: Path) -> None:
    """Source CSV accessible → colonnes et dtypes pour chaque nœud, sink → null."""
    csv = tmp_path / "data.csv"
    csv.write_text("id,name\n1,Alice\n")
    out = tmp_path / "out.parquet"

    body = _body(
        nodes=[
            {"id": "n1", "type": "source.csv", "params": {"path": str(csv)}},
            {"id": "n2", "type": "sink.parquet", "params": {"path": str(out)}},
        ],
        edges=[{"id": "e1", "source": "n1", "target": "n2"}],
    )
    response = client.post("/jobs/schema", json=body)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"

    n1 = data["nodes"]["n1"]
    assert n1["columns"] is not None
    col_names = [c["name"] for c in n1["columns"]]
    assert col_names == ["id", "name"]
    assert all("dtype" in c for c in n1["columns"])
    assert "warnings" not in n1

    # Sink n'a pas de sortie.
    assert data["nodes"]["n2"]["columns"] is None


def test_schema_route_propagation_with_column_filter(tmp_path: Path) -> None:
    """Source → RowFilter (passthrough) → ColumnFilter : vérification de projection."""
    csv = tmp_path / "people.csv"
    csv.write_text("id,name,age\n1,Alice,25\n")

    body = _body(
        nodes=[
            {"id": "n1", "type": "source.csv", "params": {"path": str(csv)}},
            {
                "id": "n2",
                "type": "transform.filter",
                "params": {"column": "age", "operator": ">=", "value": 18},
            },
            {"id": "n3", "type": "transform.select", "params": {"columns": ["name"]}},
        ],
        edges=[
            {"id": "e1", "source": "n1", "target": "n2"},
            {"id": "e2", "source": "n2", "target": "n3"},
        ],
    )
    response = client.post("/jobs/schema", json=body)
    assert response.status_code == 200
    data = response.json()

    n3 = data["nodes"]["n3"]
    assert n3["columns"] is not None
    assert [c["name"] for c in n3["columns"]] == ["name"]


def test_schema_route_inaccessible_source_returns_null(tmp_path: Path) -> None:
    """Source inaccessible → columns: null, aucune erreur HTTP levée."""
    body = _body(
        nodes=[
            {"id": "n1", "type": "source.csv", "params": {"path": "/no/such/file.csv"}},
            {
                "id": "n2",
                "type": "transform.filter",
                "params": {"column": "x", "operator": ">", "value": 0},
            },
        ],
        edges=[{"id": "e1", "source": "n1", "target": "n2"}],
    )
    response = client.post("/jobs/schema", json=body)
    assert response.status_code == 200
    data = response.json()

    assert data["nodes"]["n1"]["columns"] is None
    assert data["nodes"]["n2"]["columns"] is None


def test_schema_route_warning_for_missing_column(tmp_path: Path) -> None:
    """ColumnFilter colonne absente → warning présent dans la réponse."""
    csv = tmp_path / "data.csv"
    csv.write_text("id,name\n1,Alice\n")

    body = _body(
        nodes=[
            {"id": "n1", "type": "source.csv", "params": {"path": str(csv)}},
            {"id": "n2", "type": "transform.select", "params": {"columns": ["id", "missing_col"]}},
        ],
        edges=[{"id": "e1", "source": "n1", "target": "n2"}],
    )
    response = client.post("/jobs/schema", json=body)
    assert response.status_code == 200
    data = response.json()

    n2 = data["nodes"]["n2"]
    assert n2["columns"] is not None
    assert [c["name"] for c in n2["columns"]] == ["id"]
    assert "warnings" in n2
    assert any("missing_col" in w for w in n2["warnings"])
