from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from tigrbl_atoms.protocol_scope import AsgiScope, AsgiScopeKind


class AsgiLifecycle(str, Enum):
    REQUEST = "request"
    WEBSOCKET_SESSION = "websocket_session"
    WEBTRANSPORT_SESSION = "webtransport_session"
    APPLICATION = "application"


@dataclass(frozen=True, slots=True)
class AsgiIngressPlan:
    lifecycle: AsgiLifecycle
    default_scheme: str | None = None


_INGRESS_PLANS = {
    AsgiScopeKind.HTTP: AsgiIngressPlan(AsgiLifecycle.REQUEST),
    AsgiScopeKind.WEBSOCKET: AsgiIngressPlan(AsgiLifecycle.WEBSOCKET_SESSION, "ws"),
    AsgiScopeKind.WEBTRANSPORT: AsgiIngressPlan(
        AsgiLifecycle.WEBTRANSPORT_SESSION, "webtransport"
    ),
    AsgiScopeKind.LIFESPAN: AsgiIngressPlan(AsgiLifecycle.APPLICATION),
}


def select_asgi_ingress(projection: AsgiScope) -> AsgiIngressPlan:
    """Select the carrier lifecycle before operation dispatch."""
    return _INGRESS_PLANS[projection.kind]


@dataclass(frozen=True, slots=True)
class AsgiOperationMiss:
    status_code: int
    detail: str = ""
    close_event: str | None = None


_OPERATION_MISSES = {
    AsgiScopeKind.WEBSOCKET: AsgiOperationMiss(4404, close_event="websocket.close"),
    AsgiScopeKind.WEBTRANSPORT: AsgiOperationMiss(
        4404, close_event="webtransport.close"
    ),
}
_HTTP_MISS = AsgiOperationMiss(404, "No runtime operation matched request.")
_METHOD_NOT_ALLOWED = AsgiOperationMiss(405, "Method Not Allowed")


def select_asgi_operation_miss(
    scope_kind: str, *, method_not_allowed: bool = False
) -> AsgiOperationMiss:
    if method_not_allowed:
        return _METHOD_NOT_ALLOWED
    return _OPERATION_MISSES.get(scope_kind, _HTTP_MISS)
