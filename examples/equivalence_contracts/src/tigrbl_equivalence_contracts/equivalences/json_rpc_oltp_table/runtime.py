"""Runtime proof for the JsonRpcOltpTable table-class route surface."""

from __future__ import annotations

from typing import Any

from tigrbl_equivalence_contracts.runtime import ServerKind, assert_route_surface_over_http

ROUTES = (('/widgetjsonrpcoltptable', ('GET', 'POST')), ('/widgetjsonrpcoltptable/{item_id}', ('GET', 'PATCH', 'PUT', 'DELETE')))
EXPECTED_EVIDENCE = tuple({"path": path, "methods": tuple(methods)} for path, methods in ROUTES)


def assert_equivalence(app: Any, server_kind: ServerKind) -> tuple[dict[str, Any], ...]:
    """Start one vendor app and assert the JsonRpcOltpTable route surface."""

    evidence = assert_route_surface_over_http(app, server_kind, ROUTES)
    assert evidence == EXPECTED_EVIDENCE
    return evidence
