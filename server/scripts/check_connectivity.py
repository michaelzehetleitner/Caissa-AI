#!/usr/bin/env python3
"""
Utility script for debugging Caissa's backend connectivity.

Run this outside the sandbox (from your host machine) after activating the
virtual environment:

    source .venv/bin/activate
    python server/scripts/check_connectivity.py

Outputs a step-by-step report covering:
  1. Secret resolution via config.get_secret
  2. DNS lookup for the Neo4j host
  3. TCP connectivity to the Bolt port
  4. A simple Neo4j query executed through the official driver
  5. (Optional) A feature-check query for a specific piece/feature/target square
"""

from __future__ import annotations

import argparse
import json
import socket
import sys
import textwrap
import time
from contextlib import closing
from pathlib import Path
from urllib import error, request

from neo4j import GraphDatabase

# Ensure the server package (which holds config.py) is on sys.path
SERVER_ROOT = Path(__file__).resolve().parents[1]
if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVER_ROOT))

# Reuse the same secret-loading logic the server uses
from server.config import get_secret


def run_step(title: str, fn):
    print(f"\n=== {title} ===")
    start = time.perf_counter()
    try:
        result = fn()
    except Exception as exc:  # noqa: BLE001 - we want the full stack for diagnostics
        elapsed = time.perf_counter() - start
        print(f"[FAIL] ({elapsed:.2f}s) {exc.__class__.__name__}: {exc}")
        raise
    else:
        elapsed = time.perf_counter() - start
        print(f"[ OK ] ({elapsed:.2f}s) {result}")
        return result


def fetch_secrets():
    uri = get_secret("NEO4J_URI")
    user = get_secret("NEO4J_USERNAME")
    password = get_secret("NEO4J_PASSWORD")
    return {"uri": uri, "user": user, "password": "<hidden>"}


def resolve_dns(host: str):
    infos = socket.getaddrinfo(host, None)
    addresses = sorted({info[4][0] for info in infos})
    return ", ".join(addresses)


def check_tcp(host: str, port: int, timeout: float):
    with closing(socket.create_connection((host, port), timeout=timeout)):
        return f"Connected to {host}:{port}"


def check_neo4j(uri: str, user: str, password: str, cypher: str):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        with driver.session() as session:
            record = session.run(cypher).single()
            return dict(record) if record else "No records returned"
    finally:
        driver.close()


def check_feature(uri: str, user: str, password: str, piece: str, color: str, feature: str, square: str):
    cypher = textwrap.dedent(
        """
        MATCH (p:Piece {piece: $piece, color: $color})-[:Feature {feature: $feature}]->(s:Square {position: $square})
        RETURN p.piece AS piece, p.position AS from_square, s.position AS to_square, count(*) AS matches
        """
    )
    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        with driver.session() as session:
            record = session.run(
                cypher,
                piece=piece,
                color=color,
                feature=feature,
                square=square,
            ).single()
            if not record:
                return "No matching Feature relation"
            return dict(record)
    finally:
        driver.close()


def populate_fen(server_url: str, fen_string: str, timeout: float):
    endpoint = server_url.rstrip("/") + "/set_fen"
    payload = json.dumps({"fen_string": fen_string}).encode("utf-8")
    req = request.Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    opener = request.build_opener(request.ProxyHandler({}))  # bypass system proxies for localhost
    try:
        with opener.open(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return f"HTTP {resp.status}: {body[:200]}..."
    except error.HTTPError as http_err:
        detail = http_err.read().decode("utf-8", errors="ignore")
        raise error.HTTPError(
            http_err.url,
            http_err.code,
            f"{http_err.reason}: {detail[:200]}",
            http_err.headers,
            http_err.fp,
        )


def main():
    parser = argparse.ArgumentParser(description="Diagnose Neo4j/Graph connectivity for Caissa.")
    parser.add_argument("--host", help="Override host extracted from NEO4J_URI (e.g. a42ed0fc.databases.neo4j.io)")
    parser.add_argument("--port", type=int, default=7687, help="Bolt port (default: 7687)")
    parser.add_argument("--timeout", type=float, default=5.0, help="TCP timeout in seconds (default: 5)")
    parser.add_argument(
        "--quick-query",
        default="RETURN 1 AS ok",
        help="Cypher to run for the general connectivity test.",
    )
    parser.add_argument(
        "--feature-piece",
        default="pawn",
        help="Piece name for the optional feature check (default: pawn).",
    )
    parser.add_argument(
        "--feature-color",
        default="black",
        help="Piece color for the optional feature check (default: black).",
    )
    parser.add_argument(
        "--feature-name",
        default="move_defend",
        help="Feature name to inspect (default: move_defend).",
    )
    parser.add_argument(
        "--feature-square",
        default="a6",
        help="Destination square for the feature check (default: a6).",
    )
    parser.add_argument(
        "--skip-feature-check",
        action="store_true",
        help="Skip the optional feature relation query.",
    )
    parser.add_argument(
        "--populate-fen",
        metavar="FEN",
        help="If provided, POSTs the FEN to the local Caissa server's /set_fen endpoint before running the feature check.",
    )
    parser.add_argument(
        "--populate-timeout",
        type=float,
        default=30.0,
        help="Timeout (seconds) for the /set_fen request when using --populate-fen (default: 30).",
    )
    parser.add_argument(
        "--server-url",
        default="http://127.0.0.1:5000",
        help="Base URL for the local Caissa server (used when --populate-fen is set).",
    )
    args = parser.parse_args()

    secrets = run_step("Secrets", fetch_secrets)

    host = args.host
    if not host:
        host = secrets["uri"].split("://", 1)[-1].split(":", 1)[0]

    run_step("DNS Lookup", lambda: resolve_dns(host))
    run_step("TCP Handshake", lambda: check_tcp(host, args.port, args.timeout))
    run_step(
        "Neo4j Quick Query",
        lambda: check_neo4j(
            secrets["uri"],
            secrets["user"],
            get_secret("NEO4J_PASSWORD"),
            args.quick_query,
        ),
    )

    if args.populate_fen:
        run_step(
            "Populate FEN via /set_fen",
            lambda: populate_fen(args.server_url, args.populate_fen, args.populate_timeout),
        )

    if not args.skip_feature_check:
        run_step(
            "Feature Relation Check",
            lambda: check_feature(
                secrets["uri"],
                secrets["user"],
                get_secret("NEO4J_PASSWORD"),
                args.feature_piece,
                args.feature_color,
                args.feature_name,
                args.feature_square,
            ),
        )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("\nDiagnostics aborted due to the error above.", file=sys.stderr)
        sys.exit(1)
