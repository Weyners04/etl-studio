"""Test d'exécution bout en bout : CSV -> filter -> select -> Parquet.

Utilise tmp_path (pytest) pour créer l'entrée et capturer la sortie sans
toucher au système de fichiers réel.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl

import app.nodes  # noqa: F401  (enregistre les nœuds)
from app.interpreter import build_plan, validate
from app.interpreter.execute import execute
from app.ir import IRGraph


def _make_graph(csv_path: str, out_path: str) -> IRGraph:
    return IRGraph.model_validate(
        {
            "version": "0.1.0",
            "id": "test_e2e",
            "name": "Test bout en bout",
            "nodes": [
                {
                    "id": "n1",
                    "type": "source.csv",
                    "params": {"path": csv_path},
                },
                {
                    "id": "n2",
                    "type": "transform.filter",
                    "params": {"column": "age", "operator": ">=", "value": 18},
                },
                {
                    "id": "n3",
                    "type": "transform.select",
                    "params": {"columns": ["id", "name", "age"]},
                },
                {
                    "id": "n4",
                    "type": "sink.parquet",
                    "params": {"path": out_path},
                },
            ],
            "edges": [
                {"id": "e1", "source": "n1", "target": "n2"},
                {"id": "e2", "source": "n2", "target": "n3"},
                {"id": "e3", "source": "n3", "target": "n4"},
            ],
        }
    )


def test_end_to_end_lazy_execution(tmp_path: Path) -> None:
    """Un job CSV -> filter(age >= 18) -> select -> Parquet produit le bon résultat."""
    csv_file = tmp_path / "people.csv"
    csv_file.write_text("id,name,age\n1,Alice,25\n2,Bob,16\n3,Carol,30\n")
    out_file = tmp_path / "adults.parquet"

    graph = _make_graph(str(csv_file), str(out_file))
    validate(graph)
    result = execute(build_plan(graph))

    # Le sink renvoie un récapitulatif
    assert result["n4"] == {"written": str(out_file)}

    # Le fichier Parquet existe et contient les bonnes lignes
    assert out_file.exists()
    df = pl.read_parquet(out_file)
    assert df.columns == ["id", "name", "age"]
    assert len(df) == 2  # Alice (25) et Carol (30) — Bob (16) filtré
    assert set(df["name"].to_list()) == {"Alice", "Carol"}
    assert all(df["age"] >= 18)
