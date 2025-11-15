# Prompt Centralization – Regression Test Plan

Goal: after moving every LangChain prompt into a centralized `server/prompts/` module (or external text files), ensure that chatbot behaviour stays identical. This plan focuses on automated checks we can add before/after the refactor so we can refactor with confidence.

---

## 1. Identify Behavioural Surfaces
- **API endpoints**: `/chatbot`, `/reinforced_chatbot`, `/neurosym`, `/legal_moves`, `/set_fen`, `/make_move`.
- **Agents and tools**: classic ReAct agent (`agent.py`), LangGraph pipeline (`pipeline.py`), builder/verifier agents, Cypher generator.
- **Prompt-specific outputs**: tool invocation traces (Thought/Action/Observation), generated Cypher, JSON emitted by builder/verifier, LangGraph decision nodes.

We will exercise each surface in tests to detect text drift or broken wiring.

## 2. Baseline Snapshot Tests (Before Refactor)
1. **Golden conversations**  
   - Create fixtures with deterministic seeds (set `OPENAI_API_KEY` to mock or use LangChain’s `FakeListLLM`) so responses are stable.  
   - Scripts:  
     - `tests/golden/test_classic_agent.py` hitting `/chatbot` with canned inputs (defend/threat question, board state query).  
     - `tests/golden/test_reinforced_pipeline.py` calling `pipeline.chat()` with identical prompts/FEN.  
   - Capture both final answers and the intermediate `Thought/Action` logs to compare later.

2. **Cypher generator snapshots**  
   - Exercise `tools/cypher.cypher_qa` with representative questions and assert generated Cypher exactly matches golden strings (strip whitespace).

3. **Builder/Verifier JSON snapshots**  
   - For builder: feed known relation description, compare JSON structure.  
   - For verifier: pass representative commentary; assert extracted statements + “fixed” text equal baselines.

4. **Kor schema extraction**  
   - Unit-test `verify_piece_position/relation/move_feature` helper functions with mocked symbolic outputs to ensure they still call into `Verifier` correctly and return expected structure.

Implementation detail: use `pytest` + `freezegun` + `monkeypatch` to substitute `ChatOpenAI` with LangChain’s `FakeListLLM`, so we don’t rely on live APIs.

## 3. Refactor-Specific Tests
1. **Prompt registry coverage**  
   - Add a test asserting every prompt constant exists in the new module(s).  
   - Ensure no `.from_template("""` string remains in the original files by running `rg` in tests (`pytest` can call `subprocess.run(["rg", ...])`).

2. **Import wiring**  
   - Tests that import each agent module and confirm the `PromptTemplate` uses the centralized constant (e.g., `assert agent.AGENT_PROMPT is prompts.AGENT_PROMPT`).  
   - Guard against circular imports with a simple `pytest.importorskip`.

## 4. Regression Verification After Refactor
1. Re-run all snapshot tests; differences should be zero. If diff occurs:
   - Confirm whether formatting (e.g., whitespace) changed; relax comparison to ignore whitespace if necessary.  
   - If actual logic changed, fix prompt wiring.

2. Add CI guard that fails when snapshot fixtures differ (use `pytest --snapshot-update` workflow).

3. Optional: add lightweight E2E test using `requests` against a test instance to ensure HTTP layer still responds 200 and bodies equal baselines.

## 5. Tooling & Automation
- **Test harness**: extend existing `pytest.ini` to include new `tests/golden/` directory.  
- **LLM Fakes**: create helper `tests/utils/fake_llm.py` that mimics ChatOpenAI and returns deterministic outputs so prompts don’t hit external services.  
- **Pre-commit hook**: add script `scripts/ensure_prompts_centralized.py` that scans for multi-line prompt literals; run in CI.

## 6. Rollout Steps
1. Implement fake LLM + baseline snapshot tests on current code.  
2. Confirm CI passes; collect and store golden outputs in repo.  
3. Perform prompt centralization refactor.  
4. Re-run tests locally and in CI; updates must show no diffs.  
5. Keep plan + test docs in `refactor/` for future reference.

Following this plan gives us confidence that moving prompt text will not subtly change agent behaviour.
