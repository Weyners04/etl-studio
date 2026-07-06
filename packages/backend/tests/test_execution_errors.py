"""Tests d'attribution des erreurs d'exécution à leur nœud culpable.

Vérifie que _diagnose() isole précisément le nœud responsable et catégorise
correctement l'erreur, sink compris.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import app.nodes  # noqa: F401  (enregistre les nœuds)
from app.interpreter import build_plan, validate
from app.interpreter.errors import ErrorCategory, ExecutionError
from app.interpreter.execute import execute
from app.ir import IRGraph


def _graph(nodes: list[dict], edges: list[dict], gid: str = "t") -> IRGraph:
    return IRGraph.model_validate(
        {
            "version": "0.1.0",
            "id": gid,
            "name": "test",
            "nodes": nodes,
            "edges": edges,
        }
    )


# ──────────────────────────────────────────────────────────────
# Test 1 — source manquante → attributée à la source, RESOURCE
# ──────────────────────────────────────────────────────────────


def test_missing_csv_attributed_to_source(tmp_path: Path) -> None:
    missing = str(tmp_path / "missing.csv")
    graph = _graph(
        nodes=[
            {"id": "n1", "type": "source.csv", "params": {"path": missing}},
            {"id": "n2", "type": "sink.parquet", "params": {"path": str(tmp_path / "out.parquet")}},
        ],
        edges=[{"id": "e1", "source": "n1", "target": "n2"}],
    )
    validate(graph)

    with pytest.raises(ExecutionError) as exc_info:
        execute(build_plan(graph))

    err = exc_info.value
    assert err.node_id == "n1"
    assert err.category == ErrorCategory.RESOURCE


# ──────────────────────────────────────────────────────────────
# Test 2 — colonne inexistante dans filter → attributée au transform, DATA
# ──────────────────────────────────────────────────────────────


def test_bad_column_in_filter_attributed_to_transform(tmp_path: Path) -> None:
    csv = tmp_path / "data.csv"
    csv.write_text("id,name\n1,Alice\n")
    graph = _graph(
        nodes=[
            {"id": "n1", "type": "source.csv", "params": {"path": str(csv)}},
            {
                "id": "n2",
                "type": "transform.filter",
                "params": {"column": "nonexistent_column", "operator": "==", "value": 1},
            },
            {"id": "n3", "type": "sink.parquet", "params": {"path": str(tmp_path / "out.parquet")}},
        ],
        edges=[
            {"id": "e1", "source": "n1", "target": "n2"},
            {"id": "e2", "source": "n2", "target": "n3"},
        ],
    )
    validate(graph)

    with pytest.raises(ExecutionError) as exc_info:
        execute(build_plan(graph))

    err = exc_info.value
    assert err.node_id == "n2"
    assert err.category == ErrorCategory.DATA


# ──────────────────────────────────────────────────────────────
# Test 3 — exécution réussie inchangée (régression)
# ──────────────────────────────────────────────────────────────


def test_successful_execution_raises_no_error(tmp_path: Path) -> None:
    csv = tmp_path / "data.csv"
    csv.write_text("id,age\n1,25\n2,16\n")
    out = tmp_path / "out.parquet"
    graph = _graph(
        nodes=[
            {"id": "n1", "type": "source.csv", "params": {"path": str(csv)}},
            {
                "id": "n2",
                "type": "transform.filter",
                "params": {"column": "age", "operator": ">=", "value": 18},
            },
            {"id": "n3", "type": "sink.parquet", "params": {"path": str(out)}},
        ],
        edges=[
            {"id": "e1", "source": "n1", "target": "n2"},
            {"id": "e2", "source": "n2", "target": "n3"},
        ],
    )
    validate(graph)

    result = execute(build_plan(graph))
    assert result["n3"] == {"written": str(out)}
    assert out.exists()


# ──────────────────────────────────────────────────────────────
# Test 4 — RESOURCE ≠ DATA : deux erreurs de nature différente
# ──────────────────────────────────────────────────────────────


def test_error_categories_are_distinct(tmp_path: Path) -> None:
    # RESOURCE : fichier source manquant
    graph_resource = _graph(
        nodes=[
            {"id": "n1", "type": "source.csv", "params": {"path": str(tmp_path / "missing.csv")}},
            {"id": "n2", "type": "sink.parquet", "params": {"path": str(tmp_path / "r.parquet")}},
        ],
        edges=[{"id": "e1", "source": "n1", "target": "n2"}],
        gid="t_resource",
    )
    validate(graph_resource)
    with pytest.raises(ExecutionError) as exc_resource:
        execute(build_plan(graph_resource))

    # DATA : colonne inexistante
    csv = tmp_path / "data.csv"
    csv.write_text("a,b\n1,2\n")
    graph_data = _graph(
        nodes=[
            {"id": "n1", "type": "source.csv", "params": {"path": str(csv)}},
            {
                "id": "n2",
                "type": "transform.filter",
                "params": {"column": "nope", "operator": "==", "value": 1},
            },
            {"id": "n3", "type": "sink.parquet", "params": {"path": str(tmp_path / "d.parquet")}},
        ],
        edges=[
            {"id": "e1", "source": "n1", "target": "n2"},
            {"id": "e2", "source": "n2", "target": "n3"},
        ],
        gid="t_data",
    )
    validate(graph_data)
    with pytest.raises(ExecutionError) as exc_data:
        execute(build_plan(graph_data))

    assert exc_resource.value.category == ErrorCategory.RESOURCE
    assert exc_data.value.category == ErrorCategory.DATA
    assert exc_resource.value.category != exc_data.value.category


# ──────────────────────────────────────────────────────────────
# Test 5 — erreur propre au sink → attributée AU sink, RESOURCE
#
# Ce test échoue avec l'ancienne logique (sink skipé → repli honnête,
# node_id=None) et passe avec la nouvelle (sonde sink attrape l'OSError).
# ──────────────────────────────────────────────────────────────


def test_sink_write_error_attributed_to_sink(tmp_path: Path) -> None:
    csv = tmp_path / "data.csv"
    csv.write_text("id,name\n1,Alice\n")

    # Crée un fichier ordinaire là où le sink voudrait un dossier parent.
    # mkdir(parents=True, exist_ok=True) lèvera FileExistsError.
    blocking = tmp_path / "blocking_file"
    blocking.write_text("I am a file, not a directory")
    sink_path = blocking / "output.parquet"

    graph = _graph(
        nodes=[
            {"id": "n1", "type": "source.csv", "params": {"path": str(csv)}},
            {"id": "n2", "type": "sink.parquet", "params": {"path": str(sink_path)}},
        ],
        edges=[{"id": "e1", "source": "n1", "target": "n2"}],
    )
    validate(graph)

    with pytest.raises(ExecutionError) as exc_info:
        execute(build_plan(graph))

    err = exc_info.value
    assert err.node_id == "n2", (
        f"Le sink doit être le coupable ; obtenu node_id={err.node_id!r}, message={str(err)!r}"
    )
    assert err.category == ErrorCategory.RESOURCE
