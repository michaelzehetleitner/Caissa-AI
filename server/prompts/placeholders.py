"""Shared prompt fragments and placeholder helpers."""

from __future__ import annotations

CAREER_IMPORTANCE_PLACEHOLDER = "<<CAREER_IMPORTANCE_BLOCK>>\n"
JSON_ONLY_PLACEHOLDER = "<<JSON_ONLY_LINE>>\n"
RELATIONSHIP_LIST_PLACEHOLDER = "<<CHESS_RELATIONSHIP_LIST_BLOCK>>"
RELATIONSHIP_LIST_FEATURES_PLACEHOLDER = "<<CHESS_RELATIONSHIP_FEATURES_BLOCK>>"
RELATIONSHIP_LIST_MEDIUM_PLACEHOLDER = "<<CHESS_RELATIONSHIP_LIST_MEDIUM_BLOCK>>"
RELATIONSHIP_LIST_SHORT_PLACEHOLDER = "<<CHESS_RELATIONSHIP_LIST_SHORT_BLOCK>>"
PIECE_LIST_PLACEHOLDER = "<<CHESS_PIECE_LIST_BLOCK>>"
COLOR_LIST_PLACEHOLDER = "<<CHESS_COLOR_LIST_BLOCK>>"
BOARD_SQUARE_LIST_PLACEHOLDER = "<<CHESS_BOARD_SQUARE_LIST_BLOCK>>"
RELATION_NAME_LIST_PLACEHOLDER = "<<CHESS_RELATION_LIST_BLOCK>>"
RELATION_FEATURE_LIST_PLACEHOLDER = "<<CHESS_RELATION_FEATURE_LIST_BLOCK>>"
TOOLS_STANDARD_PLACEHOLDER = "<<TOOLS_STANDARD_BLOCK>>"
TOOLS_NO_TOOL_PLACEHOLDER = "<<TOOLS_NO_TOOL_BLOCK>>"
TOOLS_INDENTED_PLACEHOLDER = "<<TOOLS_INDENTED_BLOCK>>"
TOOLS_ROUTER_AGENT_PLACEHOLDER = "<<TOOLS_ROUTER_AGENT_BLOCK>>"
TOOLS_ROUTER_TOOL_PLACEHOLDER = "<<TOOLS_ROUTER_TOOL_BLOCK>>"
ROUTER_AGENT_NOTES_PLACEHOLDER = "<<ROUTER_AGENT_NOTES_BLOCK>>"
ROUTER_TOOL_NOTES_PLACEHOLDER = "<<ROUTER_TOOL_NOTES_BLOCK>>"
ROUTER_EXAMPLES_PLACEHOLDER = "<<ROUTER_EXAMPLES_BLOCK>>"
INTERACTION_BEGIN_PLACEHOLDER = "<<INTERACTION_BEGIN_TAIL>>"
INTERACTION_ROUTER_PLACEHOLDER = "<<INTERACTION_ROUTER_TAIL>>"
INTERACTION_SIMPLE_PLACEHOLDER = "<<INTERACTION_SIMPLE_TAIL>>"
INTERACTION_SIMPLE_INDENT_PLACEHOLDER = "<<INTERACTION_SIMPLE_TAIL_INDENT>>"

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
RELATIONSHIP_LIST_FEATURES_BLOCK = (
    "1. {{feature: \"move_defend\"}}: is a move made by a piece from its current position to new position to defend an ally piece on a third different position. Use when asked about a \"move\" that defend or protect a piece.\n"
    "2. {{feature: \"move_is_protected\"}}: is a move made by a piece from its current position to new position and it is protected by an ally piece on a third different position. Use when asked about pieces that defend or protect a \"move\".\n"
    "3. {{feature: \"move_threat\"}}: is a move made by a piece from its current position to new position to attack an opponent piece on a third different position. Use when asked about a \"move\" that attack or threat a piece.\n"
    "4. {{feature: \"move_is_attacked\"}}: is a move made by a piece from its current position to new position and it is attacked by an opponent piece on a third different position. Use when asked about pieces that attack or threat a \"move\".\n"
)
RELATIONSHIP_LIST_SHORT_BLOCK = (
    "1. {{feature: \"move_defend\"}}: is a move made by a piece from its current position to new position to defend an ally piece on a third different position. Use when asked about a \"move\" that defend or protect a piece.\n"
    "2. {{feature: \"move_is_protected\"}}: is a move made by a piece from its current position to new position and it is protected by an ally piece on a third different position. Use when asked about pieces that defend or protect a \"move\".\n"
    "3. {{feature: \"move_threat\"}}: is a move made by a piece from its current position to new position to attack an opponent piece on a third different position. Use when asked about a \"move\" that attack or threat a piece.\n"
    "4. {{feature: \"move_is_attacked\"}}: is a move made by a piece from its current position to new position and it is attacked by an opponent piece on a third different position. Use when asked about pieces that attack or threat a \"move\".\n"
    "5. {{tactic: \"defend\"}}: is a relationship between a piece and an ally piece such that piece can defend or protect the ally piece. this is DIFFERENT from \"move_defend\" and \"move_is_protected\".\n"
    "6. {{tactic: \"threat\"}}: is a relationship between a piece and an opponent piece such that piece can attack or threat the opponent. this is DIFFERENT from \"move_threat\" and \"move_is_attacked\".\n"
)
PIECE_LIST_BLOCK = (
    "- Chess piece from the following list of pieces: [king, queen, knight, bishop, rook, pawn]\n"
)
COLOR_LIST_BLOCK = (
    "- Chess color of a chess piece from the following list: [black, white]\n"
)
BOARD_SQUARE_LIST_BLOCK = (
    "- Chess position of a chess piece from the following list of positions: [\n"
    "    a1, a2, a3, a4, a5, a6, a7, a8,\n"
    "    b1, b2, b3, b4, b5, b6, b7, b8,\n"
    "    c1, c2, c3, c4, c5, c6, c7, c8,\n"
    "    d1, d2, d3, d4, d5, d6, d7, d8,\n"
    "    e1, e2, e3, e4, e5, e6, e7, e8,\n"
    "    f1, f2, f3, f4, f5, f6, f7, f8,\n"
    "    g1, g2, g3, g4, g5, g6, g7, g8,\n"
    "    h1, h2, h3, h4, h5, h6, h7, h8\n"
    " ]\n"
)
RELATION_NAME_LIST_BLOCK = (
    "- Chess relation between two chess pieces is from the following list of relations: [defend, threat]\n"
)
RELATION_FEATURE_LIST_BLOCK = (
    "- Chess move features between two chess pieces is from the following list of relations: [move_defend, move_threat, move_is_protected, move_is_attacked]\n"
)
TOOLS_STANDARD_BLOCK = (
    "TOOLS:\n"
    "------\n"
    "\n"
    "You have access to the following tools:\n"
    "\n"
    "{tools}\n"
    "\n"
    "To use a tool, please use the following format:\n"
    "\n"
    "```\n"
    "Thought: Do I need to use a tool? Yes\n"
    "Action: the action to take, should be one of [{tool_names}]\n"
    "Action Input: the input to the action\n"
    "Observation: the result of the action\n"
    "Output: the output from the tool\n"
    "```\n"
    "\n"
    "When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:\n"
    "\n"
    "```\n"
    "Thought: Do I need to use a tool? No\n"
    "Final Answer: [your response here]\n"
    "```\n"
)

TOOLS_NO_TOOL_BLOCK = (
    "TOOLS:\n"
    "------\n"
    "\n"
    "You have access to the following tools:\n"
    "\n"
    "{tools}\n"
    "\n"
    "{tool_names}\n"
    "\n"
    "Do not use any tool\n"
)

TOOLS_INDENTED_BLOCK = (
    "TOOLS:\n"
    "------\n"
    "\n"
    "You have access to the following tools:\n"
    "\n"
    "{tools}\n"
    "\n"
    "To use a tool, please use the following format:\n"
    "\n"
    "    Thought: Do I need to use a tool? Yes\n"
    "    Action: the action to take, should be one of [{tool_names}]\n"
    "    Action Input: the input to the action\n"
    "    Observation: the result of the action\n"
    "    Output: the output from the tool\n"
    "\n"
    "When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:\n"
    "\n"
    "    Thought: Do I need to use a tool? No\n"
    "    Final Answer: [your response here]\n"
)

TOOLS_ROUTER_AGENT_BLOCK = (
    "AGENTS:\n"
    "------\n"
    "\n"
    "You have access to the following agents:\n"
    "\n"
    "{tools}\n"
    "           \n"
    "please use the following format:\n"
    "\n"
    "```\n"
    "Thought: What agent should I pick?\n"
    "Action: the agent to take, should be one of [{tool_names}]\n"
    "Final Answer: the output is the name of the agent choosen\n"
    "```\n"
)

TOOLS_ROUTER_TOOL_BLOCK = (
    "TOOLS:\n"
    "------\n"
    "\n"
    "You have access to the following tools:\n"
    "\n"
    "{tools}\n"
    "\n"
    "please use the following format:\n"
    "\n"
    "```\n"
    "Thought: What tool should I pick?\n"
    "Action: the action to take, should be one of [{tool_names}]\n"
    "Final Answer: the output is the name of the tool choosen\n"
    "```\n"
)

INTERACTION_BEGIN_TAIL_BLOCK = (
    "Begin!\n"
    "\n"
    "New input: {input}\n"
    "{agent_scratchpad}\n"
)

INTERACTION_ROUTER_TAIL_BLOCK = (
    "Begin!\n"
    "\n"
    "New input: {input}\n"
    "{agent_scratchpad}\n"
    "\n"
    "Output:\n"
)

INTERACTION_SIMPLE_TAIL_BLOCK = (
    "New input: {input}\n"
    "{agent_scratchpad}\n"
)

INTERACTION_SIMPLE_TAIL_INDENT_BLOCK = (
    "New input: {input}\n"
    "{agent_scratchpad}\n"
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
    text = _replace_placeholder_block(text, PIECE_LIST_PLACEHOLDER, PIECE_LIST_BLOCK)
    text = _replace_placeholder_block(text, COLOR_LIST_PLACEHOLDER, COLOR_LIST_BLOCK)
    text = _replace_placeholder_block(text, BOARD_SQUARE_LIST_PLACEHOLDER, BOARD_SQUARE_LIST_BLOCK)
    text = _replace_placeholder_block(text, RELATION_NAME_LIST_PLACEHOLDER, RELATION_NAME_LIST_BLOCK)
    text = _replace_placeholder_block(text, RELATION_FEATURE_LIST_PLACEHOLDER, RELATION_FEATURE_LIST_BLOCK)
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
            f"{indent}{line}" if line else indent for line in block.strip("\n").splitlines()
        )
        text = f"{text[:line_start]}{indented_block}\n{text[line_end + 1 :]}"
    return text


def apply_relationship_placeholders(text: str) -> str:
    text = _replace_placeholder_block(text, RELATIONSHIP_LIST_PLACEHOLDER, RELATIONSHIP_LIST_BLOCK)
    text = _replace_placeholder_block(
        text,
        RELATIONSHIP_LIST_FEATURES_PLACEHOLDER,
        RELATIONSHIP_LIST_FEATURES_BLOCK,
    )
    text = _replace_placeholder_block(text, RELATIONSHIP_LIST_MEDIUM_PLACEHOLDER, RELATIONSHIP_LIST_MEDIUM_BLOCK)
    text = _replace_placeholder_block(text, RELATIONSHIP_LIST_SHORT_PLACEHOLDER, RELATIONSHIP_LIST_SHORT_BLOCK)
    return text


def apply_tool_placeholders(text: str) -> str:
    text = _replace_placeholder_block(text, TOOLS_STANDARD_PLACEHOLDER, TOOLS_STANDARD_BLOCK)
    text = _replace_placeholder_block(text, TOOLS_NO_TOOL_PLACEHOLDER, TOOLS_NO_TOOL_BLOCK)
    text = _replace_placeholder_block(text, TOOLS_INDENTED_PLACEHOLDER, TOOLS_INDENTED_BLOCK)
    text = _replace_placeholder_block(text, TOOLS_ROUTER_AGENT_PLACEHOLDER, TOOLS_ROUTER_AGENT_BLOCK)
    text = _replace_placeholder_block(text, TOOLS_ROUTER_TOOL_PLACEHOLDER, TOOLS_ROUTER_TOOL_BLOCK)
    text = _replace_placeholder_block(text, ROUTER_AGENT_NOTES_PLACEHOLDER, ROUTER_AGENT_NOTES_BLOCK)
    text = _replace_placeholder_block(text, ROUTER_TOOL_NOTES_PLACEHOLDER, ROUTER_TOOL_NOTES_BLOCK)
    return text


def apply_interaction_placeholders(text: str) -> str:
    text = _replace_placeholder_block(text, INTERACTION_BEGIN_PLACEHOLDER, INTERACTION_BEGIN_TAIL_BLOCK)
    text = _replace_placeholder_block(text, INTERACTION_ROUTER_PLACEHOLDER, INTERACTION_ROUTER_TAIL_BLOCK)
    text = _replace_placeholder_block(text, INTERACTION_SIMPLE_PLACEHOLDER, INTERACTION_SIMPLE_TAIL_BLOCK)
    text = _replace_placeholder_block(
        text,
        INTERACTION_SIMPLE_INDENT_PLACEHOLDER,
        INTERACTION_SIMPLE_TAIL_INDENT_BLOCK,
    )
    return text


__all__ = [
    "apply_json_placeholders",
    "apply_relationship_placeholders",
    "apply_tool_placeholders",
    "apply_interaction_placeholders",
    "_replace_once",
]
TOOLS_ROUTER_BLOCK = (
    "You have access to the following tools:\n"
    "\n"
    "{tools}\n"
    "           \n"
    "please use the following format:\n"
    "\n"
    "```\n"
    "Thought: What agent should I pick?\n"
    "Action: the agent to take, should be one of [{tool_names}]\n"
    "Final Answer: the output is the name of the agent choosen\n"
    "```\n"
)

ROUTER_AGENT_NOTES_BLOCK = (
    "- Do not execute an agent.\n"
    "- ONLY give Output as a Final Answer\n"
    "- Do not include character ` in the Output\n"
)

ROUTER_TOOL_NOTES_BLOCK = (
    "- Do not execute a tool.\n"
    "- ONLY give Output as a Final Answer\n"
)

def build_router_examples_block(examples: list[tuple[str, str] | tuple[str, str, str]]) -> str:
    lines = ["# Examples:"]
    for idx, example in enumerate(examples, start=1):
        if len(example) == 2:
            example_input, answer = example
            heading = f"### Example {idx}"
        else:
            heading, example_input, answer = example  # type: ignore[misc]
            if not heading:
                heading = f"### Example {idx}"
        lines.append(heading)
        lines.append(f"Input: {example_input}")
        lines.append(f"Final Answer: {answer}")
        lines.append("")
    lines.append("")
    return "\n".join(lines)
