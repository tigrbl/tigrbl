from types import SimpleNamespace

import pytest

from tigrbl_atoms.protocol_scope import AsgiScopeKind, project_asgi_scope
from tigrbl_kernel import asgi_dispatch
from tigrbl_runtime.runtime import Runtime


@pytest.mark.asyncio
async def test_runtime_executes_the_kernel_selection(monkeypatch):
    scope = {"type": "lifespan"}
    calls = []

    async def handler(actual_scope, actual_receive, actual_send):
        calls.append((actual_scope, actual_receive, actual_send))

    def unexpected(*args):
        pytest.fail("Runtime selected a different ingress path")

    app = SimpleNamespace(
        trace_sink=None,
        _handle_http=unexpected,
        _handle_websocket=unexpected,
        _handle_webtransport=handler,
        _handle_lifespan=unexpected,
    )
    received = object()
    sent = object()
    selected = asgi_dispatch.AsgiIngressPlan(
        asgi_dispatch.AsgiLifecycle.WEBTRANSPORT_SESSION
    )

    def select(projected):
        assert projected.kind is AsgiScopeKind.LIFESPAN
        return selected

    monkeypatch.setattr(asgi_dispatch, "select_asgi_ingress", select)
    await Runtime().dispatch_asgi(app, scope, received, sent)
    assert calls == [(scope, received, sent)]
    assert project_asgi_scope(scope).kind is AsgiScopeKind.LIFESPAN
