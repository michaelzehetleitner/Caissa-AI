#!/usr/bin/env python3
"""
Measure how long it takes to populate tactics relations for a given FEN.

Example:
    PYTHONPATH=. python3 scripts/benchmark_tactics.py --fen "<FEN>" --iterations 3 --reuse
"""

from __future__ import annotations

import argparse
import os
import statistics
import time

from server import server as server_module
from server.neurosymbolicAI import NeuroSymbolic


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark tactic graph construction.")
    parser.add_argument("--fen", required=True, help="Forsyth-Edwards Notation to benchmark.")
    parser.add_argument(
        "--kb-path",
        default=os.getenv("KB_PATH", "server/neurosymbolicAI/symbolicAI/general.pl"),
        help="Path to the Prolog knowledge base.",
    )
    parser.add_argument("--iterations", type=int, default=1, help="Number of repetitions.")
    parser.add_argument(
        "--reuse",
        action="store_true",
        help="Reuse the shared NeuroSymbolic.symbolic instance (simulates /set_fen path).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ns = NeuroSymbolic()

    durations: list[float] = []

    for _ in range(args.iterations):
        symbolic = ns.symbolic if args.reuse else None
        start = time.perf_counter()
        server_module.add_tactics_to_graph(
            args.kb_path,
            args.fen,
            symbolic_instance=symbolic,
        )
        durations.append(time.perf_counter() - start)

    mean = statistics.mean(durations)
    pct99 = max(durations) if len(durations) == 1 else statistics.quantiles(durations, n=100)[-1]

    mode = "reused instance" if args.reuse else "fresh instance"
    print(f"Mode: {mode}")
    print(f"Iterations: {len(durations)}")
    print(f"Mean: {mean:.3f}s")
    print(f"p99: {pct99:.3f}s")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
