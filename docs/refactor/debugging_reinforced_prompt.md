## Debugging the Reinforced `/reinforced_chatbot` Prompt

Use this checklist whenever the Reinforced agent falls back to “Sorry, I do not know the answer!” or the pipeline throws `commentary_agent_outcome` errors.

1. **Seed the knowledge graph**
   ```bash
   source .venv/bin/activate
   export CAISSA_SKIP_LLM=1  # optional: skip LLM weights during debugging
   python server/server.py
   ```
   In a second terminal (same venv) run:
   ```bash
   python server/scripts/check_connectivity.py \
     --populate-fen "rnbqk1nr/ppp1ppbp/3p2p1/6N1/3PP3/8/PPP2PPP/RNBQKB1R b KQkq - 1 4" \
     --populate-timeout 120
   ```
   Wait until the script prints `Populate FEN via /set_fen ... [ OK ]`. This confirms Neo4j has all tactic relations for that FEN.

2. **Inspect GraphCypher QA logs**
   - Every time the Reinforced agent calls the Cypher tool you’ll now see logs like:
     ```
     [CypherQA] Incoming question/input: ...
     [CypherQA] Context size: N
     [CypherQA] Raw result: {'context': [...]}
     ```
   - If `Context size` stays `0`, copy the question from the log and test it manually with `cypher-shell` to see why the query returns nothing.

3. **Handle missing commentary gracefully**
   - The pipeline now skips the verifier if `commentary_agent_outcome` is missing, so you’ll see `run_verifier: missing commentary_agent_outcome`. When that happens, focus on the Reinforced agent logs to see why it failed (usually because the Cypher tool returned empty context).

4. **Replay the prompt**
   - Use `curl` (ensure the JSON is a single line) to replay the chess question:
     ```bash
     curl -X POST http://127.0.0.1:5000/reinforced_chatbot \
       -H "Content-Type: application/json" \
       -d '{"prompt":"<your chess question>","fen":"<fen>"}'
     ```
   - Watch the server terminal: you should now see the `[CypherQA]` diagnostics followed by the final commentary instead of the fallback.

5. **If problems persist**
   - Confirm `/set_fen` is still returning `200` in the server log.
   - Re-run the connectivity script to verify the feature relation exists.
   - Repeat step 2 to ensure the Cypher tool is generating the expected query.
