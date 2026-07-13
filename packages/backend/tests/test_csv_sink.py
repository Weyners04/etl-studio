"""Tests de sink.csv (CSVWriter) : écriture en CSV avec séparateurs ',' et ';'."""

from __future__ import annotations

from pathlib import Path

import polars as pl

import app.nodes  # noqa: F401  (enregistre les nœuds)
from app.interpreter import build_plan, validate
from app.interpreter.execute import execute
from app.ir import IRGraph


def _graph(src_path: str, out_path: str, separator: str = ",") -> IRGraph:
    return IRGraph.model_validate(
        {
            "version": "0.1.0",
            "id": "test_csv_sink",
            "name": "test",
            "nodes": [
                {"id": "n1", "type": "source.csv", "params": {"path": src_path}},
                {
                    "id": "n2",
                    "type": "sink.csv",
                    "params": {"path": out_path, "separator": separator},
                },
            ],
            "edges": [{"id": "e1", "source": "n1", "target": "n2"}],
        }
    )


def test_csv_sink_writes_correct_content(tmp_path: Path) -> None:
    """CSVWriter écrit les bonnes colonnes et lignes avec le séparateur virgule."""
    src = tmp_path / "input.csv"
    src.write_text("id,name,age\n1,Alice,25\n2,Bob,30\n")
    out = tmp_path / "output.csv"

    graph = _graph(str(src), str(out), separator=",")
    validate(graph)
    result = execute(build_plan(graph))

    assert result["n2"] == {"written": str(out)}
    assert out.exists()
    df = pl.read_csv(out)
    assert df.columns == ["id", "name", "age"]
    assert len(df) == 2
    assert df["name"].to_list() == ["Alice", "Bob"]


def test_csv_sink_semicolon_separator_in_file(tmp_path: Path) -> None:
    """CSVWriter avec separator=';' produit un fichier dont les champs sont séparés par ';'."""
    src = tmp_path / "input.csv"
    src.write_text("x,y\n1,a\n2,b\n")
    out = tmp_path / "output.csv"

    graph = _graph(str(src), str(out), separator=";")
    validate(graph)
    execute(build_plan(graph))

    raw = out.read_text()
    first_line = raw.splitlines()[0]
    assert ";" in first_line
    assert "," not in first_line

    df = pl.read_csv(out, separator=";")
    assert df.columns == ["x", "y"]
    assert len(df) == 2


def test_csv_sink_creates_parent_directory(tmp_path: Path) -> None:
    """CSVWriter crée le répertoire parent s'il n'existe pas encore."""
    src = tmp_path / "input.csv"
    src.write_text("a\n1\n")
    out = tmp_path / "nested" / "dir" / "output.csv"

    graph = _graph(str(src), str(out))
    validate(graph)
    execute(build_plan(graph))

    assert out.exists()
