from __future__ import annotations

import importlib
import sys
import types
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _install_stub_module(monkeypatch, fullname, attrs=None):
    module = types.ModuleType(fullname)
    if attrs:
        for key, value in attrs.items():
            setattr(module, key, value)
    monkeypatch.setitem(sys.modules, fullname, module)
    if "." in fullname:
        parent_name, _, child = fullname.rpartition(".")
        if parent_name:
            parent = sys.modules.get(parent_name)
            if parent is None:
                parent = _install_stub_module(monkeypatch, parent_name)
            setattr(parent, child, module)
    return module


def _load_pipeline_with_stubs(monkeypatch):
    sys.modules.pop("server.pipeline", None)

    _install_stub_module(
        monkeypatch,
        "langchain_google_genai",
        {"ChatGoogleGenerativeAI": type("StubGemini", (), {})},
    )

    class StubTool:
        def __init__(self, name, func, description="", **kwargs):
            self.name = name
            self.func = func
            self.description = description
            self.kwargs = kwargs

        @classmethod
        def from_function(cls, *, name, func, description="", return_direct=False):
            return cls(name=name, func=func, description=description)

    class StubAgentExecutor:
        def __init__(self, agent, tools, verbose=True, **kwargs):
            self.agent = agent
            self.tools = tools
            self.verbose = verbose
            self.kwargs = kwargs
            self.calls = []

        def invoke(self, payload):
            self.calls.append(payload)
            if callable(self.agent):
                return self.agent(payload)
            return self.agent

    def create_react_agent(llm, tools, prompt):
        def _agent(payload):
            return {"output": payload.get("input", "") or "N/A"}

        return _agent

    _install_stub_module(
        monkeypatch,
        "langchain.agents",
        {
            "Tool": StubTool,
            "AgentExecutor": StubAgentExecutor,
            "create_react_agent": create_react_agent,
        },
    )

    _install_stub_module(
        monkeypatch,
        "langchain_core.agents",
        {
            "AgentAction": type("AgentAction", (), {}),
            "AgentFinish": type("AgentFinish", (), {}),
        },
    )

    class StubPromptTemplate:
        def __init__(self, template):
            self.template = template

        @classmethod
        def from_template(cls, template):
            return cls(template)

    _install_stub_module(
        monkeypatch,
        "langchain.prompts",
        {"PromptTemplate": StubPromptTemplate},
    )

    class StubChatOpenAI:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

    _install_stub_module(
        monkeypatch,
        "langchain_community.chat_models",
        {"ChatOpenAI": StubChatOpenAI},
    )

    class StubWorkflow:
        def stream(self, *_):
            return []

    class StubStateGraph:
        def __init__(self, *_):
            pass

        def add_node(self, *_):
            pass

        def add_edge(self, *_):
            pass

        def add_conditional_edges(self, *_):
            pass

        def set_entry_point(self, *_):
            pass

        def compile(self):
            return StubWorkflow()

    _install_stub_module(
        monkeypatch,
        "langgraph.graph",
        {"StateGraph": StubStateGraph, "END": object()},
    )

    class StubVerifier:
        def parse_fen(self, *_):
            return None

        def verify_piece_position(self, *_):
            return []

        def verify_piece_relation(self, *_):
            return []

        def verify_piece_move_feature(self, *_):
            return []

    class StubBuilder:
        def build_relations(self, *_):
            return "built"

    _install_stub_module(
        monkeypatch,
        "server.neurosymbolicAI",
        {"Verifier": StubVerifier, "Builder": StubBuilder},
    )

    _install_stub_module(
        monkeypatch,
        "server.reinforced_agent",
        {"generate_response": lambda *_, **__: "response"},
    )

    _install_stub_module(
        monkeypatch,
        "server.prompts",
        {
            "PIPELINE_MAIN_PROMPT": "main",
            "PIPELINE_VERIFIER_PROMPT": "verifier",
            "REINFORCED_AGENT_PROMPT": "reinforced",
            "CLASSIC_AGENT_PROMPT": "classic",
            "CYPHER_GENERATION_TEMPLATE": "cypher",
        },
    )

    config_module = _install_stub_module(monkeypatch, "server.config")
    config_module.get_secret = lambda *_, **__: "secret"

    pipeline = importlib.import_module("server.pipeline")
    return importlib.reload(pipeline)


def test_run_verifier_missing_commentary_returns_na(monkeypatch):
    pipeline = _load_pipeline_with_stubs(monkeypatch)

    result = pipeline.run_verifier({"status": "Reinforced Agent"})

    assert result == {"verifier_agent_outcome": "N/A", "status": "N/A"}


def test_run_verifier_skips_agent_when_status_na(monkeypatch):
    pipeline = _load_pipeline_with_stubs(monkeypatch)

    class SpyExecutor:
        def __init__(self):
            self.calls = []

        def invoke(self, payload):
            self.calls.append(payload)
            return {"output": "should not run"}

    spy = SpyExecutor()
    monkeypatch.setattr(pipeline, "verifier_agent_runnable", spy)

    result = pipeline.run_verifier(
        {"commentary_agent_outcome": "text", "status": "N/A"}
    )

    assert result == {"verifier_agent_outcome": "N/A", "status": "N/A"}
    assert spy.calls == []


def test_run_verifier_handles_executor_exception(monkeypatch):
    pipeline = _load_pipeline_with_stubs(monkeypatch)

    class BoomExecutor:
        def __init__(self):
            self.calls = 0

        def invoke(self, payload):
            self.calls += 1
            raise RuntimeError("boom")

    boom = BoomExecutor()
    monkeypatch.setattr(pipeline, "verifier_agent_runnable", boom)

    result = pipeline.run_verifier(
        {"commentary_agent_outcome": "text", "status": "Reinforced Agent"}
    )

    assert result == {"verifier_agent_outcome": "N/A", "status": "N/A"}
    assert boom.calls == 1


def test_run_verifier_returns_pipeline_history_on_success(monkeypatch):
    pipeline = _load_pipeline_with_stubs(monkeypatch)

    class SuccessExecutor:
        def __init__(self):
            self.calls = []

        def invoke(self, payload):
            self.calls.append(payload)
            return {"output": "Clean"}

    success = SuccessExecutor()
    monkeypatch.setattr(pipeline, "verifier_agent_runnable", success)

    result = pipeline.run_verifier(
        {"commentary_agent_outcome": "story", "status": "Reinforced Agent"}
    )

    assert result["verifier_agent_outcome"] == "Clean"
    assert result["status"] == "Clean"
    assert result["pipeline_history"] == [("Tiny Agent", "Clean")]
    assert success.calls == [{"input": "story"}]


def test_execute_tools_returns_na_for_unknown_status(monkeypatch):
    pipeline = _load_pipeline_with_stubs(monkeypatch)
    result = pipeline.execute_tools({"status": "Something Else"})

    assert result == {
        "status": "N/A",
        "verifier_agent_outcome": "N/A",
        "pipeline_history": [("Tiny Agent", "N/A")],
    }


def test_execute_tools_dispatches_to_correct_helper(monkeypatch):
    pipeline = _load_pipeline_with_stubs(monkeypatch)
    calls = []

    def fake_verify(state):
        calls.append(state["status"])
        return "verified"

    monkeypatch.setattr(pipeline, "verify_piece_position", fake_verify)

    result = pipeline.execute_tools({"status": "Verify Piece Position"})

    assert result["verifier_agent_outcome"] == "verified"
    assert result["pipeline_history"] == [("Tiny Agent", "verified")]
    assert calls == ["Verify Piece Position"]


def test_execute_tools_handles_helper_exception(monkeypatch):
    pipeline = _load_pipeline_with_stubs(monkeypatch)

    def boom(_state):
        raise RuntimeError("fail")

    monkeypatch.setattr(pipeline, "verify_piece_position", boom)

    result = pipeline.execute_tools({"status": "Verify Piece Position"})

    assert result == {
        "status": "N/A",
        "verifier_agent_outcome": "N/A",
        "pipeline_history": [("Tiny Agent", "N/A")],
    }
