# Prompt Refactor: Repair & Test Strategy

## Why This Exists
The recent prompt modularization touched `server/prompts/` only, but side effects spread into
`builder_ai.py` and the LangGraph pipeline. We now have a single place to capture how to fix the
regressions **and** the extra tests we expect before repeating a prompt-focused PR.

## Repair Plan (Immediate)
1. **Restore a working Builder agent**
   - Re‑implement `Builder.build_relations()` (or equivalent) so it actually calls the JSON parser,
     produces `json_response`, and iterates the graph to create features.
   - Ensure `Builder.__init__` no longer references undefined locals (the current
     `print("json_response:", json_response)` line fails instantly).
2. **Re-wire pipeline tool bindings**
   - Update the `verifier_tools` lambdas in `server/pipeline.py` to point to
     `verify_piece_position`, `verify_piece_relation`, and `verify_move_relation` respectively,
     each accepting the LangGraph `state` dict.
   - Keep `run_main -> build_relation` coherent: once the builder is restored, the `status`
     transitions should once again reach `"End"` instead of raising `AttributeError`.
3. **Clean the working tree**
   - Remove committed artefacts such as `__pycache__/`, `.DS_Store`, model checkpoints, etc.
   - Verify `.gitignore` (now at repo root) excludes those paths going forward.

## Ongoing Expectations
- Whenever prompts change, re-run both the golden-master tests and the new wiring/builder suites.
- Keep this document updated when the architecture evolves (e.g., if Builder or Verifier move to
  dedicated microservices, document the new smoke tests required).

## Golden-Master Recovery & Transition Plan
The original inline prompts from `server/*.py` are the canonical “golden master.” To keep the
refactor honest we need both the modular files *and* a way to verify they still match the source
text. Follow this process:

1. **Extract the golden text**
   - Run `python3 scripts/create_prompt_snapshot.py --git-ref origin/main` to regenerate
     `tests/golden_prompts/prompts.json` from the canonical commit. (You can point `--git-ref` at a
     different hash/branch if the ground truth changes.)
   - The generated JSON stores both the prompt text and metadata (`path`, `target`, optional `scope`)
     plus a top-level `metadata.commit` entry recording the git hash used for extraction.

2. **Replicate the golden text in the modular files**
   - Replace the current contents of `server/prompts/agents.py`, `selectors.py`, `tools.py`, and the
     shared text files (`agent_examples.txt`, `agent_guidance.txt`) with the freshly extracted golden
     text so the new modules are byte-for-byte equivalent to the original inline prompts (apart from
     necessary indentation tweaks).

3. **Add golden-master tests**
   - `tests/test_prompt_golden_master.py` now imports each prompt from `server.prompts.*`, looks up
     the matching entry in `tests/golden_prompts/prompts.json`, and asserts equality. Any edit that
     doesn’t update the JSON (via the script above) will fail.
   - Document in this markdown file (and in code review checklists) that changing a prompt requires
     updating: (a) the prompt module, and (b) rerunning `scripts/create_prompt_snapshot.py` so the
     JSON golden master reflects the change.

4. **Resume refactoring with guardrails**
   - With the modular files verified against the golden master, continue reorganizing shared blocks
     or adding new prompts. Each intentional change now forces a golden-file update, ensuring we
     never lose the original behavior silently.

5. **Optional clean-up once stable**
   - After the refactor is fully vetted, we can decide whether to keep the golden directory as a
     long-term reference or archive it. Until then, it remains our safety net.

## Prompt Centralization Design

### Current Prompt Inventory

| Location | Variable | Purpose |
| --- | --- | --- |
| `server/agent.py` | `agent_prompt` | Classic ReAct agent for `/chatbot`. |
| `server/reinforced_agent.py` | `agent_prompt` | ReAct agent invoked inside LangGraph pipeline. |
| `server/pipeline.py` | `main_prompt` | Dispatcher that picks Builder vs. Reinforced agent. |
| `server/pipeline.py` | `verifier_prompt` | Classifies verification tool usage. |
| `server/neurosymbolicAI/builder_ai.py` | `self.agent_prompt` | Extracts JSON relation definitions. |
| `server/neurosymbolicAI/verifier_ai.py` | `self.agent_prompt` | Breaks commentary into JSON statements. |
| `server/neurosymbolicAI/verifier_ai.py` | `self.fix_agent_prompt` | Rewrites statements into clean prose. |
| `server/tools/cypher.py` | `CYPHER_GENERATION_TEMPLATE` | Generates Cypher for Graph RAG. |
| `server/neurosymbolicAI/verifier_ai.py` | `schema` string inside `verify_piece_position` | Kor extraction schema (also replicated for relation/move checks). |

### Target Structure

Create a dedicated package: `server/prompts/`.

```
server/prompts/
├── __init__.py               # re-export helpers/constants
├── agents.py                 # ReAct-style prompts (classic, reinforced, builder, verifier)
├── selectors.py              # LangGraph main + verifier dispatcher prompts
├── tools.py                  # Cypher generation template + other tool-specific templates
├── schemas.py                # Kor schema text blocks (piece position, relation, move feature)
```

Guidelines:
- Store each prompt as an upper-case constant (e.g., `CLASSIC_AGENT_PROMPT`).
- For prompts that require string formatting (e.g., LangChain `PromptTemplate`), keep the string literal in `server/prompts/...` and have the consumer do `PromptTemplate.from_template(prompt_constants.CLASSIC_AGENT_PROMPT)`.
- If a prompt requires runtime `format` (like `{tools}` placeholders), keep the placeholders but let each module pass the values when instantiating `PromptTemplate`.
- For repeated schemas (e.g., Kor extraction), expose helper functions that return the string; verifier utilities then pull from `prompts.schemas`.

### Migration Steps

1. **Introduce package**
   - Create `server/prompts/__init__.py` exporting constants for the rest of the codebase.
   - Move the raw multi-line strings into the corresponding files, ensuring git history keeps context.

2. **Update imports**
   - `server/agent.py` & `server/reinforced_agent.py`: `from prompts.agents import CLASSIC_AGENT_PROMPT` etc.
   - `server/pipeline.py`: import selector prompts.
   - `server/tools/cypher.py`: import `CYPHER_GENERATION_TEMPLATE` from `prompts.tools`.
   - `builder_ai.py` / `verifier_ai.py`: import builder/verifier/fix prompts from `prompts.agents`.
   - Kor schemas inside verifier helpers: import from `prompts.schemas`.

3. **Share common prompts**
   - The two `agent_prompt` strings are nearly identical; consolidate into one constant + optional variants (e.g., `CLASSIC_AGENT_PROMPT`, `REINFORCED_AGENT_PROMPT` with small differences). If they are identical, point both modules to the same constant.

4. **Wire golden tests**
   - Ensure `tests/test_prompt_golden_master.py` (or its equivalent) imports the centralized modules so equality is enforced directly against the JSON golden master.

5. **Documentation**
   - Add a note in `README.md` (developer section) or create `CONTRIBUTING.md` snippet instructing contributors to edit prompt text in `server/prompts/` and run `scripts/create_prompt_snapshot.py` when they intentionally change a prompt.

6. **Future work**
   - Once prompts live in one module, consider splitting extremely long sections (e.g., example-heavy prompts) into external `.jinja` or `.md` files if editing them in Python becomes unwieldy.

#### Parity Subplan

1. Add regression tests that assert the current monolithic strings equal the soon-to-be-shared constants before any refactor. Keep them in `tests/test_prompt_equality.py`.
2. Perform the extraction so `server/agent.py`, `server/reinforced_agent.py`, builder/verifier modules, etc., import from the centralized definitions.
3. Keep the equality tests (they now verify the modules consume the shared constants) and continue running the golden-master test suite to ensure byte-for-byte parity.
4. Remove the temporary equality tests only after we are confident all prompts originate from the central module.

### Current Shared Blocks

- `agent_examples.txt` contains the entire “# Examples” block used by both classic and reinforced agents. It is loaded via `AGENT_EXAMPLES_BLOCK` in `server/prompts/agents.py`.
- `agent_guidance.txt` holds the “How to Process Tool Output / How to answer commentary” instructions and the notes/feedback section shared by both agents.
- The role/context section is generated via `_build_role_context(...)`, letting each agent inject its small customization (e.g., classic adds “Your name is Caïssa”).

### Next Targets

1. Apply the same extraction to the builder/verifier prompts so they reuse the common role/context/tool instructions where possible.
2. Consider reintroducing a lightweight equality/assertion test that ensures every prompt references the shared constants (preventing accidental re-duplication).
3. Document in the TODO list who owns each shared block so new prompts go through the same structure.

## Prompt TODOs

| Task | Severity / Gain | Ease of Implementation | Notes / File References |
| --- | --- | --- | --- |
| Split the monolithic agent prompt into separate, scoped templates and drop redundant ReAct boilerplate so each agent only loads what it needs. | High (prompt bloat affects every request) | Medium | `server/prompts/agents.py:3` (role/context, examples, guidance now shared; remaining work: builder/verifier prompts & small suffix differences) |
| ~~Fix contradictory or malformed examples (Example 7 color/position mismatch, Example 8/9 move drift, Example 10 bad coordinate) before they poison few-shot behavior.~~ | ✅ Done (PR pending) |  | `server/prompts/agents.py:160-220` |
| ~~Clean up Step 4/5 instructions so numbering is correct and the “skip unanswered questions” rule is unambiguous to reduce tool-call churn.~~ | ✅ Done (improved instructions + new snapshots) |  | `server/prompts/agents.py:400-430` |
| Add an explicit “None/N/A” option (or guidance) to the pipeline selector so it can refuse out-of-scope prompts instead of dispatching a wrong agent. | Medium | Low | `server/prompts/selectors.py:26-45` |
| ~~Align verifier selector examples with the allowed tool list (e.g., add `N/A` as a tool or update Example 2) to avoid runtime errors.~~ | ✅ Done (Example updated + notes) |  | `server/prompts/selectors.py:95-108` |
| ~~Fix typos/malformed JSON in the Cypher tool prompt examples and add a short injection/safety reminder to protect the schema from hostile input.~~ | ✅ Done (grammar fixes + injection guard) |  | `server/prompts/tools.py:42-219` |
| Centralize shared tool instructions and interaction tails (e.g., `TOOLS` block, `New input`/`agent_scratchpad`). | High | Medium | Shared across virtually every prompt; begin with classic/reinforced, then builder/verifier/pipeline as variants |`server/prompts/placeholders.py`, `server/prompts/text/*.txt`|
| Parameterize builder/verifier role/context/note sections to avoid duplicating JSON guidance and “Do not use a tool” caveats. | Medium | Medium | Builder now reuses shared placeholders for piece/color/board/relation bullets; verifier JSON prompt still needs equivalent treatment once we intentionally change its text | `server/prompts/text/builder_agent_prompt.txt`, `server/prompts/text/verifier_json_prompt.txt` |
| Deduplicate pipeline router headers (AGENTS/TOOLS list, “Do not execute…”, example formatting) into shared fragments. | Medium | Medium | Shared note blocks and example scaffolding now live in placeholders, leaving only agent-specific instructions to maintain | `server/prompts/text/pipeline_*.txt` |
| ~~Replace builder’s “How to get Final Answer” relationship descriptions with the shared relationship fragment.~~ | ✅ Done (shared placeholder now injected) |  | `server/prompts/text/builder_agent_prompt.txt` |
| After any prompt edit, regenerate the golden JSON via `python3 scripts/create_prompt_snapshot.py --git-ref <target>` so `tests/test_prompt_golden_master.py` stays green. | High (tests fail otherwise) | Low | `scripts/create_prompt_snapshot.py:1-120` |
| Add builder smoke regression tests (`tests/test_builder_agent.py`) covering `Builder.build_relations`, JSON parsing, and graph feature creation. | High (breakages currently invisible) | Medium | Ensures prompt-only edits can’t silently break builder runtime |
| Add pipeline wiring tests (`tests/test_pipeline_wiring.py`) exercising LangGraph tool mappings and `pipeline_history` bookkeeping. | High (protects selector/agent cohesion) | Medium | Validates `execute_tools` routes and agent selection |
| Add a pipeline→builder sentinel test (`tests/test_pipeline_builder_branch.py`) that monkeypatches builder to assert state transitions reach `\"End\"`. | High (catches branch regressions) | Medium | Covers LangGraph branch to builder agent |

Update this list as items are completed or new prompt-related work surfaces.
