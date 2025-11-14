import importlib
import sys
import types
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def make_module(name, **attrs):
    module = types.ModuleType(name)
    for key, value in attrs.items():
        setattr(module, key, value)
    return module


class DummyPromptTemplate:
    def __init__(self, template: str):
        self.template = template

    @classmethod
    def from_template(cls, template: str):
        return cls(template)

    def format(self, **kwargs):
        return self.template.format(**kwargs)


class DummyTool:
    def __init__(self, name, func, description):
        self.name = name
        self.func = func
        self.description = description


class DummyAgentExecutor:
    def __init__(self, agent, tools, verbose=False):
        self.agent = agent
        self.tools = tools
        self.verbose = verbose
        self.output = "N/A"

    def invoke(self, *_args, **_kwargs):
        return {"output": self.output}


def dummy_create_react_agent(llm, tools, prompt):
    return {"llm": llm, "tools": tools, "prompt": prompt}


class DummyAgentAction:
    pass


class DummyAgentFinish:
    pass


class DummyStateGraph:
    def __init__(self, _state_type):
        self.nodes = {}
        self.edges = {}
        self.conditional_edges = {}
        self.entry_point = None

    def add_node(self, name, func):
        self.nodes[name] = func

    def add_edge(self, start, end):
        self.edges.setdefault(start, []).append(end)

    def set_entry_point(self, name):
        self.entry_point = name

    def add_conditional_edges(self, node, condition, mapping):
        self.conditional_edges[node] = (condition, mapping)

    @staticmethod
    def _merge_state(state, updates):
        for key, value in updates.items():
            if key == "pipeline_history":
                history = state.get(key, [])
                state[key] = history + value
            elif isinstance(value, list):
                existing = state.get(key)
                if isinstance(existing, list):
                    state[key] = existing + value
                else:
                    state[key] = list(value)
            elif isinstance(value, dict):
                existing = state.get(key)
                if isinstance(existing, dict):
                    merged = existing.copy()
                    merged.update(value)
                    state[key] = merged
                else:
                    state[key] = dict(value)
            else:
                state[key] = value
        return state

    def compile(self):
        graph = self

        class DummyCompiledGraph:
            def stream(self_inner, inputs):
                state = dict(inputs)
                current = graph.entry_point

                while current is not None and current is not END:
                    node_fn = graph.nodes[current]
                    output = node_fn(state) or {}
                    DummyStateGraph._merge_state(state, output)
                    yield {current: output}

                    if current in graph.conditional_edges:
                        condition, mapping = graph.conditional_edges[current]
                        branch = condition(state)
                        next_node = mapping.get(branch)
                    else:
                        next_nodes = graph.edges.get(current, [])
                        next_node = next_nodes[0] if next_nodes else None

                    if next_node is END or next_node is None:
                        break

                    current = next_node

        return DummyCompiledGraph()


class DummyVerifier:
    def __init__(self):
        self.last_fen = None

    def parse_fen(self, fen):
        self.last_fen = fen

    def verify_piece_position(self, response):
        return f"position::{response}"

    def verify_piece_relation(self, response):
        return f"relation::{response}"

    def verify_piece_move_feature(self, response):
        return f"feature::{response}"


class DummyBuilder:
    def build_relations(self, text):
        return f"built::{text}"


def dummy_generate_response(**kwargs):
    return {"response": kwargs}


END = object()


@pytest.fixture()
def pipeline_module(monkeypatch):
    fake_streamlit = types.SimpleNamespace(secrets={"GROQ_API_KEY": "dummy"})
    monkeypatch.setitem(sys.modules, "streamlit", fake_streamlit)
    monkeypatch.setitem(
        sys.modules, "langchain_groq", make_module("langchain_groq", ChatGroq=lambda **_: None)
    )
    monkeypatch.setitem(
        sys.modules,
        "langchain_google_genai",
        make_module("langchain_google_genai", ChatGoogleGenerativeAI=lambda **_: None),
    )
    monkeypatch.setitem(
        sys.modules,
        "langchain.prompts",
        make_module("langchain.prompts", PromptTemplate=DummyPromptTemplate),
    )
    monkeypatch.setitem(
        sys.modules,
        "langchain.agents",
        make_module(
            "langchain.agents",
            Tool=DummyTool,
            AgentExecutor=DummyAgentExecutor,
            create_react_agent=dummy_create_react_agent,
        ),
    )
    monkeypatch.setitem(
        sys.modules,
        "langchain_core.agents",
        make_module(
            "langchain_core.agents",
            AgentAction=DummyAgentAction,
            AgentFinish=DummyAgentFinish,
        ),
    )
    monkeypatch.setitem(
        sys.modules,
        "langgraph.graph",
        make_module("langgraph.graph", StateGraph=DummyStateGraph, END=END),
    )
    monkeypatch.setitem(
        sys.modules,
        "neurosymbolicAI",
        make_module("neurosymbolicAI", Verifier=DummyVerifier, Builder=DummyBuilder),
    )
    monkeypatch.setitem(
        sys.modules,
        "reinforced_agent",
        make_module("reinforced_agent", generate_response=dummy_generate_response),
    )

    module = importlib.import_module("server.pipeline")
    yield module
    sys.modules.pop("server.pipeline", None)


def test_main_prompt_mentions_known_agents(pipeline_module):
    template = pipeline_module.main_prompt.template
    assert "Reinforced Agent" in template
    assert "Builder Agent" in template


def test_main_tools_invoke_expected_helpers(pipeline_module):
    reinforce_tool, builder_tool = pipeline_module.main_tools
    commentary_state = {"input": "comment", "status": "Reinforced Agent"}
    build_state = {"input": "relation spec", "status": "Builder Agent"}

    commentary_result = reinforce_tool.func(commentary_state)
    builder_result = builder_tool.func(build_state)

    assert "commentary_agent_outcome" in commentary_result
    assert commentary_result["commentary_agent_outcome"]["response"]["prompt"] == "comment"

    assert builder_result["status"] in {"End", "N/A"}


def test_selection_checkpoint_routes_by_history(pipeline_module):
    build_state = {"pipeline_history": [("Main Agent", "Builder Agent")]}
    comment_state = {"pipeline_history": [("Main Agent", "Reinforced Agent")]}
    end_state = {"pipeline_history": [("Main Agent", "N/A")]}

    assert pipeline_module.selection_checkpoint(build_state) == "build"
    assert pipeline_module.selection_checkpoint(comment_state) == "comment"
    assert pipeline_module.selection_checkpoint(end_state) == "end"


def test_should_continue_handles_status_transitions(pipeline_module):
    assert pipeline_module.should_continue({"status": "End"}) == "end"
    assert pipeline_module.should_continue({"status": "Reflex"}) == "reflex"
    assert pipeline_module.should_continue({"status": "Verify Piece Position"}) == "end"


def test_execute_tools_dispatches_based_on_status(pipeline_module, monkeypatch):
    calls = []

    def fake_pos(state):
        calls.append(("pos", state["status"]))
        return {"status": "End"}

    def fake_rel(state):
        calls.append(("rel", state["status"]))
        return {"status": "End"}

    def fake_move(state):
        calls.append(("move", state["status"]))
        return {"status": "End"}

    monkeypatch.setattr(pipeline_module, "verify_piece_position", fake_pos)
    monkeypatch.setattr(pipeline_module, "verify_piece_relation", fake_rel)
    monkeypatch.setattr(pipeline_module, "verify_move_relation", fake_move)

    base_state = {
        "fen": "fen",
        "commentary_agent_outcome": "text",
        "verifier_agent_outcome": "tool",
    }

    pipeline_module.execute_tools({**base_state, "status": "Verify Piece Position"})
    pipeline_module.execute_tools({**base_state, "status": "Verify Piece Relation"})
    pipeline_module.execute_tools({**base_state, "status": "Verify Piece Move Feature"})

    assert calls == [
        ("pos", "Verify Piece Position"),
        ("rel", "Verify Piece Relation"),
        ("move", "Verify Piece Move Feature"),
    ]


def test_run_main_uses_agent_executor_output(pipeline_module):
    pipeline_module.main_agent_runnable.output = "Builder Agent"
    result = pipeline_module.run_main({"input": "please build"})

    assert result["status"] == "Builder Agent"
    assert result["pipeline_history"] == [("Main Agent", "Builder Agent")]


def test_run_verifier_passthroughs_agent_choice(pipeline_module):
    pipeline_module.verifier_agent_runnable.output = "Verify Piece Position"
    state = {"commentary_agent_outcome": "analysis", "status": "Reinforced Agent"}

    result = pipeline_module.run_verifier(state)

    assert result["verifier_agent_outcome"] == "Verify Piece Position"
    assert result["status"] == "Verify Piece Position"
    assert result["pipeline_history"] == [("Tiny Agent", "Verify Piece Position")]


def test_chat_happy_path_runs_pipeline(pipeline_module, monkeypatch):
    pipeline_module.main_agent_runnable.output = "Reinforced Agent"
    pipeline_module.verifier_agent_runnable.output = "Verify Piece Position"

    commentary_calls = []

    def fake_generate_response(prompt, feedback=None):
        commentary_calls.append({"prompt": prompt, "feedback": feedback})
        return "The white rook at a1 defends white pawn at a2."

    monkeypatch.setattr(pipeline_module, "generate_response", fake_generate_response)

    def fake_verify_piece_position(state):
        assert state["fen"] == "integration fen"
        assert state["status"] == "Verify Piece Position"
        assert state["commentary_agent_outcome"] == "The white rook at a1 defends white pawn at a2."
        return {
            "pipeline_history": [
                (
                    state["verifier_agent_outcome"],
                    [{"statement": "The white rook at a1 defends white pawn at a2.", "condition": True}],
                )
            ]
        }

    monkeypatch.setattr(pipeline_module, "verify_piece_position", fake_verify_piece_position)

    result = pipeline_module.chat("Does the rook defend a2?", "integration fen")

    assert result == "The white rook at a1 defends white pawn at a2."
    assert commentary_calls == [{"prompt": "Does the rook defend a2?", "feedback": None}]
