# ChessQA Integration Plan

Plan for building an interface between Caïssa and the `other_repos/chessqa-benchmark` suite so we can run Caïssa on the benchmark and quantify performance.

## 1. Objectives
- Drive Caïssa’s `/reinforced_chatbot` endpoint with ChessQA tasks (FEN + prompt) without manual intervention.
- Enforce ChessQA’s strict output formats (`FINAL ANSWER: ...`) so responses can be auto-graded by the benchmark scripts.
- Produce accuracy/cost/error breakdowns per ChessQA category to highlight strengths/weaknesses of Caïssa’s neuro‑symbolic stack.

## 2. Prerequisites
1. **Local services**: Caïssa backend running (Flask + Neo4j/Prolog) with `KB_PATH` configured; ensure `/reinforced_chatbot` accepts `{prompt, fen}` and returns commentary.
2. **Benchmark assets**: Verify the JSONL files under `other_repos/chessqa-benchmark/benchmark/` are accessible; optional re-generation requires the large Lichess datasets listed in that repo’s README.
3. **Environment**: Python ≥3.9 with access to both Caïssa dependencies and ChessQA requirements (mainly `python-chess`, `tqdm`). Keep network/API keys (OpenAI, etc.) available if Caïssa depends on them.

## 3. High-Level Architecture
```
ChessQA JSONL → Loader → Prompt Formatter ┐
                                           ├─> Caïssa Runner → Response Normalizer → ChessQA Evaluator → Stats
FEN/context  → Loader → FEN Extractor     ┘
```
- **Loader & formatter**: Reuse `load_tasks`, `format_prompt`, and `get_context` from `other_repos/chessqa-benchmark/eval/run_openrouter.py`.
- **Caïssa runner**: Small Python client that batches tasks, POSTs to `/reinforced_chatbot`, and records raw responses.
- **Normalizer**: Ensures each response ends with `FINAL ANSWER: <value>` matching the expected answer type (single token, multi-list, MCQ letter).
- **Evaluator**: Call ChessQA’s `extract_answer` and `evaluate_answer_with_error_type` to compute per-task correctness and aggregate statistics.

## 4. Implementation Steps
1. **Scaffold runner package**
   - Create `scripts/chessqa_runner/` (or similar) with a `requirements.txt` referencing ChessQA’s lightweight deps (`chess`, `tqdm`, `requests`).
   - Add a CLI entry point (`python scripts/chessqa_runner/main.py --dataset structural --limit 100 --output results/caissa_structural.jsonl`).

2. **Reuse ChessQA helpers**
   - Import `load_tasks`, `format_prompt`, `extract_answer`, `evaluate_answer_with_error_type` directly from the ChessQA repo (mind relative paths or package them via a local module import).
   - Support flags mirroring ChessQA (`--add-context`, `--N-samples-per-task`, etc.) to stay compatible with future datasets.

3. **Bridge to Caïssa**
   - For each task:
     - Extract `fen` from `task["input"]` (strip anything after `|` like `fen | e2e4`).
     - Build POST payload `{ "prompt": formatted_prompt, "fen": fen_clean }`.
     - Call `http://localhost:<port>/reinforced_chatbot` (port from `.env` or CLI flag).
     - Handle timeouts/retries, log failed task IDs for later reruns.

4. **Response normalization**
   - Caïssa currently outputs descriptive text without mandatory `FINAL ANSWER` syntax. Introduce one of:
     1. Prompt tweak: wrap the formatted ChessQA prompt in instructions that force Caïssa to conclude with the exact `FINAL ANSWER: ...` line.
     2. Post-processor: if Caïssa returns structured data (e.g., verified statements), convert to the expected format before saving.
   - For Structural tasks, consider adding a dedicated tool that queries the symbolic model (`Symbolic` methods already enumerate pieces/legal moves) to build deterministic answers rather than prose.

5. **Logging & persistence**
   - Save each result as a JSON object mirroring ChessQA’s schema (`task` fields + `inference` dict containing prompt, response, extraction result, correctness, error type, latency).
   - Produce summary stats JSON (`*_stats.json`) using ChessQA’s `calculate_total_usage` helper, substituting Caïssa-specific metrics (latency instead of token cost, etc.).

6. **Reporting**
   - Extend Caïssa’s README or docs with instructions: how to start services, run the benchmark (`python scripts/chessqa_runner/main.py --dataset-root other_repos/chessqa-benchmark/benchmark`), and interpret outputs.
   - Optionally generate markdown/CSV leaderboard snapshots for each category to track improvements over time.

## 5. Validation Checklist
- [ ] Smoke-test single task per category; confirm Caïssa responds and extraction succeeds.
- [ ] Run a small batch (e.g., 20 tasks) to ensure retries, logging, and stats work.
- [ ] Evaluate full benchmark; inspect error breakdowns (format errors vs wrong answers) to prioritize model or prompt tweaks.
- [ ] Document known gaps (e.g., Position Judgement needs engine evals) so results are contextualized.

## 6. Stretch Goals
1. **Category-specific adapters**: tailor prompts/tools so Caïssa leverages its strengths (e.g., call neurosymbolic `suggest` for Short Tactics, dedicated query builder for Structural).
2. **Automation hook**: integrate runner into CI or a nightly job that persists scores and highlights regressions.
3. **Leaderboard contribution**: once Caïssa outputs align with ChessQA’s submission format, publish results or compare against the public leaderboard.
