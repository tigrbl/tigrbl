import pytest

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
