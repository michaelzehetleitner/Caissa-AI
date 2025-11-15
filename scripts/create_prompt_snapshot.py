#!/usr/bin/env python3
"""
Create a JSON snapshot of all long-form prompts so we can track them as a
golden master referenced by tests.
"""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional


@dataclass(frozen=True)
class PromptSpec:
    """Configuration describing a single prompt to extract."""

    id: str
    path: str
    target: str
    scope: Optional[str] = None


PROMPT_SPECS: List[PromptSpec] = [
    PromptSpec("server.agent.agent_prompt", "server/agent.py", "agent_prompt"),
    PromptSpec(
        "server.neurosymbolicAI.builder.agent_prompt",
        "server/neurosymbolicAI/builder_ai.py",
        "self.agent_prompt",
        scope="Builder.__init__",
    ),
    PromptSpec(
        "server.neurosymbolicAI.verifier.agent_prompt",
        "server/neurosymbolicAI/verifier_ai.py",
        "self.agent_prompt",
        scope="Verifier.__init__",
    ),
    PromptSpec(
        "server.neurosymbolicAI.verifier.fix_agent_prompt",
        "server/neurosymbolicAI/verifier_ai.py",
        "self.fix_agent_prompt",
        scope="Verifier.__init__",
    ),
    PromptSpec("server.pipeline.main_prompt", "server/pipeline.py", "main_prompt"),
    PromptSpec(
        "server.pipeline.verifier_prompt", "server/pipeline.py", "verifier_prompt"
    ),
    PromptSpec(
        "server.reinforced_agent.agent_prompt",
        "server/reinforced_agent.py",
        "agent_prompt",
    ),
    PromptSpec(
        "server.tools.cypher.CYPHER_GENERATION_TEMPLATE",
        "server/tools/cypher.py",
        "CYPHER_GENERATION_TEMPLATE",
    ),
]


def group_specs_by_path() -> Dict[str, List[PromptSpec]]:
    grouped: Dict[str, List[PromptSpec]] = {}
    for spec in PROMPT_SPECS:
        grouped.setdefault(spec.path, []).append(spec)
    return grouped


class PromptCollector(ast.NodeVisitor):
    """AST visitor that extracts prompt literals based on PromptSpec."""

    def __init__(
        self, file_path: Path, source: str, specs: Iterable[PromptSpec]
    ) -> None:
        self.file_path = file_path
        self.source = source
        self.tree = ast.parse(source, filename=str(file_path))
        self.scope_stack: List[str] = []
        self.specs = list(specs)
        self.spec_index: Dict[str, List[PromptSpec]] = {}
        for spec in self.specs:
            self.spec_index.setdefault(spec.target, []).append(spec)
        self.named_strings: Dict[str, str] = {}
        self.results: Dict[str, Dict[str, Optional[str]]] = {}

    def collect(self) -> Dict[str, Dict[str, Optional[str]]]:
        self.visit(self.tree)
        return self.results

    # Helpers ------------------------------------------------------------------
    def current_scope(self) -> Optional[str]:
        if not self.scope_stack:
            return None
        return ".".join(self.scope_stack)

    def _target_repr(self, node: ast.expr) -> Optional[str]:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            base = self._target_repr(node.value)
            if base:
                return f"{base}.{node.attr}"
        return None

    def _literal(self, node: ast.AST) -> Optional[str]:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        if isinstance(node, ast.JoinedStr):
            return self._render_joined_str(node)
        if isinstance(node, ast.Name):
            return self.named_strings.get(node.id)
        return None

    def _render_joined_str(self, node: ast.JoinedStr) -> str:
        parts: List[str] = []
        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                parts.append(value.value)
            elif isinstance(value, ast.FormattedValue):
                segment = ast.get_source_segment(self.source, value.value)
                if not segment:
                    segment = ast.unparse(value.value)
                fmt = ""
                if value.format_spec:
                    fmt = ":" + self._render_joined_str(value.format_spec)
                conv = ""
                if value.conversion != -1:
                    conv = f"!{chr(value.conversion)}"
                parts.append(f"{{{segment}{conv}{fmt}}}")
            else:
                segment = ast.get_source_segment(self.source, value)
                if not segment:
                    segment = ast.unparse(value)
                parts.append(segment)
        return "".join(parts)

    def _prompt_template_literal(self, node: ast.AST) -> Optional[str]:
        if not isinstance(node, ast.Call):
            return None
        func = node.func
        if not (
            isinstance(func, ast.Attribute)
            and func.attr == "from_template"
            and isinstance(func.value, ast.Name)
            and func.value.id == "PromptTemplate"
        ):
            return None
        template_node: Optional[ast.AST] = None
        if node.args:
            template_node = node.args[0]
        else:
            for keyword in node.keywords:
                if keyword.arg == "template":
                    template_node = keyword.value
                    break
        if template_node is None:
            return None
        return self._literal(template_node)

    def _extract_prompt(self, value: ast.AST) -> Optional[str]:
        template = self._prompt_template_literal(value)
        if template is not None:
            return template
        return self._literal(value)

    # Visitor overrides --------------------------------------------------------

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.scope_stack.append(node.name)
        self.generic_visit(node)
        self.scope_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.scope_stack.append(node.name)
        self.generic_visit(node)
        self.scope_stack.pop()

    def visit_Assign(self, node: ast.Assign) -> None:
        literal_value = self._literal(node.value)
        if literal_value is not None:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.named_strings[target.id] = literal_value

        for target in node.targets:
            target_label = self._target_repr(target)
            if not target_label:
                continue
            specs = self.spec_index.get(target_label, [])
            for spec in specs:
                if spec.id in self.results:
                    continue
                if spec.scope and spec.scope != self.current_scope():
                    continue
                text = self._extract_prompt(node.value)
                if text is None:
                    continue
                self.results[spec.id] = {
                    "path": spec.path,
                    "target": spec.target,
                    "scope": spec.scope,
                    "text": text,
                }
        self.generic_visit(node)


def read_source(repo_root: Path, relative_path: str, git_ref: Optional[str]) -> str:
    if git_ref:
        cmd = [
            "git",
            "-C",
            str(repo_root),
            "show",
            f"{git_ref}:{relative_path}",
        ]
        try:
            return subprocess.check_output(cmd).decode("utf-8")
        except subprocess.CalledProcessError as exc:  # pragma: no cover - bubble up
            raise RuntimeError(
                f"git show failed for {relative_path} at {git_ref}: "
                f"{exc.output.decode().strip()}"
            )
    file_path = repo_root / relative_path
    if not file_path.exists():
        raise FileNotFoundError(f"Cannot find {relative_path}")
    return file_path.read_text(encoding="utf-8")


def create_snapshot(repo_root: Path, git_ref: Optional[str]) -> OrderedDict:
    snapshot: Dict[str, Dict[str, Optional[str]]] = {}
    for relative_path, specs in group_specs_by_path().items():
        source = read_source(repo_root, relative_path, git_ref)
        collector = PromptCollector(repo_root / relative_path, source, specs)
        snapshot.update(collector.collect())

    missing = [spec.id for spec in PROMPT_SPECS if spec.id not in snapshot]
    if missing:
        raise RuntimeError(
            "Failed to extract prompts for: " + ", ".join(sorted(missing))
        )

    ordered = OrderedDict()
    for spec in PROMPT_SPECS:
        ordered[spec.id] = snapshot[spec.id]
    return ordered


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a JSON snapshot of all long-form prompts."
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("tests/golden_prompts/prompts.json"),
        help="File to write (default: %(default)s).",
    )
    parser.add_argument(
        "--git-ref",
        type=str,
        default=None,
        help="Optional git ref to read from, e.g. origin/main.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repository root (defaults to this script's grandparent).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = args.root or Path(__file__).resolve().parents[1]
    snapshot = create_snapshot(repo_root, args.git_ref)

    if args.git_ref:
        commit_ref = args.git_ref
    else:
        commit_ref = "HEAD"

    commit_hash = (
        subprocess.check_output(
            ["git", "-C", str(repo_root), "rev-parse", commit_ref],
            stderr=subprocess.STDOUT,
        )
        .decode("utf-8")
        .strip()
    )

    payload = OrderedDict(
        metadata={
            "git_ref": args.git_ref or "WORKING_TREE",
            "commit": commit_hash,
        },
        prompts=snapshot,
    )

    output_path = args.output
    if not output_path.is_absolute():
        output_path = repo_root / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    suffix = f" from {args.git_ref}" if args.git_ref else ""
    try:
        rel = output_path.relative_to(repo_root)
    except ValueError:
        rel = output_path
    print(f"Wrote {len(snapshot)} prompts to {rel}{suffix}")


if __name__ == "__main__":
    main()
