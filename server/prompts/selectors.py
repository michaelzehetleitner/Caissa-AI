"""LangGraph selector prompt text sourced from the original inline definitions."""

from __future__ import annotations

from pathlib import Path

from .placeholders import (
    apply_interaction_placeholders,
    apply_relationship_placeholders,
    apply_tool_placeholders,
    build_router_examples_block,
)

_TEXT_DIR = Path(__file__).with_name("text")


def _load_text(filename: str) -> str:
    path = _TEXT_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing selector prompt text file: {path}")
    return path.read_text()


def _inject_examples(text: str, placeholder: str, examples: list[tuple[str, str]]) -> str:
    block = build_router_examples_block(examples)
    token = placeholder
    search = f"{token}"
    idx = text.index(search)
    line_start = text.rfind("\n", 0, idx) + 1
    indent = text[line_start:idx]
    indented_block = "\n".join(
        f"{indent}{line}" if line else indent for line in block.splitlines()
    )
    return text.replace(f"{indent}{token}", indented_block, 1)


_main_text = _load_text("pipeline_main_prompt.txt")
_main_examples = [
    ("Please give me a commentary for the move of white rook from a1 to a8.", "Reinforced Agent"),
    ("What is the position of the black queen?", "Reinforced Agent"),
    ("## Example 3", "What does the white knight defend?", "Reinforced Agent"),
    ("A move_threat_and_defend is a feature of a move that defend an ally piece and attack an opponent piece.", "Builder Agent"),
]
_main_text = _inject_examples(_main_text, "<<ROUTER_EXAMPLES_BLOCK>>", _main_examples)
_main_text = apply_tool_placeholders(_main_text)
_main_text = apply_interaction_placeholders(_main_text)
PIPELINE_MAIN_PROMPT = _main_text

_verifier_text = _load_text("pipeline_verifier_prompt.txt")
_verifier_examples = [
    ("The position of black queen is a2.", "Verify Piece Position"),
    ("### Example 2 ", "I am sorry I can't answer the question.", "N/A"),
    ("The black rook move from c3 to h3 is attacked by white rook at h1.", "Verify Piece Move Feature"),
]
_verifier_text = _inject_examples(_verifier_text, "<<ROUTER_EXAMPLES_BLOCK>>", _verifier_examples)
_verifier_text = apply_relationship_placeholders(_verifier_text)
_verifier_text = apply_tool_placeholders(_verifier_text)
_verifier_text = apply_interaction_placeholders(_verifier_text)
PIPELINE_VERIFIER_PROMPT = _verifier_text

__all__ = ["PIPELINE_MAIN_PROMPT", "PIPELINE_VERIFIER_PROMPT"]
