from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = REPO_ROOT / "server" / "neurosymbolicAI" / "builder_ai.py"


def _builder_class_node() -> ast.ClassDef:
    module = ast.parse(BUILDER_PATH.read_text())
    for node in module.body:
        if isinstance(node, ast.ClassDef) and node.name == "Builder":
            return node
    raise AssertionError("Builder class definition not found in builder_ai.py")


def test_builder_exposes_build_relations_method() -> None:
    builder_cls = _builder_class_node()
    method_names = {
        node.name for node in builder_cls.body if isinstance(node, ast.FunctionDef)
    }
    assert (
        "build_relations" in method_names
    ), "Builder must define build_relations() so the pipeline can invoke it."


def test_build_relations_accepts_user_input_argument() -> None:
    builder_cls = _builder_class_node()
    for node in builder_cls.body:
        if isinstance(node, ast.FunctionDef) and node.name == "build_relations":
            # Expect at least (self, input_text)
            arg_count = len(node.args.args)
            assert (
                arg_count >= 2
            ), "build_relations() should accept the relation description in addition to self."
            return
    raise AssertionError("build_relations() definition missing from Builder.")
