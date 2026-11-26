from __future__ import annotations

import ast
import inspect
import textwrap

from tigrbl_concrete._concrete._app import App


def test_app_call_only_delegates_raw_ingress_to_runtime() -> None:
    method = ast.parse(textwrap.dedent(inspect.getsource(App.__call__))).body[0]
    body = method.body
    assert len(body) == 1
    assert ast.unparse(body[0]) == "await self.runtime.dispatch_asgi(self, scope, receive, send)"
