"""Aller-retour CSV → Parquet → CSV : prouve que les formats se chaînent.

Job 1 : source.csv  → sink.parquet  (CSVReader  → ParquetWriter)
Job 2 : source.parquet → sink.csv   (ParquetReader → CSVWriter)

Le résultat final est relu avec Polars pour vérifier que les données
sont intactes après les deux conversions.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl

import app.nodes  # noqa: F401  (enregistre les nœuds)
from app.interpreter import build_plan, validate
from app.interpreter.execute import execute
from app.ir import IRGraph


def _csv_to_parquet(csv_path: str, parquet_path: str) -> IRGraph:
    return IRGraph.model_validate(
        {
            "version": "0.1.0",
            "id": "job_csv_to_parquet",
            "name": "CSV → Parquet",
            "nodes": [
                {"id": "n1", "type": "source.csv", "params": {"path": csv_path}},
                {"id": "n2", "type": "sink.parquet", "params": {"path": parquet_path}},
            ],
            "edges": [{"id": "e1", "source": "n1", "target": "n2"}],
        }
    )


def _parquet_to_csv(parquet_path: str, csv_path: str) -> IRGraph:
    return IRGraph.model_validate(
        {
            "version": "0.1.0",
            "id": "job_parquet_to_csv",
            "name": "Parquet → CSV",
            "nodes": [
                {"id": "n1", "type": "source.parquet", "params": {"path": parquet_path}},
                {"id": "n2", "type": "sink.csv", "params": {"path": csv_path}},
            ],
            "edges": [{"id": "e1", "source": "n1", "target": "n2"}],
        }
    )


def test_csv_to_parquet_to_csv_roundtrip(tmp_path: Path) -> None:
    """Les données sont intactes après conversion CSV → Parquet → CSV."""
    original_csv = tmp_path / "original.csv"
    original_csv.write_text("id,name,score\n1,Alice,95\n2,Bob,82\n3,Carol,78\n")

    intermediate = tmp_path / "intermediate.parquet"
    final_csv = tmp_path / "final.csv"

    # Job 1 : CSV → Parquet
    graph1 = _csv_to_parquet(str(original_csv), str(intermediate))
    validate(graph1)
    result1 = execute(build_plan(graph1))
    assert result1["n2"] == {"written": str(intermediate)}
    assert intermediate.exists()

    # Job 2 : Parquet → CSV
    graph2 = _parquet_to_csv(str(intermediate), str(final_csv))
    validate(graph2)
    result2 = execute(build_plan(graph2))
    assert result2["n2"] == {"written": str(final_csv)}
    assert final_csv.exists()

    # Vérification des données finales
    df_original = pl.read_csv(original_csv)
    df_final = pl.read_csv(final_csv)

    assert df_final.columns == df_original.columns
    assert len(df_final) == len(df_original)
    assert df_final["name"].to_list() == df_original["name"].to_list()
    assert df_final["score"].to_list() == df_original["score"].to_list()
