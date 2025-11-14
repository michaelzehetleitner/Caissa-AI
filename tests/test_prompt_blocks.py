from __future__ import annotations

import importlib
from pathlib import Path
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _block_text(filename: str) -> str:
    return (REPO_ROOT / "server" / "prompts" / filename).read_text()


@pytest.mark.parametrize(
    "prompt_attr",
    [
        "CLASSIC_AGENT_PROMPT",
        "REINFORCED_AGENT_PROMPT",
    ],
)
def test_agent_prompts_include_shared_examples_and_guidance(prompt_attr: str) -> None:
    agents = importlib.import_module("server.prompts.agents")
    prompt_text = getattr(agents, prompt_attr)
    examples_block = _block_text("agent_examples.txt")
    guidance_block = _block_text("agent_guidance.txt")
    assert examples_block in prompt_text
    assert guidance_block in prompt_text


def test_builder_prompt_includes_shared_context_block() -> None:
    agents = importlib.import_module("server.prompts.agents")
    prompt_text = agents.BUILDER_AGENT_PROMPT
    block = agents.BUILDER_CONTEXT_AND_TOOL_BLOCK  # reuse exported constant
    assert block in prompt_text


def test_verifier_prompts_include_shared_tool_instructions() -> None:
    agents = importlib.import_module("server.prompts.agents")
    tool_block = agents.INDENTED_TOOL_BLOCK
    assert tool_block in agents.VERIFIER_JSON_PROMPT
    assert tool_block in agents.VERIFIER_FIX_PROMPT


@pytest.mark.parametrize(
    "prompt_attr",
    ["VERIFIER_JSON_PROMPT", "VERIFIER_FIX_PROMPT"],
)
def test_verifier_prompts_remain_tool_free(prompt_attr: str) -> None:
    agents = importlib.import_module("server.prompts.agents")
    prompt_text = getattr(agents, prompt_attr)
    assert "Do not use any tool" in prompt_text


def test_builder_prompt_lists_complete_piece_metadata() -> None:
    agents = importlib.import_module("server.prompts.agents")
    prompt_text = agents.BUILDER_AGENT_PROMPT
    required_snippets = [
        "[king, queen, knight, bishop, rook, pawn]",
        "[black, white]",
        "a1, a2, a3, a4",
        "h5, h6, h7, h8",
    ]
    for snippet in required_snippets:
        assert snippet in prompt_text
