from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from tigrbl_atoms import protocol_scope
from tigrbl_kernel import asgi_dispatch
from tigrbl_atoms.protocol_scope import AsgiScope, AsgiScopeKind
from tigrbl_kernel.asgi_dispatch import (
    AsgiLifecycle,
    select_asgi_ingress,
    select_asgi_operation_miss,
)


@pytest.mark.parametrize(
    ("kind", "lifecycle", "default_scheme"),
    [
        (AsgiScopeKind.HTTP, AsgiLifecycle.REQUEST, None),
        (AsgiScopeKind.WEBSOCKET, AsgiLifecycle.WEBSOCKET_SESSION, "ws"),
        (
            AsgiScopeKind.WEBTRANSPORT,
            AsgiLifecycle.WEBTRANSPORT_SESSION,
            "webtransport",
        ),
        (AsgiScopeKind.LIFESPAN, AsgiLifecycle.APPLICATION, None),
    ],
)
def test_kernel_selects_carrier_plan_from_typed_scope(kind, lifecycle, default_scheme):
    plan = select_asgi_ingress(AsgiScope(kind))
    assert plan.lifecycle is lifecycle
    assert plan.default_scheme == default_scheme


@pytest.mark.parametrize(
    ("kind", "method_not_allowed", "status", "close_event"),
    [
        (AsgiScopeKind.HTTP, False, 404, None),
        (AsgiScopeKind.HTTP, True, 405, None),
        (AsgiScopeKind.WEBSOCKET, False, 4404, "websocket.close"),
        (AsgiScopeKind.WEBTRANSPORT, False, 4404, "webtransport.close"),
    ],
)
def test_kernel_owns_carrier_miss_outcome(
    kind, method_not_allowed, status, close_event
):
    miss = select_asgi_operation_miss(kind, method_not_allowed=method_not_allowed)
    assert miss.status_code == status
    assert miss.close_event == close_event


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", list(AsgiScopeKind))
async def test_kernel_entry_projects_once_before_selecting(monkeypatch, kind):
    scope = {"type": kind.value, "path": "/", "headers": []}
    calls = []
    receive = AsyncMock()
    send = AsyncMock()
    project = protocol_scope.project_asgi_scope
    app = SimpleNamespace(
        trace_sink=None,
        _handle_http_prelude=AsyncMock(return_value=False),
        _handle_lifespan=AsyncMock(),
    )
    entry = asgi_dispatch.KernelAsgiApp(app, None)

    def record_projection(raw):
        assert raw is scope
        projection = project(raw)
        calls.append(projection)
        return projection

    def record_selection(projection):
        assert calls == [projection] and calls[0] is projection
        calls.append(projection.kind)
        return select_asgi_ingress(projection)

    async def session_run(session, scope, invoke, snapshot):
        await invoke()

    monkeypatch.setattr(protocol_scope, "project_asgi_scope", record_projection)
    monkeypatch.setattr(asgi_dispatch, "select_asgi_ingress", record_selection)
    monkeypatch.setattr(asgi_dispatch.WebTransportSessionPlan, "run", session_run)
    monkeypatch.setattr(entry, "invoke", AsyncMock())

    await entry(scope, receive, send)

    assert calls == [AsgiScope(kind), kind]
    if kind is AsgiScopeKind.LIFESPAN:
        app._handle_lifespan.assert_awaited_once_with(scope, receive, send)
        entry.invoke.assert_not_called()
    else:
        entry.invoke.assert_awaited_once()
        assert entry.invoke.await_args.args[0].receive is receive


@pytest.mark.asyncio
async def test_kernel_entry_stops_at_invalid_scope(monkeypatch):
    def unexpected_selection(projection):
        pytest.fail("invalid raw scope reached ingress selection")

    monkeypatch.setattr(asgi_dispatch, "select_asgi_ingress", unexpected_selection)
    entry = asgi_dispatch.KernelAsgiApp(None, None)
    with pytest.raises(ValueError, match="unsupported ASGI scope type"):
        await entry({"type": "unknown"}, AsyncMock(), AsyncMock())
