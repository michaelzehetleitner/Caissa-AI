"""Shared prompt fragments and placeholder helpers."""

from __future__ import annotations

CAREER_IMPORTANCE_PLACEHOLDER = "<<CAREER_IMPORTANCE_BLOCK>>\n"
JSON_ONLY_PLACEHOLDER = "<<JSON_ONLY_LINE>>\n"
RELATIONSHIP_LIST_PLACEHOLDER = "<<CHESS_RELATIONSHIP_LIST_BLOCK>>"
RELATIONSHIP_LIST_MEDIUM_PLACEHOLDER = "<<CHESS_RELATIONSHIP_LIST_MEDIUM_BLOCK>>"
RELATIONSHIP_LIST_SHORT_PLACEHOLDER = "<<CHESS_RELATIONSHIP_LIST_SHORT_BLOCK>>"

CAREER_IMPORTANCE_BLOCK = (
    "            - This is very important to my career\n"
    "            - This task is vital to my career, and I greatly value your thorough analysis\n"
    "            \n"
)
JSON_ONLY_LINE = "            - You MUST ONLY give the JSON format of the Input.\n"
RELATIONSHIP_LIST_BLOCK = (
    "1. {{feature: \"move_defend\"}}: is a move made by a piece from its current position to new position to defend an ally piece on a third different position. Use when asked about a \"move\" that defend or protect a piece.\n"
    "2. {{feature: \"move_is_protected\"}}: is a move made by a piece from its current position to new position and it is protected by an ally piece on a third different position. Use when asked about pieces that defend or protect a \"move\".\n"
    "3. {{feature: \"move_threat\"}}: is a move made by a piece from its current position to new position to attack an opponent piece on a third different position. Use when asked about a \"move\" that attack or threat a piece.\n"
    "4. {{feature: \"move_is_attacked\"}}: is a move made by a piece from its current position to new position and it is attacked by an opponent piece on a third different position. Use when asked about pieces that attack or threat a \"move\" or counterattack.\n"
    "5. {{tactic: \"defend\"}}: is a relationship between a piece and an ally piece such that piece can defend or protect the ally piece. this is DIFFERENT from \"move_defend\" and \"move_is_protected\".\n"
    "6. {{tactic: \"threat\"}}: is a relationship between a piece and an opponent piece such that piece can capture or attack or threat the opponent. this is DIFFERENT from \"move_threat\" and \"move_is_attacked\".\n"
)
RELATIONSHIP_LIST_MEDIUM_BLOCK = (
    "1. {{feature: \"move_defend\"}}: is a move made by a piece from its current position to new position to defend an ally piece on a third different position. Use when asked about a \"move\" that defend or protect a piece.\n"
    "2. {{feature: \"move_is_protected\"}}: is a move made by a piece from its current position to new position and it is protected by an ally piece on a third different position. Use when asked about pieces that defend or protect a \"move\".\n"
    "3. {{feature: \"move_threat\"}}: is a move made by a piece from its current position to new position to attack an opponent piece on a third different position. Use when asked about a \"move\" that attack or threat a piece.\n"
    "4. {{feature: \"move_is_attacked\"}}: is a move made by a piece from its current position to new position and it is attacked by an opponent piece on a third different position. Use when asked about pieces that attack or threat a \"move\" or counterattack.\n"
    "5. {{tactic: \"defend\"}}: is a relationship between a piece and an ally piece such that piece can defend or protect the ally piece. this is DIFFERENT from \"move_defend\" and \"move_is_protected\".\n"
    "6. {{tactic: \"threat\"}}: is a relationship between a piece and an opponent piece such that piece can attack or threat the opponent. this is DIFFERENT from \"move_threat\" and \"move_is_attacked\".\n"
)
RELATIONSHIP_LIST_SHORT_BLOCK = (
    "1. {{feature: \"move_defend\"}}: is a move made by a piece from its current position to new position to defend an ally piece on a third different position. Use when asked about a \"move\" that defend or protect a piece.\n"
    "2. {{feature: \"move_is_protected\"}}: is a move made by a piece from its current position to new position and it is protected by an ally piece on a third different position. Use when asked about pieces that defend or protect a \"move\".\n"
    "3. {{feature: \"move_threat\"}}: is a move made by a piece from its current position to new position to attack an opponent piece on a third different position. Use when asked about a \"move\" that attack or threat a piece.\n"
    "4. {{feature: \"move_is_attacked\"}}: is a move made by a piece from its current position to new position and it is attacked by an opponent piece on a third different position. Use when asked about pieces that attack or threat a \"move\".\n"
    "5. {{tactic: \"defend\"}}: is a relationship between a piece and an ally piece such that piece can defend or protect the ally piece. this is DIFFERENT from \"move_defend\" and \"move_is_protected\".\n"
    "6. {{tactic: \"threat\"}}: is a relationship between a piece and an opponent piece such that piece can attack or threat the opponent. this is DIFFERENT from \"move_threat\" and \"move_is_attacked\".\n"
)


def _replace_once(text: str, target: str, replacement: str) -> str:
    """Replace ``target`` exactly once, raising if it is missing."""

    if target not in text:
        raise ValueError(f"Expected text {target!r} not found in prompt")
    return text.replace(target, replacement, 1)


def apply_json_placeholders(text: str) -> str:
    if CAREER_IMPORTANCE_PLACEHOLDER in text:
        text = _replace_once(text, CAREER_IMPORTANCE_PLACEHOLDER, CAREER_IMPORTANCE_BLOCK)
    if JSON_ONLY_PLACEHOLDER in text:
        text = _replace_once(text, JSON_ONLY_PLACEHOLDER, JSON_ONLY_LINE)
    return text


def _replace_placeholder_block(text: str, token: str, block: str) -> str:
    while token in text:
        idx = text.index(token)
        line_start = text.rfind("\n", 0, idx) + 1
        line_end = text.find("\n", idx)
        if line_end == -1:
            line_end = len(text)
        indent = text[line_start:idx]
        indented_block = "\n".join(
            f"{indent}{line}" if line else "" for line in block.strip("\n").splitlines()
        )
        text = f"{text[:line_start]}{indented_block}\n{text[line_end + 1 :]}"
    return text


def apply_relationship_placeholders(text: str) -> str:
    text = _replace_placeholder_block(text, RELATIONSHIP_LIST_PLACEHOLDER, RELATIONSHIP_LIST_BLOCK)
    text = _replace_placeholder_block(text, RELATIONSHIP_LIST_MEDIUM_PLACEHOLDER, RELATIONSHIP_LIST_MEDIUM_BLOCK)
    text = _replace_placeholder_block(text, RELATIONSHIP_LIST_SHORT_PLACEHOLDER, RELATIONSHIP_LIST_SHORT_BLOCK)
    return text


__all__ = [
    "apply_json_placeholders",
    "apply_relationship_placeholders",
    "_replace_once",
]
