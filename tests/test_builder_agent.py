import importlib

import pytest


@pytest.fixture
def builder_module(monkeypatch):
    module = importlib.reload(importlib.import_module("server.neurosymbolicAI.builder_ai"))

    class DummyGraph:
        def __init__(self):
            self.relation_moves = {}
            self.find_calls = []
            self.build_feature_calls = []

        def find_moves(self, relation_name):
            self.find_calls.append(relation_name)
            return self.relation_moves.get(relation_name, [])

        def build_feature(self, piece, color, from_position, to_position, feature_name):
            self.build_feature_calls.append((piece, color, from_position, to_position, feature_name))

    class DummySymbolic:
        def __init__(self):
            self.graph = DummyGraph()

        def consult(self, path):
            self.kb_path = path

    class FakeLLM:
        def __init__(self, *args, **kwargs):
            self.kwargs = kwargs

    class FakePromptTemplate:
        @classmethod
        def from_template(cls, template):
            return template

    def fake_create_agent(llm, tools, prompt):
        def _agent(payload):
            return {"output": payload.get("input", "")}

        return _agent

    class FakeAgentExecutor:
        def __init__(self, agent, tools, **kwargs):
            self.agent = agent

        def invoke(self, inputs):
            return self.agent(inputs)

    class RecordingParser:
        def __init__(self, *args, **kwargs):
            self.calls = []

        def parse(self, text):
            self.calls.append(text)
            return {}

    monkeypatch.setattr(module, "Symbolic", DummySymbolic)
    monkeypatch.setattr(module, "ChatOpenAI", FakeLLM)
    monkeypatch.setattr(module, "PromptTemplate", FakePromptTemplate)
    monkeypatch.setattr(module, "create_react_agent", fake_create_agent)
    monkeypatch.setattr(module, "AgentExecutor", FakeAgentExecutor)
    monkeypatch.setattr(module, "JsonOutputParser", RecordingParser)

    return module


def test_build_relations_uses_json_parser_and_populates_graph(builder_module):
    builder = builder_module.Builder()

    shared_moves = [
        {"piece": "knight", "color": "white", "from": "g5", "to": "e4"},
        {"piece": "knight", "color": "white", "from": "g5", "to": "e4"},
    ]
    builder.sym.graph.relation_moves = {
        "fork_line_a": list(shared_moves),
        "fork_line_b": list(shared_moves),
    }

    structured_payload = {
        "name": "Fork Finder",
        "relationships": {"relation_1": "fork_line_a", "relation_2": "fork_line_b"},
    }
    parser_calls = []

    def parse_override(text):
        parser_calls.append(text)
        return structured_payload

    builder.parser.parse = parse_override

    def unexpected_fallback(_):
        raise AssertionError("Builder should rely on JsonOutputParser.parse instead of manual JSON hacks.")

    builder._load_structured_response = unexpected_fallback

    built = []

    def record_build_feature(piece, color, from_pos, to_pos, feature_name):
        built.append((piece, color, from_pos, to_pos, feature_name))

    builder.sym.graph.build_feature = record_build_feature
    builder.extract_relations = lambda description: {"output": "unused"}

    try:
        builder.build_relations("Add a fork feature")
    except AssertionError as exc:
        pytest.fail(str(exc))

    assert built, "Builder must materialize parsed moves via graph.build_feature"
    assert parser_calls, "Builder must parse the agent output with JsonOutputParser.parse"
