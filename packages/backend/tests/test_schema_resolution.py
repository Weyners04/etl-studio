"""Tests du moteur de résolution de schéma (resolve_schemas).

Couvre :
- Source CSV réelle → bonnes colonnes et dtypes.
- Propagation source → RowFilter (passthrough) → ColumnFilter (projection).
- Source inaccessible → None propagé en aval sans erreur.
- ColumnFilter avec colonne absente → warning + schéma partiel.
- Source Parquet réelle → bonnes colonnes et dtypes.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl

import app.nodes  # noqa: F401  (enregistre les nœuds)
from app.interpreter.interpret import build_plan
from app.interpreter.resolve_schema import resolve_schemas
from app.ir import IRGraph


def _graph(nodes: list[dict], edges: list[dict]) -> IRGraph:
    return IRGraph.model_validate(
        {"version": "0.1.0", "id": "test_schema", "name": "test", "nodes": nodes, "edges": edges}
    )


# ---------------------------------------------------------------------------
# Source CSV réelle
# ---------------------------------------------------------------------------


def test_csv_source_resolves_columns_and_dtypes(tmp_path: Path) -> None:
    """Une source CSV existante renvoie les colonnes et dtypes Polars corrects."""
    csv = tmp_path / "data.csv"
    csv.write_text("id,name,age\n1,Alice,25\n")

    graph = _graph(
        nodes=[{"id": "n1", "type": "source.csv", "params": {"path": str(csv)}}],
        edges=[],
    )
    results = resolve_schemas(build_plan(graph))

    schema = results["n1"].schema
    assert schema is not None
    names = [c.name for c in schema]
    dtypes = {c.name: c.dtype for c in schema}
    assert names == ["id", "name", "age"]
    assert dtypes["id"] == "Int64"
    assert dtypes["name"] == "String"
    assert dtypes["age"] == "Int64"


# ---------------------------------------------------------------------------
# Source Parquet réelle
# ---------------------------------------------------------------------------


def test_parquet_source_resolves_columns_and_dtypes(tmp_path: Path) -> None:
    """Une source Parquet existante renvoie les colonnes et dtypes Polars corrects."""
    pq = tmp_path / "data.parquet"
    pl.DataFrame({"x": [1.0, 2.0], "flag": [True, False]}).write_parquet(pq)

    graph = _graph(
        nodes=[{"id": "n1", "type": "source.parquet", "params": {"path": str(pq)}}],
        edges=[],
    )
    results = resolve_schemas(build_plan(graph))

    schema = results["n1"].schema
    assert schema is not None
    dtypes = {c.name: c.dtype for c in schema}
    assert dtypes["x"] == "Float64"
    assert dtypes["flag"] == "Boolean"


# ---------------------------------------------------------------------------
# Propagation source → RowFilter → ColumnFilter
# ---------------------------------------------------------------------------


def test_schema_propagation_through_filter_and_select(tmp_path: Path) -> None:
    """CSVReader → RowFilter (passthrough) → ColumnFilter (projection ordonnée)."""
    csv = tmp_path / "people.csv"
    csv.write_text("id,name,age\n1,Alice,25\n2,Bob,17\n")

    graph = _graph(
        nodes=[
            {"id": "n1", "type": "source.csv", "params": {"path": str(csv)}},
            {
                "id": "n2",
                "type": "transform.filter",
                "params": {"column": "age", "operator": ">=", "value": 18},
            },
            {"id": "n3", "type": "transform.select", "params": {"columns": ["name", "id"]}},
        ],
        edges=[
            {"id": "e1", "source": "n1", "target": "n2"},
            {"id": "e2", "source": "n2", "target": "n3"},
        ],
    )
    results = resolve_schemas(build_plan(graph))

    # RowFilter transmet l'entrée inchangée
    assert results["n2"].schema == results["n1"].schema

    # ColumnFilter réduit et réordonne
    n3_schema = results["n3"].schema
    assert n3_schema is not None
    assert [c.name for c in n3_schema] == ["name", "id"]
    assert results["n3"].warnings == []


# ---------------------------------------------------------------------------
# Source inaccessible → indéterminé propagé
# ---------------------------------------------------------------------------


def test_inaccessible_source_yields_none_propagated(tmp_path: Path) -> None:
    """Un chemin inexistant donne schema=None, propagé en aval sans exception."""
    graph = _graph(
        nodes=[
            {"id": "n1", "type": "source.csv", "params": {"path": "/no/such/file.csv"}},
            {
                "id": "n2",
                "type": "transform.filter",
                "params": {"column": "x", "operator": ">", "value": 0},
            },
            {"id": "n3", "type": "transform.select", "params": {"columns": ["x"]}},
        ],
        edges=[
            {"id": "e1", "source": "n1", "target": "n2"},
            {"id": "e2", "source": "n2", "target": "n3"},
        ],
    )
    results = resolve_schemas(build_plan(graph))

    assert results["n1"].schema is None
    assert results["n2"].schema is None
    assert results["n3"].schema is None


# ---------------------------------------------------------------------------
# ColumnFilter avec colonne absente
# ---------------------------------------------------------------------------


def test_column_filter_missing_column_produces_warning(tmp_path: Path) -> None:
    """ColumnFilter demandant une colonne absente → warning + colonne exclue du résultat."""
    csv = tmp_path / "data.csv"
    csv.write_text("id,name\n1,Alice\n")

    graph = _graph(
        nodes=[
            {"id": "n1", "type": "source.csv", "params": {"path": str(csv)}},
            {"id": "n2", "type": "transform.select", "params": {"columns": ["id", "score"]}},
        ],
        edges=[{"id": "e1", "source": "n1", "target": "n2"}],
    )
    results = resolve_schemas(build_plan(graph))

    n2 = results["n2"]
    assert n2.schema is not None
    assert [c.name for c in n2.schema] == ["id"]  # "score" exclue
    assert any("score" in w for w in n2.warnings)


# ---------------------------------------------------------------------------
# Sink : schema=None (pas de sortie à propager)
# ---------------------------------------------------------------------------


def test_sink_schema_is_none(tmp_path: Path) -> None:
    """Les sinks ont schema=None (ports.max_out == 0, pas de sortie)."""
    csv = tmp_path / "data.csv"
    csv.write_text("id\n1\n")
    out = tmp_path / "out.parquet"

    graph = _graph(
        nodes=[
            {"id": "n1", "type": "source.csv", "params": {"path": str(csv)}},
            {"id": "n2", "type": "sink.parquet", "params": {"path": str(out)}},
        ],
        edges=[{"id": "e1", "source": "n1", "target": "n2"}],
    )
    results = resolve_schemas(build_plan(graph))

    assert results["n1"].schema is not None  # source connue
    assert results["n2"].schema is None  # sink → pas de sortie
