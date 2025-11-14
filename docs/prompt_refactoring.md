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

## Regression Tests To Add
These are quick pytest modules that prevent prompt-only edits from silently breaking agents.

1. **Builder smoke test (`tests/test_builder_agent.py`)**
   - Monkeypatch `Symbolic` and `get_secret` to avoid external calls.
   - Instantiate `Builder()` and assert it exposes `build_relations`.
   - Patch the JSON parser to return a canned dict and assert `build_relations("dummy")`
     eventually calls `graph.build_feature`.
2. **Pipeline wiring test (`tests/test_pipeline_wiring.py`)**
   - Import `server.pipeline`, build a minimal `state` dict, and assert:
     * `execute_tools` routes `"Verify Piece Position"` to `verify_piece_position`.
     * `"Verify Piece Relation"` hits `verify_piece_relation`.
     * `"Verify Piece Move Feature"` hits `verify_move_relation`.
   - Include a test that `run_main({"input": "build a relation"})` stores `"Builder Agent"`
     in `pipeline_history`, ensuring prompt changes don’t desync selection.
3. **End-to-end sentinel (`tests/test_pipeline_builder_branch.py`)**
   - Monkeypatch `Builder.build_relations` to record the payload and return success.
   - Run the LangGraph workflow up to the builder branch with a dummy FEN input and ensure
     the state transitions to `"End"` with the expected final answer string.

## Ongoing Expectations
- Whenever prompts change, re-run both the snapshot tests and the new wiring/builder suites.
- Keep this document updated when the architecture evolves (e.g., if Builder or Verifier move to
  dedicated microservices, document the new smoke tests required).
