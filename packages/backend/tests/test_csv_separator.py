"""Tests du paramètre separator sur source.csv.

Vérifie que :
- separator=";" lit correctement un CSV à points-virgules
- separator="," (défaut) donne le même résultat qu'avant (régression)
- /nodes expose bien l'enum [",", ";"] dans le params_schema de source.csv
"""

from __future__ import annotations

from pathlib import Path

import polars as pl
from fastapi.testclient import TestClient

import app.nodes  # noqa: F401  (enregistre les nœuds)
from app.interpreter import build_plan, validate
from app.interpreter.execute import execute
from app.ir import IRGraph
from app.main import api_app

client = TestClient(api_app)


def _graph(csv_path: str, out_path: str, separator: str) -> IRGraph:
    return IRGraph.model_validate(
        {
            "version": "0.1.0",
            "id": "test_sep",
            "name": "test",
            "nodes": [
                {
                    "id": "n1",
                    "type": "source.csv",
                    "params": {"path": csv_path, "separator": separator},
                },
                {"id": "n2", "type": "sink.parquet", "params": {"path": out_path}},
            ],
            "edges": [{"id": "e1", "source": "n1", "target": "n2"}],
        }
    )


def test_semicolon_separator_reads_correct_columns(tmp_path: Path) -> None:
    """Un CSV à points-virgules lu avec separator=';' donne les bonnes colonnes."""
    csv = tmp_path / "data.csv"
    csv.write_text("id;name;age\n1;Alice;25\n2;Bob;30\n")
    out = tmp_path / "out.parquet"

    graph = _graph(str(csv), str(out), separator=";")
    validate(graph)
    result = execute(build_plan(graph))

    assert result["n2"] == {"written": str(out)}
    df = pl.read_parquet(out)
    assert df.columns == ["id", "name", "age"]
    assert len(df) == 2
    assert df["name"].to_list() == ["Alice", "Bob"]


def test_default_comma_separator_is_unchanged(tmp_path: Path) -> None:
    """Le défaut separator=',' lit les CSV virgule comme avant (régression)."""
    csv = tmp_path / "data.csv"
    csv.write_text("id,name\n1,Alice\n2,Bob\n")
    out = tmp_path / "out.parquet"

    graph = _graph(str(csv), str(out), separator=",")
    validate(graph)
    execute(build_plan(graph))

    df = pl.read_parquet(out)
    assert df.columns == ["id", "name"]
    assert len(df) == 2


def test_nodes_exposes_separator_enum_for_source_csv() -> None:
    """La route /nodes expose separator avec enum=[',', ';'] pour source.csv."""
    response = client.get("/nodes")
    assert response.status_code == 200
    nodes = response.json()
    source = next(n for n in nodes if n["type"] == "source.csv")
    sep_schema = source["params_schema"]["properties"]["separator"]
    assert sep_schema["enum"] == [",", ";"]
    assert sep_schema["default"] == ","
