from __future__ import annotations

import json
import sys
from importlib import import_module
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
GOLDEN_PATH = REPO_ROOT / "tests" / "golden_prompts" / "prompts.json"
GOLDEN_PAYLOAD = json.loads(GOLDEN_PATH.read_text())
GOLDEN_DATA = GOLDEN_PAYLOAD.get("prompts", {})


def _normalize_prompt(text: str) -> str:
    """Loosen comparisons to ignore trailing spaces and repeated blank lines."""

    lines = [line.rstrip() for line in text.strip().splitlines()]
    normalized: list[str] = []
    previous_blank = False
    for line in lines:
        if not line:
            if previous_blank:
                continue
            previous_blank = True
        else:
            previous_blank = False
        normalized.append(line)
    return "\n".join(normalized)

PROMPT_CASES = [
    ("server.prompts.agents", "CLASSIC_AGENT_PROMPT", "server.agent.agent_prompt"),
    ("server.prompts.agents", "REINFORCED_AGENT_PROMPT", "server.reinforced_agent.agent_prompt"),
    ("server.prompts.agents", "BUILDER_AGENT_PROMPT", "server.neurosymbolicAI.builder.agent_prompt"),
    ("server.prompts.agents", "VERIFIER_JSON_PROMPT", "server.neurosymbolicAI.verifier.agent_prompt"),
    ("server.prompts.agents", "VERIFIER_FIX_PROMPT", "server.neurosymbolicAI.verifier.fix_agent_prompt"),
    ("server.prompts.selectors", "PIPELINE_MAIN_PROMPT", "server.pipeline.main_prompt"),
    ("server.prompts.selectors", "PIPELINE_VERIFIER_PROMPT", "server.pipeline.verifier_prompt"),
    (
        "server.prompts.tools",
        "CYPHER_GENERATION_TEMPLATE",
        "server.tools.cypher.CYPHER_GENERATION_TEMPLATE",
    ),
]


@pytest.mark.parametrize("module_path, attr, golden_id", PROMPT_CASES)
def test_prompts_match_golden_master(module_path: str, attr: str, golden_id: str) -> None:
    golden_entry = GOLDEN_DATA.get(golden_id)
    assert golden_entry is not None, f"Missing golden entry for {golden_id}"

    module = import_module(module_path)
    current_text = getattr(module, attr)
    assert _normalize_prompt(current_text) == _normalize_prompt(
        golden_entry["text"]
    ), f"{module_path}:{attr} diverged from golden master {golden_id}"
