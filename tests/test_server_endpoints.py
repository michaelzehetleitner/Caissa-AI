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


class DummySymbolicRuntime:
    def __init__(self):
        self.legal_moves_result = ["a2a4"]
        self.make_move_result = (["ok"], ["board"])
        self.board = [["init"]]
        self.construct_graph_calls = 0
        self.parse_history = []
        self.legal_moves_calls = []
        self.make_move_calls = []
        self.update_history = []

    def parse_fen(self, fen):
        self.parse_history.append(fen)

    def legal_moves(self, piece, color, position):
        self.legal_moves_calls.append((piece, color, position))
        return list(self.legal_moves_result)

    def display_board_cli(self):
        pass

    def make_move(self, piece, color, from_position, to_position):
        self.make_move_calls.append((piece, color, from_position, to_position))
        return self.make_move_result

    def construct_graph(self):
        self.construct_graph_calls += 1

    def update_board(self, fen):
        self.update_history.append(fen)
        self.board = [[fen]]

    def get_board(self):
        return self.board


def _noop(*_args, **_kwargs):
    return None


class DummySymbolic:
    def consult(self, filepath):
        self.last_consult = filepath

    def parse_fen(self, fen):
        self.last_fen = fen


for attr in [
    "mate",
    "create_fork_relation",
    "create_absolute_pin_relation",
    "create_relative_pin_relation",
    "create_skewer_relation",
    "create_discovery_attack_relation",
    "hanging_piece",
    "create_interference_relation",
    "create_mate_in_two_relation",
    "defend",
    "threat",
    "move_defend",
    "move_threat",
    "protected_move",
    "attacked_move",
]:
    setattr(DummySymbolic, attr, staticmethod(_noop))


@pytest.fixture()
def server_module(monkeypatch):
    symbolic_runtime = DummySymbolicRuntime()

    class DummyNeuroSymbolic:
        def __init__(self):
            self.symbolic = symbolic_runtime
            self.suggest_calls = []

        def suggest(self, **kwargs):
            self.suggest_calls.append(kwargs)
            return f"suggest::{kwargs.get('fen_string')}"

    neuro_module = make_module("neurosymbolicAI", NeuroSymbolic=DummyNeuroSymbolic)
    symbolic_ai_module = make_module("neurosymbolicAI.symbolicAI.symbolic_ai", Symbolic=DummySymbolic)
    symbolic_ai_pkg = make_module("neurosymbolicAI.symbolicAI", symbolic_ai=symbolic_ai_module)
    setattr(neuro_module, "symbolicAI", symbolic_ai_pkg)

    monkeypatch.setitem(sys.modules, "neurosymbolicAI", neuro_module)
    monkeypatch.setitem(sys.modules, "neurosymbolicAI.symbolicAI", symbolic_ai_pkg)
    monkeypatch.setitem(sys.modules, "neurosymbolicAI.symbolicAI.symbolic_ai", symbolic_ai_module)

    agent_calls = []

    def fake_generate_response(prompt):
        agent_calls.append(prompt)
        return f"agent::{prompt}"

    monkeypatch.setitem(sys.modules, "agent", make_module("agent", generate_response=fake_generate_response))

    chat_calls = []

    def fake_chat(*, input, fen_string):
        chat_calls.append({"input": input, "fen": fen_string})
        return f"chat::{input}::{fen_string}"

    monkeypatch.setitem(sys.modules, "pipeline", make_module("pipeline", chat=fake_chat))

    module = importlib.import_module("server.server")

    add_calls = []

    def fake_add_tactics(*args, **kwargs):
        add_calls.append((args, kwargs))

    monkeypatch.setattr(module, "add_tactics_to_graph", fake_add_tactics)

    yield {
        "module": module,
        "symbolic": symbolic_runtime,
        "agent_calls": agent_calls,
        "chat_calls": chat_calls,
        "add_calls": add_calls,
    }

    sys.modules.pop("server.server", None)


def test_get_legal_moves_returns_moves(server_module):
    module = server_module["module"]
    symbolic = server_module["symbolic"]
    symbolic.legal_moves_result = ["a2a4", "a2a3"]

    client = module.app.test_client()
    response = client.get(
        "/legal_moves", query_string={"piece": "pawn", "color": "white", "position": "a2"}
    )

    assert response.status_code == 200
    assert response.get_json() == {"legal_moves": ["a2a4", "a2a3"]}
    assert symbolic.legal_moves_calls[-1] == ("pawn", "white", "a2")


def test_reinforced_chatbot_proxies_prompt(server_module):
    module = server_module["module"]
    client = module.app.test_client()

    response = client.post("/reinforced_chatbot", json={"prompt": "hello", "fen": "fen"})

    assert response.status_code == 200
    assert response.get_json() == {"answer": "chat::hello::fen"}
    assert server_module["chat_calls"] == [{"input": "hello", "fen": "fen"}]


def test_chatbot_endpoint_uses_agent(server_module):
    module = server_module["module"]
    client = module.app.test_client()

    response = client.post("/chatbot", json={"prompt": "describe"})

    assert response.status_code == 200
    assert response.get_json() == {"answer": "agent::describe"}
    assert server_module["agent_calls"] == ["describe"]


def test_neurosym_endpoint_calls_suggest(server_module):
    module = server_module["module"]
    client = module.app.test_client()

    response = client.post("/neurosym", json={"fen": "custom fen"})

    assert response.status_code == 200
    assert response.get_json() == {"answer": "suggest::custom fen"}
    assert module.ns.symbolic.parse_history[-1] == "custom fen"
    assert module.ns.suggest_calls[-1]["fen_string"] == "custom fen"


def test_make_move_executes_graph_when_move_succeeds(server_module):
    module = server_module["module"]
    symbolic = server_module["symbolic"]
    symbolic.make_move_result = (["ok"], ["rendered board"])

    client = module.app.test_client()
    request_body = {
        "fen_string": "fen",
        "piece": "rook",
        "color": "white",
        "from_position": "a1",
        "to_position": "a8",
        "promotion": "",
    }

    response = client.post("/make_move", json=request_body)

    assert response.status_code == 200
    assert response.get_json() == {"move_status": True, "new_board": ["rendered board"]}
    assert symbolic.make_move_calls[-1] == ("rook", "white", "a1", "a8")
    assert symbolic.construct_graph_calls == 1
    assert server_module["add_calls"][-1][0] == (module.KB_PATH, "fen")


def test_set_fen_returns_updated_board(server_module):
    module = server_module["module"]
    symbolic = server_module["symbolic"]

    client = module.app.test_client()
    response = client.post("/set_fen", json={"fen_string": "board fen"})

    assert response.status_code == 200
    assert response.get_json() == {"board": [["board fen"]]}
    assert symbolic.update_history[-1] == "board fen"
    assert server_module["add_calls"][-1][0] == (module.KB_PATH, "board fen")
