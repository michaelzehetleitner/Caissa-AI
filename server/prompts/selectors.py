"""LangGraph selector prompt text sourced from the original inline definitions."""

from __future__ import annotations

from pathlib import Path

from .placeholders import apply_relationship_placeholders

_TEXT_DIR = Path(__file__).with_name("text")


def _load_text(filename: str) -> str:
    path = _TEXT_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing selector prompt text file: {path}")
    return path.read_text()


PIPELINE_MAIN_PROMPT = _load_text("pipeline_main_prompt.txt")
PIPELINE_VERIFIER_PROMPT = apply_relationship_placeholders(_load_text("pipeline_verifier_prompt.txt"))

__all__ = ["PIPELINE_MAIN_PROMPT", "PIPELINE_VERIFIER_PROMPT"]
