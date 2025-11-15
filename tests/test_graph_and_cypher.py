from __future__ import annotations

import importlib
import sys
import types
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _reload_graph(monkeypatch, *, neo4j_cls):
    fake_config = types.ModuleType("server.config")
    fake_config.get_secret = lambda key, default=None: f"{key}_value"
    monkeypatch.setitem(sys.modules, "server.config", fake_config)

    fake_lc_module = types.ModuleType("langchain_community.graphs.neo4j_graph")
    fake_lc_module.Neo4jGraph = neo4j_cls
    monkeypatch.setitem(
        sys.modules,
        "langchain_community.graphs.neo4j_graph",
        fake_lc_module,
    )

    sys.modules.pop("server.graph", None)
    return importlib.import_module("server.graph")


def _reload_cypher(monkeypatch, *, graph_obj, graph_error=None):
    langchain_pkg = sys.modules.get("langchain")
    if langchain_pkg is None:
        langchain_pkg = types.ModuleType("langchain")
        monkeypatch.setitem(sys.modules, "langchain", langchain_pkg)

    prompts_pkg = types.ModuleType("langchain.prompts")
    monkeypatch.setitem(sys.modules, "langchain.prompts", prompts_pkg)
    setattr(langchain_pkg, "prompts", prompts_pkg)

    prompt_module = types.ModuleType("langchain.prompts.prompt")

    class StubPromptTemplate:
        def __init__(self, template):
            self.template = template

        @classmethod
        def from_template(cls, template):
            return cls(template)

    prompt_module.PromptTemplate = StubPromptTemplate
    monkeypatch.setitem(sys.modules, "langchain.prompts.prompt", prompt_module)
    setattr(prompts_pkg, "prompt", prompt_module)

    fake_graph_module = types.ModuleType("server.graph")
    fake_graph_module.graph = graph_obj
    fake_graph_module.GRAPH_ERROR = graph_error
    monkeypatch.setitem(sys.modules, "server.graph", fake_graph_module)

    fake_llama = types.ModuleType("server.llama_llm")
    fake_llama.llm = object()
    monkeypatch.setitem(sys.modules, "server.llama_llm", fake_llama)

    fake_prompts = types.ModuleType("server.prompts")
    fake_prompts.CYPHER_GENERATION_TEMPLATE = "{question}"
    monkeypatch.setitem(sys.modules, "server.prompts", fake_prompts)

    class FakeGraphChain:
        instances: list["FakeGraphChain"] = []

        def __init__(self, llm, graph, **kwargs):
            self.llm = llm
            self.graph = graph
            self.kwargs = kwargs
            self.invocations: list[object] = []
            FakeGraphChain.instances.append(self)

        @classmethod
        def from_llm(cls, llm, graph, **kwargs):
            return cls(llm, graph, **kwargs)

        def invoke(self, question):
            self.invocations.append(question)
            return {"result": "ok", "context": ["ctx"]}

    fake_chain_module = types.ModuleType(
        "langchain_community.chains.graph_qa.cypher"
    )
    fake_chain_module.GraphCypherQAChain = FakeGraphChain
    monkeypatch.setitem(
        sys.modules,
        "langchain_community.chains.graph_qa.cypher",
        fake_chain_module,
    )

    sys.modules.pop("server.tools.cypher", None)
    module = importlib.import_module("server.tools.cypher")
    return module, FakeGraphChain


def test_graph_initialization_captures_error(monkeypatch):
    class ExplodingGraph:
        def __init__(self, *_, **__):
            raise RuntimeError("boom")

    graph_module = _reload_graph(monkeypatch, neo4j_cls=ExplodingGraph)

    assert graph_module.graph is None
    assert isinstance(graph_module.GRAPH_ERROR, RuntimeError)


def test_graph_successfully_creates_driver(monkeypatch):
    class DummyGraph:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

    graph_module = _reload_graph(monkeypatch, neo4j_cls=DummyGraph)

    assert isinstance(graph_module.graph, DummyGraph)
    assert graph_module.GRAPH_ERROR is None
    assert graph_module.graph.kwargs["url"] == "NEO4J_URI_value"


def test_cypher_qa_invokes_underlying_chain(monkeypatch):
    cypher_module, chain_cls = _reload_cypher(
        monkeypatch,
        graph_obj=object(),
        graph_error=None,
    )
    question = {"prompt": "test"}

    result = cypher_module.cypher_qa(question)

    assert result["result"] == "ok"
    assert chain_cls.instances[-1].invocations == [question]


def test_cypher_qa_raises_when_graph_missing(monkeypatch):
    graph_error = RuntimeError("neo4j unreachable")
    cypher_module, _ = _reload_cypher(
        monkeypatch,
        graph_obj=None,
        graph_error=graph_error,
    )

    with pytest.raises(RuntimeError) as excinfo:
        cypher_module.cypher_qa("irrelevant")

    assert "Neo4j graph connection failed" in str(excinfo.value)
    assert excinfo.value.__cause__ is graph_error
