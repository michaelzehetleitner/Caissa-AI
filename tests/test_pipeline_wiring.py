from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PIPELINE_PATH = REPO_ROOT / "server" / "pipeline.py"


def _verifier_tools_assign_node() -> ast.Assign:
    module = ast.parse(PIPELINE_PATH.read_text())
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "verifier_tools":
                    return node
    raise AssertionError("verifier_tools assignment not found in pipeline.py")


def test_verifier_tools_use_single_state_argument() -> None:
    assign = _verifier_tools_assign_node()
    list_value = assign.value
    assert isinstance(list_value, ast.List), "verifier_tools should be defined as a list."

    expected_funcs = [
        "verify_piece_position",
        "verify_piece_relation",
        "verify_move_relation",
    ]
    assert len(list_value.elts) == len(
        expected_funcs
    ), "verifier_tools should expose three entries."

    for call_node, expected_func in zip(list_value.elts, expected_funcs):
        assert isinstance(call_node, ast.Call), "Each verifier tool must be constructed via Tool()."
        func_keyword = next(
            (kw for kw in call_node.keywords if kw.arg == "func"), None
        )
        assert func_keyword is not None, "Tool definition missing func kwarg."
        lambda_node = func_keyword.value
        assert isinstance(lambda_node, ast.Lambda), "Tool func must be a lambda."
        arg_names = [arg.arg for arg in lambda_node.args.args]
        assert (
            len(arg_names) == 1
        ), "Verifier tool lambdas should accept a single LangGraph state argument."

        assert isinstance(lambda_node.body, ast.Call), "Lambda must call the matching verifier helper."
        called_func = lambda_node.body.func
        assert isinstance(called_func, ast.Name), "Verifier helper should be referenced directly."
        assert (
            called_func.id == expected_func
        ), f"Verifier lambda should call {expected_func}."

        # Ensure the lambda forwards the same state argument
        assert len(lambda_node.body.args) == 1, "Verifier helper should receive the state dict."
        forwarded_arg = lambda_node.body.args[0]
        assert isinstance(
            forwarded_arg, ast.Name
        ), "Forwarded argument should be the lambda parameter."
        assert (
            forwarded_arg.id == arg_names[0]
        ), "Verifier lambda must forward its only parameter to the helper."
