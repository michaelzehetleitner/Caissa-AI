"""Agent prompt text loaded from the original inline definitions."""

from __future__ import annotations

from pathlib import Path

from .placeholders import (
    _replace_once,
    apply_json_placeholders,
    apply_relationship_placeholders,
    apply_tool_placeholders,
    apply_interaction_placeholders,
)

_TEXT_DIR = Path(__file__).with_name("text")


def _load_text(filename: str) -> str:
    path = _TEXT_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing prompt text file: {path}")
    return path.read_text()


def _remove_line(text: str, line: str) -> str:
    """Remove the first occurrence of ``line`` from ``text``."""

    if line not in text:
        raise ValueError(f"Expected line {line!r} not found in prompt")
    return text.replace(line, "", 1)


def _replace_section(text: str, start_marker: str, end_marker: str, replacement: str = "") -> str:
    """Replace the text between ``start_marker`` and ``end_marker`` (exclusive)."""

    try:
        start = text.index(start_marker)
        end = text.index(end_marker, start)
    except ValueError as exc:  # pragma: no cover - defensive guard for prompt drift
        raise ValueError(
            f"Unable to find prompt section between {start_marker!r} and {end_marker!r}"
        ) from exc
    return text[:start] + replacement + text[end:]


def _build_reinforced_agent_prompt(base_prompt: str) -> str:
    """Derive the reinforced prompt from the classic prompt to avoid duplication."""

    prompt = base_prompt

    # Remove classic-only elements.
    prompt = _remove_line(prompt, '    Your name is "Caïssa".\n')
    prompt = _remove_line(prompt, "    You must follow all steps\n")
    prompt = _replace_section(
        prompt,
        '\n    7. {{tactic_name: "fork"}}',
        '\n\n    # Tone',
    )
    prompt = _replace_once(prompt, '\n\n    # Tone', '\n\n\n    # Tone')
    prompt = _replace_once(
        prompt,
        '    Use the tone of a chess expert commentary and explain things in a clear way that anyone can understand\n    \n',
        '    Use the tone of a chess expert commentary and explain things in a clear way that anyone can understand\n    \n    \n',
    )
    prompt = _replace_section(
        prompt,
        '\n    ### Example 10',
        '\n    # How to Process Tool Output',
    )
    prompt = _replace_once(
        prompt,
        '  \n    # How to Process Tool Output',
        '    \n    # How to Process Tool Output',
    )
    prompt = _replace_section(
        prompt,
        '\n    # How to answer question related to provide or tell the tactics that support a move:',
        '\n    # Notes',
    )
    prompt = _remove_line(prompt, "        18. You must follow all steps\n")

    # Apply the text quirks that are unique to the reinforced prompt.
    prompt = _replace_once(
        prompt,
        '        Note: If you do not know {{color}} or {{old position}} or {{new position}} then replace it with <unknown> word.\n',
        '        Note: If you do not know {{color}} or {{old position}} or {{new position}} then replace it with <unknown> word\n',
    )
    prompt = _replace_once(
        prompt,
        '        d. I am going to answer Question (d) in step 3',
        '        d. I am going to answer Question (c) in step 3',
    )
    prompt = _replace_once(
        prompt,
        '        e. I am going to answer Question (e) in step 3',
        '        e. I am going to answer Question (c) in step 3',
    )
    prompt = _replace_once(
        prompt,
        '        f. I am going to answer Question (f) in step 3',
        '        f. I am going to answer Question (c) in step 3',
    )

    # Insert the feedback block that only exists in the reinforced prompt.
    prompt = _replace_once(
        prompt,
        '\n    # Notes',
        '\n    \n    # Feedback\n    {feedback}\n        \n    # Notes',
    )
    prompt = _replace_once(prompt, '  \n    \n    # Feedback', '\n    \n    # Feedback')

    prompt = _replace_once(
        prompt,
        "        Observation: {{'context': [{{piece_old_position: h6, piece_new_position: h8, opponent_piece: rook, opponent_color: white, opponent_position: a8}}]}}\n",
        "        Observation: {{'context': [{{piece_old_position: h6, piece_new_position: h8, opponent_piece: rook, opponent_color: white, opponent_position: a8}}]}} \n",
    )
    prompt = _replace_once(prompt, '\n    Begin!', '\n     \n    Begin!')
    prompt = _replace_once(prompt, '\n\n     \n    Begin!', '\n     \n    Begin!')

    return prompt


_classic_text = _load_text("classic_agent_prompt.txt")
_classic_text = apply_relationship_placeholders(_classic_text)
_classic_text = apply_tool_placeholders(_classic_text)
_classic_text = apply_interaction_placeholders(_classic_text)
CLASSIC_AGENT_PROMPT = _classic_text
REINFORCED_AGENT_PROMPT = _build_reinforced_agent_prompt(CLASSIC_AGENT_PROMPT)
_builder_text = apply_json_placeholders(_load_text("builder_agent_prompt.txt"))
_builder_text = apply_relationship_placeholders(_builder_text)
_builder_text = apply_tool_placeholders(_builder_text)
_builder_text = apply_interaction_placeholders(_builder_text)
BUILDER_AGENT_PROMPT = _builder_text
_verifier_json_text = apply_json_placeholders(_load_text("verifier_json_prompt.txt"))
_verifier_json_text = apply_tool_placeholders(_verifier_json_text)
_verifier_json_text = apply_interaction_placeholders(_verifier_json_text)
VERIFIER_JSON_PROMPT = _verifier_json_text
_verifier_fix_text = apply_json_placeholders(_load_text("verifier_fix_prompt.txt"))
_verifier_fix_text = apply_tool_placeholders(_verifier_fix_text)
_verifier_fix_text = apply_interaction_placeholders(_verifier_fix_text)
VERIFIER_FIX_PROMPT = _verifier_fix_text

__all__ = [
    "CLASSIC_AGENT_PROMPT",
    "REINFORCED_AGENT_PROMPT",
    "BUILDER_AGENT_PROMPT",
    "VERIFIER_JSON_PROMPT",
    "VERIFIER_FIX_PROMPT",
]
