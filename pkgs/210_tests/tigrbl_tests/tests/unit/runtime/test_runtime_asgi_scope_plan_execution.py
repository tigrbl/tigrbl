from types import SimpleNamespace

import pytest

from tigrbl_atoms.protocol_scope import AsgiScopeKind, project_asgi_scope
from tigrbl_kernel import asgi_dispatch
from tigrbl_kernel.webtransport_session_plan import WebTransportSessionPlan
from tigrbl_runtime.runtime import Runtime


@pytest.mark.asyncio
async def test_runtime_executes_the_kernel_selection(monkeypatch):
    scope = {"type": "lifespan"}
    calls = []

    async def run(session_plan, actual_scope, invoke, snapshot):
        assert actual_scope is scope
        await invoke()

    async def invoke(runtime, actual_app, env):
        assert actual_app is app
        calls.append((env.scope, env.receive, env.send))

    def unexpected(*args):
        pytest.fail("Runtime selected a different ingress path")

    app = SimpleNamespace(
        trace_sink=None,
        _handle_http=unexpected,
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
    monkeypatch.setattr(WebTransportSessionPlan, "run", run)
    monkeypatch.setattr(Runtime, "invoke_app", invoke)
    await Runtime().dispatch_asgi(app, scope, received, sent)
    assert calls == [(scope, received, sent)]
    assert project_asgi_scope(scope).kind is AsgiScopeKind.LIFESPAN
