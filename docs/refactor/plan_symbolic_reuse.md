## Goal

Speed up `/set_fen` (and any other entrypoints that call `add_tactics_to_graph`) by eliminating the repeated work of instantiating `Symbolic`, consulting the Prolog KB, and parsing the same FEN for every tactic. Currently `execute_tactic` does all of that per entry in the tactics list, leading to ~30 full Prolog initialisations and redundant Neo4j prep per request.

## Current Pain Points

1. **Repeated Prolog setup** – every tactic call creates a fresh `Symbolic`, calls `consult()`, and `parse_fen()` even though the data is identical.
2. **Duplicated Neo4j connections** – each `Symbolic` instance opens its own Neo4j driver and writes overlapping metadata, which adds latency.
3. **Sequential bottleneck** – after we dropped the `multiprocessing.Pool` (for determinism), the sequential loop exacerbates the redundant setup cost.

## Proposed Refactor Steps

1. **Introduce a reusable `SymbolicContext` helper**
   - Construct `Symbolic()` once per `/set_fen` invocation.
   - Call `consult(KB_PATH)` and `parse_fen(fen_string)` exactly once.
   - Hand out the prepared instance (or lightweight wrappers) to all tactic functions.

2. **Refactor `execute_tactic`**
   - Accept an already-prepared `Symbolic` object instead of building a new one.
   - Remove the internal `consult`/`parse_fen` calls (maybe keep a fallback for legacy callers).
   - Keep the logging so we still trace which tactic just ran.

3. **Update `add_tactics_to_graph`**
   - Build the `SymbolicContext` once.
   - Iterate through the tactic list, calling `execute_tactic(prepared_symbolic, ...)`.
   - Optionally batch errors so a single failing tactic doesn’t kill the whole loop.

4. **(Optional) Reintroduce light parallelism**
   - Once the shared context exists, we could revisit batching tactics by category (e.g., white vs black) using threads (not processes) to avoid reloading Prolog. This is secondary; the immediate win comes from reusing the context.

5. **Testing / Validation**
   - Add a small benchmark (or log timestamps) around `/set_fen` before/after the change.
   - Use the existing `server/scripts/check_connectivity.py --populate-fen … --populate-timeout …` to confirm the endpoint completes faster and the feature relations are still created.

## Notes / TODOs

- Guard the new logic with an environment flag during rollout (e.g., `CAISSA_SYMBOLIC_REUSE=1`) so we can fall back quickly if needed.
- Document the new flow in the README and mention that `execute_tactic` now expects a prepared context.
