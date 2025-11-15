import importlib

import pytest


@pytest.fixture
def pipeline_module():
    return importlib.reload(importlib.import_module("server.pipeline"))


def test_execute_tools_returns_tool_payload(monkeypatch, pipeline_module):
    def fake_position(state):
        return {"result": "position"}

    monkeypatch.setattr(pipeline_module, "verify_piece_position", fake_position)

    state = {"status": "Verify Piece Position"}
    result = pipeline_module.execute_tools(state)
    assert result["verifier_agent_outcome"] == {"result": "position"}
    assert result["pipeline_history"][-1][1] == {"result": "position"}


def test_run_main_tracks_builder_selection(monkeypatch, pipeline_module):
    class DummyRunner:
        def invoke(self, inputs):
            return {"output": "Builder Agent"}

    monkeypatch.setattr(pipeline_module, "main_agent_runnable", DummyRunner())

    result = pipeline_module.run_main({"input": "build a relation"})

    assert ("Main Agent", "Builder Agent") in result["pipeline_history"]
    assert result["status"] == "Builder Agent"
