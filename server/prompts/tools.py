"""Tool-specific prompt templates backed by text files."""

from __future__ import annotations

from pathlib import Path

from .placeholders import apply_relationship_placeholders

_TEXT_DIR = Path(__file__).with_name("text")


def _load_text(filename: str) -> str:
    path = _TEXT_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing tool prompt text file: {path}")
    return path.read_text()


CYPHER_GENERATION_TEMPLATE = apply_relationship_placeholders(
    _load_text("cypher_generation_template.txt")
)

__all__ = ["CYPHER_GENERATION_TEMPLATE"]
