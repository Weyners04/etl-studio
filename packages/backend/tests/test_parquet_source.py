"""Tests de source.parquet (ParquetReader) : lecture d'un fichier Parquet existant."""

from __future__ import annotations

from pathlib import Path

import polars as pl

import app.nodes  # noqa: F401  (enregistre les nœuds)
from app.interpreter import build_plan, validate
from app.interpreter.execute import execute
from app.ir import IRGraph


def _graph(parquet_path: str, out_path: str) -> IRGraph:
    return IRGraph.model_validate(
        {
            "version": "0.1.0",
            "id": "test_parquet_source",
            "name": "test",
            "nodes": [
                {"id": "n1", "type": "source.parquet", "params": {"path": parquet_path}},
                {"id": "n2", "type": "sink.parquet", "params": {"path": out_path}},
            ],
            "edges": [{"id": "e1", "source": "n1", "target": "n2"}],
        }
    )


def test_parquet_source_reads_correct_rows_and_columns(tmp_path: Path) -> None:
    """ParquetReader lit un fichier Parquet et charge les bonnes lignes et colonnes."""
    src = tmp_path / "input.parquet"
    pl.DataFrame({"id": [1, 2, 3], "name": ["Alice", "Bob", "Carol"]}).write_parquet(src)

    out = tmp_path / "output.parquet"
    graph = _graph(str(src), str(out))
    validate(graph)
    result = execute(build_plan(graph))

    assert result["n2"] == {"written": str(out)}
    df = pl.read_parquet(out)
    assert df.columns == ["id", "name"]
    assert len(df) == 3
    assert df["name"].to_list() == ["Alice", "Bob", "Carol"]


def test_parquet_source_preserves_schema(tmp_path: Path) -> None:
    """ParquetReader conserve les types de colonnes définis dans le fichier source."""
    src = tmp_path / "typed.parquet"
    pl.DataFrame({"x": [1.0, 2.5], "flag": [True, False]}).write_parquet(src)

    out = tmp_path / "out.parquet"
    graph = _graph(str(src), str(out))
    validate(graph)
    execute(build_plan(graph))

    df = pl.read_parquet(out)
    assert df["x"].dtype == pl.Float64
    assert df["flag"].dtype == pl.Boolean
