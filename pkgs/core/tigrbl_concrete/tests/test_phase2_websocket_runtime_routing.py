from __future__ import annotations

import ast
from pathlib import Path


APP_SOURCE_PATH = (
    Path(__file__).resolve().parents[1] / "tigrbl_concrete" / "_concrete" / "_app.py"
)


def test_app_call_routes_websocket_scopes_through_runtime_invoke() -> None:
    module = ast.parse(APP_SOURCE_PATH.read_text(encoding="utf-8"))

    call_method = None
    for node in module.body:
        if isinstance(node, ast.ClassDef) and node.name == "App":
            for item in node.body:
                if isinstance(item, ast.AsyncFunctionDef) and item.name == "__call__":
                    call_method = item
                    break
    assert call_method is not None

    websocket_branch = None
    for stmt in call_method.body:
        if isinstance(stmt, ast.If) and isinstance(stmt.test, ast.Compare):
            compare = stmt.test
            if (
                isinstance(compare.left, ast.Name)
                and compare.left.id == "scope_type"
                and compare.comparators
                and isinstance(compare.comparators[0], ast.Constant)
                and compare.comparators[0].value == "websocket"
            ):
                websocket_branch = stmt
                break

    assert websocket_branch is not None
    branch_src = ast.unparse(websocket_branch)
    assert "self.invoke(env)" in branch_src
    assert "_handle_websocket" not in branch_src
