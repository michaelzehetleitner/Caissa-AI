from __future__ import annotations

from typing import List, Tuple
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from server import server as server_module  # noqa: E402


class FakeSymbolic:
    instances: List["FakeSymbolic"] = []

    def __init__(self) -> None:
        self.consult_calls = 0
        self.parse_calls = 0
        FakeSymbolic.instances.append(self)

    def consult(self, filepath: str) -> None:
        self.consult_calls += 1

    def parse_fen(self, fen_string: str) -> None:
        self.parse_calls += 1


def _patch_execute_tactic(monkeypatch):
    def _exec(method, color, description, filepath, fen_string, symbolic_instance=None):
        method(symbolic_instance, color)

    monkeypatch.setattr(server_module, "execute_tactic", _exec)


@pytest.fixture(autouse=True)
def _reset_fake_symbolic():
    FakeSymbolic.instances.clear()
    yield
    FakeSymbolic.instances.clear()


def test_add_tactics_constructs_symbolic_when_none_provided(monkeypatch):
    monkeypatch.setattr(server_module, "Symbolic", FakeSymbolic)
    _patch_execute_tactic(monkeypatch)

    tactic_calls: List[Tuple[int, str]] = []

    def fake_tactic(symbolic, color):
        tactic_calls.append((id(symbolic), color))

    tactics = [
        (fake_tactic, "white", "fake"),
        (fake_tactic, "black", "fake"),
    ]

    server_module.add_tactics_to_graph("kb.pl", "fen-string", tactics=tactics)

    assert len(FakeSymbolic.instances) == 1
    instance = FakeSymbolic.instances[0]
    assert instance.consult_calls == 1
    # parse_fen is called once before the loop and once per tactic
    assert instance.parse_calls == 1 + len(tactics)
    # both tactics should have received the same instance
    assert len({call[0] for call in tactic_calls}) == 1


def test_add_tactics_reuses_provided_symbolic(monkeypatch):
    monkeypatch.setattr(server_module, "Symbolic", FakeSymbolic)
    _patch_execute_tactic(monkeypatch)

    shared = FakeSymbolic()

    tactic_calls: List[int] = []

    def fake_tactic(symbolic, color):
        tactic_calls.append(id(symbolic))

    tactics = [
        (fake_tactic, "white", "fake"),
        (fake_tactic, "white", "fake-2"),
    ]

    server_module.add_tactics_to_graph(
        "kb.pl",
        "fen-string",
        symbolic_instance=shared,
        tactics=tactics,
    )

    # No new instances should be created beyond the shared one we made
    assert FakeSymbolic.instances == [shared]
    # consult should not be invoked on a provided instance
    assert shared.consult_calls == 0
    assert shared.parse_calls == 1 + len(tactics)
    assert all(call == id(shared) for call in tactic_calls)
