"""Tests de execute_debug : comptages, échantillons, attribution d'erreur, résultats partiels."""

from __future__ import annotations

from pathlib import Path

import pytest

import app.nodes  # noqa: F401  (enregistre les nœuds)
from app.interpreter import build_plan, validate
from app.interpreter.execute_debug import DEBUG_SAMPLE_SIZE, DebugExecutionError, execute_debug
from app.ir import IRGraph


def _graph(nodes: list[dict], edges: list[dict], gid: str = "t") -> IRGraph:  # type: ignore[type-arg]
    return IRGraph.model_validate(
        {"version": "0.1.0", "id": gid, "name": "test", "nodes": nodes, "edges": edges}
    )


def test_debug_row_counts_correct(tmp_path: Path) -> None:
    """La source rapporte 3 lignes, le filtre en retient 2, le sink a row_count=None."""
    csv = tmp_path / "data.csv"
    csv.write_text("id,name,age\n1,Alice,25\n2,Bob,16\n3,Carol,30\n")
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
    results = execute_debug(build_plan(graph))

    by_id = {r.node_id: r for r in results}
    assert by_id["n1"].row_count == 3
    assert by_id["n2"].row_count == 2
    assert by_id["n3"].row_count is None


def test_debug_sample_capped_at_debug_sample_size(tmp_path: Path) -> None:
    """Avec 15 lignes en entrée, l'échantillon est limité à DEBUG_SAMPLE_SIZE."""
    csv = tmp_path / "data.csv"
    csv.write_text("id\n" + "\n".join(str(i) for i in range(15)) + "\n")
    out = tmp_path / "out.parquet"

    graph = _graph(
        nodes=[
            {"id": "n1", "type": "source.csv", "params": {"path": str(csv)}},
            {"id": "n2", "type": "sink.parquet", "params": {"path": str(out)}},
        ],
        edges=[{"id": "e1", "source": "n1", "target": "n2"}],
    )
    validate(graph)
    results = execute_debug(build_plan(graph))

    source_result = next(r for r in results if r.node_id == "n1")
    assert source_result.row_count == 15
    assert len(source_result.sample) == DEBUG_SAMPLE_SIZE


def test_debug_sample_content_matches_rows(tmp_path: Path) -> None:
    """L'échantillon contient les vraies valeurs des premières lignes."""
    csv = tmp_path / "data.csv"
    csv.write_text("id,name\n1,Alice\n2,Bob\n")
    out = tmp_path / "out.parquet"

    graph = _graph(
        nodes=[
            {"id": "n1", "type": "source.csv", "params": {"path": str(csv)}},
            {"id": "n2", "type": "sink.parquet", "params": {"path": str(out)}},
        ],
        edges=[{"id": "e1", "source": "n1", "target": "n2"}],
    )
    validate(graph)
    results = execute_debug(build_plan(graph))

    sample = next(r for r in results if r.node_id == "n1").sample
    assert sample[0] == {"id": 1, "name": "Alice"}
    assert sample[1] == {"id": 2, "name": "Bob"}


def test_debug_error_attribution_and_partial_results(tmp_path: Path) -> None:
    """Nœud en échec → DebugExecutionError sur le bon nœud + n1 dans les résultats partiels."""
    csv = tmp_path / "data.csv"
    csv.write_text("id,name\n1,Alice\n")
    out = tmp_path / "out.parquet"

    graph = _graph(
        nodes=[
            {"id": "n1", "type": "source.csv", "params": {"path": str(csv)}},
            {
                "id": "n2",
                "type": "transform.filter",
                "params": {"column": "nonexistent", "operator": "==", "value": 1},
            },
            {"id": "n3", "type": "sink.parquet", "params": {"path": str(out)}},
        ],
        edges=[
            {"id": "e1", "source": "n1", "target": "n2"},
            {"id": "e2", "source": "n2", "target": "n3"},
        ],
    )
    validate(graph)

    with pytest.raises(DebugExecutionError) as exc_info:
        execute_debug(build_plan(graph))

    err = exc_info.value
    assert err.cause.node_id == "n2"
    assert err.cause.node_type == "transform.filter"
    partial_ids = [r.node_id for r in err.partial]
    assert "n1" in partial_ids
    assert "n2" not in partial_ids


def test_debug_sink_result_has_written_path(tmp_path: Path) -> None:
    """Le résultat du sink a row_count=None, sample=[] et le chemin du fichier écrit."""
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
    validate(graph)
    results = execute_debug(build_plan(graph))

    sink = next(r for r in results if r.node_id == "n2")
    assert sink.row_count is None
    assert sink.sample == []
    assert sink.written == str(out)
