"""Tests de la route GET /nodes : liste enrichie avec catégorie et schéma params."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import api_app  # importe app.nodes en effet de bord → nœuds enregistrés

client = TestClient(api_app)


def test_nodes_returns_list():
    """La route renvoie une liste (pas un dict) contenant tous les types enregistrés."""
    response = client.get("/nodes")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    types = [n["type"] for n in data]
    assert "source.csv" in types
    assert "transform.filter" in types
    assert "transform.select" in types
    assert "sink.parquet" in types


def test_transform_filter_schema_has_operator_enum():
    """transform.filter expose l'énumération des opérateurs dans son params_schema.

    C'est ce qui permet au frontend de générer un menu déroulant plutôt qu'un champ libre.
    """
    response = client.get("/nodes")
    nodes = response.json()
    filter_node = next(n for n in nodes if n["type"] == "transform.filter")

    assert filter_node["category"] == "transform"

    schema = filter_node["params_schema"]
    operator_schema = schema["properties"]["operator"]
    assert operator_schema["enum"] == ["==", "!=", ">", ">=", "<", "<="]
    assert "column" in schema["required"]
    assert "operator" in schema["required"]
    assert "value" in schema["required"]


def test_source_csv_category():
    """source.csv a bien category == 'source', déduit du préfixe."""
    response = client.get("/nodes")
    nodes = response.json()
    source_node = next(n for n in nodes if n["type"] == "source.csv")
    assert source_node["category"] == "source"
    assert "path" in source_node["params_schema"]["properties"]


def test_sink_parquet_category():
    """sink.parquet a bien category == 'sink'."""
    response = client.get("/nodes")
    nodes = response.json()
    sink_node = next(n for n in nodes if n["type"] == "sink.parquet")
    assert sink_node["category"] == "sink"
