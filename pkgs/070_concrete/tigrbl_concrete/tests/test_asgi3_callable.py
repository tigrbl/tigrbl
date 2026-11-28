import ast
from pathlib import Path


APP_SOURCE_PATH = (
    Path(__file__).resolve().parents[1] / "tigrbl_concrete" / "_concrete" / "_app.py"
)


def _get_call_method_node() -> ast.AsyncFunctionDef:
    module = ast.parse(APP_SOURCE_PATH.read_text(encoding="utf-8"))

    for node in module.body:
        if isinstance(node, ast.ClassDef) and node.name == "App":
            for item in node.body:
                if isinstance(item, ast.AsyncFunctionDef) and item.name == "__call__":
                    return item

    msg = "App.__call__ async method not found"
    raise AssertionError(msg)


def test_app_call_signature_matches_asgi3() -> None:
    call_method = _get_call_method_node()
    arg_names = [arg.arg for arg in call_method.args.args]

    assert arg_names == ["self", "scope", "receive", "send"]


def test_app_call_delegates_asgi3_to_runtime() -> None:
    call_method = _get_call_method_node()

    assert len(call_method.body) == 1
    delegation = call_method.body[0]
    assert isinstance(delegation, ast.Expr)
    assert isinstance(delegation.value, ast.Await)
    assert ast.unparse(delegation.value.value) == (
        "self.runtime.dispatch_asgi(scope, receive, send)"
    )
