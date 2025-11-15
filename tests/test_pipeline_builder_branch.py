import importlib

import pytest


@pytest.fixture
def pipeline_module():
    return importlib.reload(importlib.import_module("server.pipeline"))


def test_build_relation_records_success_history(monkeypatch, pipeline_module):
    captured = {}

    class DummyBuilder:
        def __init__(self):
            captured["initialized"] = True

        def build_relations(self, payload):
            captured["payload"] = payload
            return {"status": "ok"}

    monkeypatch.setattr(pipeline_module, "Builder", DummyBuilder)

    state = {"status": "Builder Agent", "input": "construct a tactic", "pipeline_history": []}
    result = pipeline_module.build_relation(state)

    assert captured["payload"] == "construct a tactic"
    assert result["status"] == "End"
    assert result["final_answer"]
    assert result.get("pipeline_history"), "Builder branch should append a pipeline_history entry on success"
