# Situation
You wrote:
Here is a structured breakdown of redundancies and how you can factor the prompts into reusable pieces.

---

## 1. High-level inventory

Your JSON has 8 prompts:

1. `server.agent.agent_prompt`
   Chess commentary / Q&A agent using tools.

2. `server.reinforced_agent.agent_prompt`
   Variant of the above with reinforcement/feedback logic.

3. `server.tools.cypher.CYPHER_GENERATION_TEMPLATE`
   Neo4j Cypher generation for chess queries.

4. `server.pipeline.main_prompt`
   Router that picks which agent to call.

5. `server.pipeline.verifier_prompt`
   Router that picks which verification tool to call.

6. `server.neurosymbolicAI.builder.agent_prompt`
   Turns natural language into JSON feature/relationship statements.

7. `server.neurosymbolicAI.verifier.agent_prompt`
   Verifies / normalizes JSON statements via tools.

8. `server.neurosymbolicAI.verifier.fix_agent_prompt`
   English rephrasing / cleanup of statements.

Most of them share the same structural patterns and many literal blocks of text.

---

## 2. Where the redundancies are

### 2.1 Agent vs Reinforced agent (huge duplication)

Prompts:

* `server.agent.agent_prompt`
* `server.reinforced_agent.agent_prompt`

Observations:

* Almost all of `server.reinforced_agent.agent_prompt` is a copy of `server.agent.agent_prompt`.
* They share:

  * `# Role` text: “You are a chess expert providing information about chess strategies and tactics. If you are asked about anything related to chess, please use a tool.”
  * `# Context` section: only respond to chess; must use tools; must traverse GraphCypher QA Chain output; must only use `context`, etc.
  * Relationship descriptions (move_defend, move_is_protected, move_threat, move_is_attacked, tactic defend/threat).
  * `# Tone` section.
  * `# Examples` section with GraphCypher QA examples like:

    * “Question: Does rook defend king?”
    * “Question: Does rook threat bishop?”
    * etc.
  * Tool-use section:

    * `TOOLS:`
    * `You have access to the following tools:`
    * `{tools}`
    * `{tool_names}`
    * The ReAct pattern:
      `Thought: Do I need to use a tool? Yes` → `Action:` → `Action Input:` → `Observation:` → loop → `Final Answer: ...`
  * “How to Process Tool Output” and subsequent “How to …” sections.
  * Tail:

    * `Begin!`
    * `New input: {input}`
    * `{agent_scratchpad}`

Differences:

* `server.agent.agent_prompt` includes a name (“Your name is "Caïssa".”) and one extra “How to answer question related to provide or tell the tactics that support a move”.
* `server.reinforced_agent.agent_prompt` adds a `# Feedback` section that uses user ratings to adjust answers and tweaks some examples.

Conclusion:
`server.reinforced_agent.agent_prompt` is basically `server.agent.agent_prompt` + a small feedback block and minor tweaks. This is the single biggest redundancy.

---

### 2.2 Relationship / feature description block

Appears in:

* `server.agent.agent_prompt`
* `server.reinforced_agent.agent_prompt`
* `server.tools.cypher.CYPHER_GENERATION_TEMPLATE`
* `server.neurosymbolicAI.builder.agent_prompt`
* `server.pipeline.verifier_prompt`

Content pattern:

* Bullet list defining:

  * `{{feature: "move_defend"}}`
  * `{{feature: "move_is_protected"}}`
  * `{{feature: "move_threat"}}`
  * `{{feature: "move_is_attacked"}}`
  * `{{tactic: "defend"}}`
  * `{{tactic: "threat"}}`

  Each with a textual explanation like “is a move made by a piece from its current position to new position… Use when asked about a 'move' that defend or protect a piece” etc., and clarifying difference between tactics vs move_* features.

* In `server.tools.cypher.CYPHER_GENERATION_TEMPLATE` and some others, the block is followed by more schema / context, but the actual definitions are repeated almost verbatim.

Conclusion:
This “relationship semantics” block is duplicated across at least 5 prompts.

---

### 2.3 Shared ReAct tool-usage pattern

Appears (with minor variations) in:

* `server.agent.agent_prompt`
* `server.reinforced_agent.agent_prompt`
* `server.neurosymbolicAI.builder.agent_prompt`
* `server.neurosymbolicAI.verifier.agent_prompt`
* `server.pipeline.verifier_prompt`

Common structure:

* Tool listing:

  * `TOOLS:`
  * `------`
  * `You have access to the following tools:`
  * `{tools}`
  * Often `{tool_names}` as a separate line.

* ReAct protocol:

  * “To use a tool, please use the following format:”
  * `Thought: Do I need to use a tool? Yes`
  * `Action: <tool name>`
  * `Action Input: <json or question>`
  * After tool call:

    * `Observation: ...`
    * `Thought: Do I need to use a tool? [Yes/No]`
  * Final answer pattern:

    * “When you have a response…”
      `Thought: Do I need to use a tool? No`
      `Final Answer: [your response here]`

Differences:

* Indentation and some wording variations per agent.
* Some prompts restrict tool use (e.g., fix_agent says “Do not use any tool” but still reuses part of the “You have access…” boilerplate).

Conclusion:
There is one conceptual module here: how tools are listed and how to call them, repeated with small modifications.

---

### 2.4 “Career importance / specifics” boilerplate

Appears in:

* `server.neurosymbolicAI.builder.agent_prompt` (`# Specifies`)
* `server.neurosymbolicAI.verifier.agent_prompt` (`# Specifics`)
* `server.neurosymbolicAI.verifier.fix_agent_prompt` (`# Specifics`)
* `server.tools.cypher.CYPHER_GENERATION_TEMPLATE` (`# Specifics`)

Content:

* `This is very important to my career`
* `This task is vital to my career, and I greatly value your thorough analysis`

Conclusion:
A two-line emotional/priority block duplicated across 4 prompts.

---

### 2.5 “New input / scratchpad” tail

Appears in:

* `server.agent.agent_prompt`
* `server.neurosymbolicAI.builder.agent_prompt`
* `server.neurosymbolicAI.verifier.agent_prompt`
* `server.neurosymbolicAI.verifier.fix_agent_prompt`
* `server.pipeline.main_prompt`
* `server.pipeline.verifier_prompt`
* `server.reinforced_agent.agent_prompt`

Common snippet:

* `New input: {input}`
* `{agent_scratchpad}`

Sometimes preceded by `Begin!` and sometimes followed by `Output:`.

Conclusion:
The interaction loop tail is almost globally reused, with only minor wrappers.

---

### 2.6 Example blocks reused across prompts

1. **GraphCypher QA examples**
   Appear in:

   * `server.agent.agent_prompt`
   * `server.reinforced_agent.agent_prompt`

   Repeating Q&A patterns like:

   * “Question: Does rook defend king?”
     with full ReAct trace and final answer.
   * “Question: Does rook threat bishop?” etc.

   These example interactions are extremely similar (many literally identical) between the two prompts.

2. **Routing examples**
   Appear in:

   * `server.pipeline.main_prompt` (`# Examples:` mapping text inputs to “Reinforced Agent” or “Builder Agent”)
   * `server.pipeline.verifier_prompt` (`# Examples:` mapping inputs to “Verify Piece Position”, “N/A”, etc.)

   Structure is the same; only labels differ.

3. **JSON transformation examples**
   Appear in:

   * `server.neurosymbolicAI.builder.agent_prompt`
   * `server.neurosymbolicAI.verifier.agent_prompt`

   Both have:

   * `# Examples`
   * `### Example 1`, `### Example 2`
     mapping natural language to a JSON structure of `statements`.

4. **Fix agent example**

   * `server.neurosymbolicAI.verifier.fix_agent_prompt`
     has its own small `# Examples` block (“Input: {…} Final Answer: The position of the white queen is d8.”); those are unique but follow the same formatting convention as the others.

Conclusion:
The examples blocks follow strongly consistent patterns and often share lines verbatim. They are good candidates to isolate by type (GraphCypher examples, JSON examples, routing examples, fix examples).

---

### 2.7 Pipeline main vs pipeline verifier

Prompts:

* `server.pipeline.main_prompt`
* `server.pipeline.verifier_prompt`

Shared elements:

* `# Role` and `# Context` sections that say:

  * “You ONLY choose which [agent/tool] to use from the list.”
* “AGENTS:” / “TOOLS:” listing with `{tools}`.
* `# Examples:` block structure (Input → Final Answer: <Agent/Tool>).
* `# Notes:` including:

  * “Do not execute an [agent/tool].”
  * “ONLY give Output as a Final Answer.”
* Tail:

  * `Begin!`
  * `New input: {input}`
  * `{agent_scratchpad}`
  * `Output:`

Differences:

* One chooses agents, the other chooses verification tools.
* Example content and allowed outputs differ.

Conclusion:
They share a “router pattern” that can be turned into a generic component and parameterized by “what am I routing?” and the allowed outputs.

---

### 2.8 Cypher generation template vs other chess prompts

Prompt:

* `server.tools.cypher.CYPHER_GENERATION_TEMPLATE`

Overlaps with others:

* Shares the same relationship definitions (move_* and tactics).
* Shares the “Specifics” career boilerplate with the neurosymbolic prompts.
* Shares the general chess context (“Our system is a chess commentary solution that provides explanation for chess moves using chess tactics.”) with the main agent prompts.

Conclusion:
This template reuses the domain ontology and importance boilerplate; you can externalize them as separate modules.

---

## 3. Suggested segmentation into reusable components

Below is a reasonable decomposition into components that you can reuse/combine to reconstruct all eight prompts.

### 3.1 Cross-cutting components

1. **CHESS_RELATIONSHIP_DEFINITIONS**

   * Contains the bullet list:

     * `{{feature: "move_defend"}}`
     * `{{feature: "move_is_protected"}}`
     * `{{feature: "move_threat"}}`
     * `{{feature: "move_is_attacked"}}`
     * `{{tactic: "defend"}}`
     * `{{tactic: "threat"}}`

   * Used by:

     * `server.agent.agent_prompt`
     * `server.reinforced_agent.agent_prompt`
     * `server.tools.cypher.CYPHER_GENERATION_TEMPLATE`
     * `server.neurosymbolicAI.builder.agent_prompt`
     * `server.pipeline.verifier_prompt`

2. **CAREER_IMPORTANCE_BOILERPLATE**

   * Text under `# Specifies / # Specifics`:

     * “This is very important to my career”
     * “This task is vital to my career, and I greatly value your thorough analysis”

   * Used by:

     * `server.neurosymbolicAI.builder.agent_prompt`
     * `server.neurosymbolicAI.verifier.agent_prompt`
     * `server.neurosymbolicAI.verifier.fix_agent_prompt`
     * `server.tools.cypher.CYPHER_GENERATION_TEMPLATE`

3. **COMMON_TOOL_LIST**

   * The “you have tools” boilerplate:

     * `TOOLS:`
     * `------`
     * `You have access to the following tools:`
     * `{tools}`
     * optionally `{tool_names}`

   * Used by:

     * `server.agent.agent_prompt`
     * `server.reinforced_agent.agent_prompt`
     * `server.neurosymbolicAI.builder.agent_prompt`
     * `server.neurosymbolicAI.verifier.agent_prompt`
     * `server.pipeline.verifier_prompt`
     * `server.neurosymbolicAI.verifier.fix_agent_prompt` (partially)

4. **COMMON_REACT_PROTOCOL**

   * The generic ReAct instructions:

     * “To use a tool, please use the following format:”
     * `Thought: Do I need to use a tool? Yes`
     * `Action:`
     * `Action Input:`
     * `Observation:`
     * “When you have a response to say to the Human…”
     * `Thought: Do I need to use a tool? No`
     * `Final Answer: [your response here]`

   * Used by the same tool-using agents as above (with fix_agent overriding “Do not use any tool”).

5. **INTERACTION_TAIL**

   * Conversation trailer:

     * optionally `Begin!`
     * `New input: {input}`
     * `{agent_scratchpad}`
     * optional `Output:`

   * Used by:

     * all except `server.tools.cypher.CYPHER_GENERATION_TEMPLATE`.

You can define these as string fragments and include them where needed.

---

### 3.2 Family-specific components

#### A. Chess commentary / explanation agents

For:

* `server.agent.agent_prompt`
* `server.reinforced_agent.agent_prompt`

Components:

1. `ROLE_CHESS_EXPERT_AGENT`
   “You are a chess expert providing information about chess strategies and tactics. If you are asked about anything related to chess, please use a tool.” (+ optional name “Caïssa”).

2. `CONTEXT_CHESS_QA`

   * Only chess questions allowed.
   * Must use tools for chess positions, tactics, puzzles.
   * Must traverse GraphCypher QA output and only use its `context`.

3. `TONE_CHESS_COMMENTATOR`
   The `# Tone` section.

4. `GRAPH_CYPHER_EXAMPLES`
   The Q&A examples for “Does rook defend king?”, “Does rook threat bishop?”, etc., including the full ReAct traces.

5. `TOOL_OUTPUT_PROCESSING_GUIDE`
   The “How to Process Tool Output” and follow-up “How to answer question related to a summary step by step…”, “How to process output list…”, “How to answer commentary…” sections.

6. `FEEDBACK_SECTION` (only for `reinforced_agent`)
   The rating-driven feedback instructions.

Then:

* `server.agent.agent_prompt` =
  `ROLE_CHESS_EXPERT_AGENT`

  * `CONTEXT_CHESS_QA`
  * `CHESS_RELATIONSHIP_DEFINITIONS`
  * `TONE_CHESS_COMMENTATOR`
  * `GRAPH_CYPHER_EXAMPLES`
  * `COMMON_TOOL_LIST`
  * `COMMON_REACT_PROTOCOL`
  * `TOOL_OUTPUT_PROCESSING_GUIDE`
  * `INTERACTION_TAIL`.

* `server.reinforced_agent.agent_prompt` =
  same as above, minus the name “Caïssa”, plus `FEEDBACK_SECTION` and slightly adjusted examples.

#### B. Cypher generation template

For:

* `server.tools.cypher.CYPHER_GENERATION_TEMPLATE`

Components:

1. `ROLE_NEO4J_CYPHER_DEV`
2. `SPECIFICS_CAREER_IMPORTANCE` (import `CAREER_IMPORTANCE_BOILERPLATE`)
3. `CONTEXT_CHESS_COMMENTARY_SYSTEM` (system description, importance of choosing the right relationship).
4. `CHESS_RELATIONSHIP_DEFINITIONS` (reuse).
5. `CYPHER_SCHEMA_DESCRIPTION` (graph schema + properties).
6. `CYPHER_EXAMPLE_QUERIES` (`### Example 1: {{feature: "move_is_protected"}}` … `### Example 19: {{tactic_name: "hanging piece"}}`).
7. Output constraints (only Cypher, no explanations).

This prompt already doesn’t use tools or `{agent_scratchpad}`, so it stays stand-alone but shares common blocks.

#### C. Neurosymbolic builder / verifier / fix

For:

* `server.neurosymbolicAI.builder.agent_prompt`
* `server.neurosymbolicAI.verifier.agent_prompt`
* `server.neurosymbolicAI.verifier.fix_agent_prompt`

Components:

1. `ROLE_JSON_BUILDER`
   “You are a chess expert in extracting features and relationships … in form of JSON.”

2. `ROLE_JSON_VERIFIER`
   “You are an expert in converting complex text to simple statements in form of JSON…”

3. `ROLE_ENGLISH_FIXER`
   “You are an english expert in re-adjusting statements in better structure…”

4. `SPECIFICS_CAREER_IMPORTANCE`
   Import `CAREER_IMPORTANCE_BOILERPLATE`.

5. `CONTEXT_JSON_ONLY`

   * “You MUST ONLY give the JSON format of the Input.”
   * For the builder: allowed piece/color/position/relation/feature values.
   * For the verifier: additional instructions about not hallucinating information.

6. `COMMON_TOOL_LIST` + `COMMON_REACT_PROTOCOL`
   For builder & verifier (fix_agent overrides with “Do not use any tool”).

7. `JSON_EXAMPLES_BUILDER`
   Examples 1–2 mapping natural language to JSON statements.

8. `JSON_EXAMPLES_VERIFIER`
   Similar examples used in the verifier prompt.

9. `FIX_EXAMPLES`
   Example of rephrasing.

10. `INTERACTION_TAIL`
    Shared tail.

Composition:

* Builder = `ROLE_JSON_BUILDER` + `SPECIFICS_CAREER_IMPORTANCE` + `CONTEXT_JSON_ONLY` + `CHESS_RELATIONSHIP_DEFINITIONS` (if needed) + `COMMON_TOOL_LIST` + `COMMON_REACT_PROTOCOL` + `JSON_EXAMPLES_BUILDER` + `INTERACTION_TAIL`.

* Verifier = `ROLE_JSON_VERIFIER` + `SPECIFICS_CAREER_IMPORTANCE` + `CONTEXT_JSON_ONLY` + `COMMON_TOOL_LIST` + `COMMON_REACT_PROTOCOL` + `JSON_EXAMPLES_VERIFIER` + `INTERACTION_TAIL`.

* Fix = `ROLE_ENGLISH_FIXER` + `SPECIFICS_CAREER_IMPORTANCE` + small tool notice (“Do not use any tool”) + `FIX_EXAMPLES` + `INTERACTION_TAIL`.

#### D. Routing / pipeline prompts

For:

* `server.pipeline.main_prompt`
* `server.pipeline.verifier_prompt`

Components:

1. `ROLE_AGENT_ROUTER`
   “You are the main agent that decides which sub-agent to take…”

2. `ROLE_VERIFIER_ROUTER`
   “You are a chess expert, validating the commentary … You ONLY choose which tool to use…”

3. `CONTEXT_ROUTER_CORE`

   * “You ONLY choose which [agent/tool] to use from the list.”
   * Do not execute them.

4. `ROUTER_TOOL_LIST`
   The `AGENTS:/TOOLS:` block with `{tools}`.

5. `ROUTER_EXAMPLES_AGENT`
   Examples mapping user inputs to “Reinforced Agent” vs “Builder Agent”.

6. `ROUTER_EXAMPLES_VERIFIER`
   Examples mapping to “Verify Piece Position”, “Verify Piece Move Feature”, “N/A”.

7. `ROUTER_NOTES`

   * “Do not execute an [agent/tool].”
   * “ONLY give Output as a Final Answer.”
   * For `main_prompt`: “Do not include character ` in the Output.”

8. `INTERACTION_TAIL`
   With `Begin!`, `New input: {input}`, `{agent_scratchpad}`, `Output:`.

---

## 4. How to reconstruct prompts from components

Once you define these components as reusable strings or templates (e.g. via simple concatenation, or a templating system), you can declare each prompt as:

* A list of component IDs in order, plus
* A small per-prompt override dictionary (for names like “Caïssa”, or “do not use any tool”, or feedback section).

For example (pseudo-structure):

```json
{
  "components": {
    "role_chess_expert_agent": "...",
    "context_chess_qa": "...",
    "chess_relationship_definitions": "...",
    "tone_chess_commentator": "...",
    "graph_cypher_examples": "...",
    "common_tool_list": "...",
    "common_react_protocol": "...",
    "tool_output_processing_guide": "...",
    "interaction_tail": "...",
    "feedback_section": "..."
  },
  "prompts": {
    "server.agent.agent_prompt": {
      "parts": [
        "role_chess_expert_agent",
        "context_chess_qa",
        "chess_relationship_definitions",
        "tone_chess_commentator",
        "graph_cypher_examples",
        "common_tool_list",
        "common_react_protocol",
        "tool_output_processing_guide",
        "interaction_tail"
      ]
    },
    "server.reinforced_agent.agent_prompt": {
      "parts": [
        "role_chess_expert_agent",
        "context_chess_qa",
        "chess_relationship_definitions",
        "tone_chess_commentator",
        "graph_cypher_examples",
        "common_tool_list",
        "common_react_protocol",
        "tool_output_processing_guide",
        "feedback_section",
        "interaction_tail"
      ]
    }
  }
}
```

You can do the same for the neurosymbolic, pipeline, and Cypher prompts using the component mapping above.
