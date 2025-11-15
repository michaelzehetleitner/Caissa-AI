# Caïssa test suite

This folder groups the narrow pytest coverage we currently have for the server-side code. The tests rely on the fakes installed in `tests/conftest.py`, so they run without Neo4j, Prolog, or any LLM credentials.

## Running the tests

- Install the backend dependencies (or at minimum `pytest`) in a Python ≥3.10 environment.
- From the repo root run `python -m pytest tests`.
- `tests/conftest.py` stubs heavy third-party modules and exports `CAISSA_SKIP_LLM=1`, so the suite stays offline-friendly.

## What each test covers

- `test_prompt_golden_master.py` – imports every prompt constant from `server.prompts.*` and compares it to the canonical JSON in `tests/golden_prompts/prompts.json`. Update that JSON via `python scripts/create_prompt_snapshot.py --git-ref <commit>` whenever a prompt is intentionally edited.
- `test_builder_agent.py` – exercises `server.neurosymbolicAI.builder_ai.Builder.build_relations`, ensuring the JSON output parser is used and parsed moves reach `Graph.build_feature`.
- `test_add_tactics_to_graph.py` – checks that `server.server.add_tactics_to_graph` reuses a single `Symbolic` instance (no redundant `consult`/`parse_fen` calls) and correctly hands that instance to every tactic.
- `test_graph_and_cypher.py` – reloads `server.graph` and `server.tools.cypher` with monkeypatched LangChain/Neo4j hooks to verify that graph initialization records failures and that `cypher_qa` fans out through `GraphCypherQAChain`.
- `test_pipeline_runtime.py` – runs `server.pipeline.run_verifier` and `execute_tools` with stubbed LangGraph components to cover status transitions, error handling, and tool dispatch.
- `test_pipeline_wiring.py` – asserts the LangGraph wiring routes `"Verify Piece Position"` to the right helper and that `run_main` records when the Builder branch is chosen.
- `test_pipeline_builder_branch.py` – sanity-checks the builder branch state machine (`build_relation`) so that invoking the builder returns `"End"` plus a final answer and writes to `pipeline_history`.

## Supporting assets

- `tests/golden_prompts/prompts.json` stores the extracted prompt canon (metadata + text). Keep it in sync any time a prompt constant changes.
- `tests/__pycache__/` can be ignored; it only holds interpreter artefacts.
- `tests/utils/` is currently empty but is reserved for shared fakes/helpers (as suggested in `docs/refactor/prompt_refactor_tests_plan.md`).

## Known coverage gaps

- No HTTP-level smoke tests or ChessQA benchmarks are automated yet, even though `docs/chessqa_integration_plan.md` (#L5-L65) outlines how to add them.
- Planned suites such as builder/pipeline snapshots, verifier JSON checks, and fake LLM harnesses are documented in `docs/prompt_refactoring.md` (#L25-L70) and `docs/refactor/prompt_refactor_tests_plan.md` (#L7-L63) but not implemented.
- The client (Next.js) and observability/evaluation metrics remain untested, mirroring the gaps called out in `docs/documentation_improvement_suggestions.md:65` and `docs/rough_conceptual_improvement_plan.md:33-47`.

## TODOs

- [ ] Expand the builder/pipeline coverage beyond the existing smoke tests by adding the deeper LangGraph sentinel + wiring assertions described earlier (builder smoke, pipeline wiring, builder-branch sentinel) so we capture regressions with golden state rather than basic invocation success.
- [ ] Create golden conversation suites (`tests/golden/test_classic_agent.py`, `tests/golden/test_reinforced_pipeline.py`) plus Cypher and builder/verifier JSON snapshots as laid out in `docs/refactor/prompt_refactor_tests_plan.md:14-33`.
- [ ] Introduce prompt-registry coverage tests that scan for stray multiline literals and confirm every agent imports the centralized constants (`docs/refactor/prompt_refactor_tests_plan.md:34-42`).
- [ ] Build a reusable fake-LLM harness (`tests/utils/fake_llm.py`) and pytest config for golden directories so agent tests stay deterministic (`docs/refactor/prompt_refactor_tests_plan.md:52-55`).
- [ ] Add HTTP-level smoke tests hitting `/chatbot`, `/reinforced_chatbot`, `/neurosym`, `/legal_moves`, `/set_fen`, and `/make_move` to ensure the Flask layer respects the safety pipeline (`docs/refactor/prompt_refactor_tests_plan.md:7-11`).
- [ ] Implement the ChessQA benchmark runner + assertions to measure accuracy/error breakdowns automatically (`docs/chessqa_integration_plan.md:5-61`).
- [ ] Cover the verification helpers (`verify_piece_position`, `verify_piece_relation`, `verify_move_relation`) with targeted tests so we can enforce the CRITIC loop behaviour noted in `docs/rough_conceptual_improvement_plan.md:33-47`.
- [ ] Add unit tests for `reflex_checkpoint`, `selection_checkpoint`, `should_continue`, and `chat()` in `server/pipeline.py` to verify LangGraph state transitions and reflex retries without relying solely on smoke tests.
- [ ] Extend `server/neurosymbolicAI/verifier_ai.py` coverage by stubbing the Kor chains and fix agent so we can assert the JSON extraction, fallback repairs, and Symbolic checks behave deterministically.
- [ ] Tighten `server/neurosymbolicAI/builder_ai.py` tests around `_load_structured_response` and failure cases (missing relationships, empty `find_moves`) to ensure builder errors surface predictably.
- [ ] Exercise `server/neurosymbolicAI/neurosymbolic_ai.py`’s `suggest()` edge cases (missing FEN, CAISSA_SKIP_LLM=1, invalid UCI) using fakes for `ChessGPT` and `Symbolic`.
- [ ] Add Flask route tests for `/legal_moves`, `/chatbot`, `/reinforced_chatbot`, `/neurosym`, `/make_move`, and `/set_fen` that patch `ns`, `chat`, `generate_response`, and `add_tactics_to_graph` so HTTP error handling and side effects are covered.
- [ ] Unit-test `scripts/create_prompt_snapshot.py` with synthetic Python files to guarantee new prompt constants are captured and metadata stays consistent.
