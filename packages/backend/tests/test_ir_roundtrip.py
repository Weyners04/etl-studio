"""Tests Phase 0 : l'exemple de référence se parse, valide et planifie."""

from __future__ import annotations

import json
from pathlib import Path

from app.ir import IRGraph
from app.interpreter import build_plan, validate
import app.nodes  # noqa: F401  (enregistre les nœuds)

SAMPLE = (
    Path(__file__).resolve().parents[3] / "packages" / "ir-schema" / "examples" / "sample-job.json"
)


def load_sample() -> IRGraph:
    return IRGraph.model_validate(json.loads(SAMPLE.read_text()))


def test_sample_parses():
    graph = load_sample()
    assert graph.id == "job_sample_clients"
    assert len(graph.nodes) == 4
    assert len(graph.edges) == 3


def test_sample_validates():
    validate(load_sample())  # ne lève pas


def test_plan_is_topologically_ordered():
    plan = build_plan(load_sample())
    order = [step.node.id for step in plan.steps]
    assert order == ["n1", "n2", "n3", "n4"]
