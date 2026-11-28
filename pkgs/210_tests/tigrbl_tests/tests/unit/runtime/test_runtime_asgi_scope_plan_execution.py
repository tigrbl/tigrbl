from types import SimpleNamespace

import pytest

from tigrbl_atoms.protocol_scope import AsgiScopeKind
from tigrbl_kernel import asgi_dispatch
from tigrbl_kernel.webtransport_session_plan import WebTransportSessionPlan


@pytest.mark.asyncio
async def test_kernel_executes_its_carrier_selection(monkeypatch):
    scope = {"type": "lifespan"}
    calls = []
    received = object()
    sent = object()

    async def run(session_plan, actual_scope, invoke, snapshot):
        assert actual_scope is scope
        await invoke()

    async def invoke(self, env):
        calls.append((env.scope, env.receive, env.send))

    def select(projected):
        assert projected.kind is AsgiScopeKind.LIFESPAN
        return asgi_dispatch.AsgiIngressPlan(asgi_dispatch.AsgiLifecycle.WEBTRANSPORT_SESSION)

    monkeypatch.setattr(asgi_dispatch, "select_asgi_ingress", select)
    monkeypatch.setattr(WebTransportSessionPlan, "run", run)
    monkeypatch.setattr(asgi_dispatch.KernelAsgiApp, "invoke", invoke)
    entry = asgi_dispatch.KernelAsgiApp(SimpleNamespace(trace_sink=None), None)
    await entry(scope, received, sent)
    assert calls == [(scope, received, sent)]
