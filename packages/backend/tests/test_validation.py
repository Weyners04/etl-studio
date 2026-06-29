"""Tests de validation des params et de la cardinalité des ports.

Chaque cas de test construit une variante minimale du job de référence
(sample-job.json) pour cibler exactement la règle testée.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import app.nodes  # noqa: F401  (enregistre les nœuds)
from app.ir import IRGraph
from app.interpreter import validate
from app.interpreter.validate import ValidationError

SAMPLE_PATH = (
    Path(__file__).resolve().parents[3] / "packages" / "ir-schema" / "examples" / "sample-job.json"
)


def load_sample() -> dict:
    return json.loads(SAMPLE_PATH.read_text())


def make_graph(raw: dict) -> IRGraph:
    return IRGraph.model_validate(raw)


# ---------------------------------------------------------------------------
# Baseline
# ---------------------------------------------------------------------------


def test_valid_sample_still_passes():
    """Le job de référence doit toujours valider sans erreur."""
    validate(make_graph(load_sample()))


# ---------------------------------------------------------------------------
# Validation des params
# ---------------------------------------------------------------------------


def test_missing_required_param():
    """Un nœud source.csv sans 'path' doit lever une ValidationError claire."""
    raw = load_sample()
    # Retire 'path' du premier nœud (source.csv)
    raw["nodes"][0]["params"] = {}
    with pytest.raises(ValidationError) as exc_info:
        validate(make_graph(raw))
    msg = str(exc_info.value)
    assert "n1" in msg
    assert "source.csv" in msg
    assert "path" in msg


def test_wrong_type_param():
    """transform.select avec columns en string (pas list[str]) doit échouer."""
    raw = load_sample()
    # Nœud n3 est transform.select ; columns doit être list[str]
    raw["nodes"][2]["params"]["columns"] = "pas-une-liste"
    with pytest.raises(ValidationError) as exc_info:
        validate(make_graph(raw))
    msg = str(exc_info.value)
    assert "n3" in msg
    assert "transform.select" in msg
    assert "columns" in msg


# ---------------------------------------------------------------------------
# Cardinalité des ports
# ---------------------------------------------------------------------------


def test_source_with_incoming_edge():
    """Une source qui reçoit une arête viole sa cardinalité (max_in=0)."""
    raw = load_sample()
    # Ajoute un second nœud source et une arête vers n1 — pas de cycle, mais
    # n1 se retrouve avec 1 arête entrante alors que max_in=0.
    raw["nodes"].append({"id": "n0", "type": "source.csv", "params": {"path": "other.csv"}})
    raw["edges"].append({"id": "e_bad", "source": "n0", "target": "n1"})
    with pytest.raises(ValidationError) as exc_info:
        validate(make_graph(raw))
    msg = str(exc_info.value)
    assert "n1" in msg
    assert "source.csv" in msg
    assert "entrante" in msg


def test_sink_with_outgoing_edge():
    """Un sink qui émet une arête viole sa cardinalité (max_out=0)."""
    raw = load_sample()
    # Ajoute un nœud transform.filter supplémentaire et une arête depuis n4 (sink)
    raw["nodes"].append({"id": "n5", "type": "transform.filter", "params": {"expr": "age > 0"}})
    raw["edges"].append({"id": "e_bad", "source": "n4", "target": "n5"})
    with pytest.raises(ValidationError) as exc_info:
        validate(make_graph(raw))
    msg = str(exc_info.value)
    assert "n4" in msg
    assert "sink.parquet" in msg
    assert "sortante" in msg
