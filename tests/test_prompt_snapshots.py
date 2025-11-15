from __future__ import annotations

from importlib import import_module
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = REPO_ROOT / "tests" / "prompt_snapshots"

PROMPT_CASES = [
    ("server.prompts.agents", "CLASSIC_AGENT_PROMPT", "agent_prompt.txt"),
    ("server.prompts.agents", "REINFORCED_AGENT_PROMPT", "reinforced_agent_prompt.txt"),
    ("server.prompts.agents", "BUILDER_AGENT_PROMPT", "builder_agent_prompt.txt"),
    ("server.prompts.agents", "VERIFIER_JSON_PROMPT", "verifier_agent_prompt.txt"),
    ("server.prompts.agents", "VERIFIER_FIX_PROMPT", "verifier_fix_prompt.txt"),
    ("server.prompts.selectors", "PIPELINE_MAIN_PROMPT", "pipeline_main_prompt.txt"),
    ("server.prompts.selectors", "PIPELINE_VERIFIER_PROMPT", "pipeline_verifier_prompt.txt"),
    ("server.prompts.tools", "CYPHER_GENERATION_TEMPLATE", "cypher_template.txt"),
]


@pytest.mark.parametrize("module_path, attr, snapshot_name", PROMPT_CASES)
def test_prompt_snapshots_match(module_path: str, attr: str, snapshot_name: str) -> None:
    snapshot_path = SNAPSHOT_DIR / snapshot_name
    assert snapshot_path.exists(), f"missing snapshot for {module_path}:{attr}"

    module = import_module(module_path)
    current_prompt = getattr(module, attr)
    expected_prompt = snapshot_path.read_text()

    assert current_prompt == expected_prompt, (
        f"Prompt mismatch for {module_path}:{attr}. "
        f"Run `python3 scripts/update_prompt_snapshots.py` after intentional edits."
    )
