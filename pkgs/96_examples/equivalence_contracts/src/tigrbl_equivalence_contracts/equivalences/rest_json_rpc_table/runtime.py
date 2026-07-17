"""Runtime proof for the RestJsonRpcTable table-class REST and JSON-RPC surfaces."""

from __future__ import annotations

from typing import Any

from tigrbl_equivalence_contracts.runtime import (
    ServerKind,
    assert_route_surface_over_http,
    start_http_server,
)

RPC_PATH = "/rpc"
METHOD_PREFIX = "WidgetRestJsonRpcTable"
ROUTES = (
    ("/widgetrestjsonrpctable", ("GET", "POST", "DELETE")),
    ("/widgetrestjsonrpctable/{item_id}", ("GET", "PATCH", "PUT", "DELETE")),
)
EXPECTED_REST_EVIDENCE = tuple({"path": path, "methods": tuple(methods)} for path, methods in ROUTES)
EXPECTED_JSONRPC_EVIDENCE = (
    {
        "step": "create",
        "status_code": 200,
        "envelope": {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {"id": "widget-1", "name": "First"},
        },
    },
    {
        "step": "read_created",
        "status_code": 200,
        "envelope": {
            "jsonrpc": "2.0",
            "id": 2,
            "result": {"id": "widget-1", "name": "First"},
        },
    },
    {
        "step": "list_created",
        "status_code": 200,
        "envelope": {
            "jsonrpc": "2.0",
            "id": 3,
            "result": [{"id": "widget-1", "name": "First"}],
        },
    },
    {
        "step": "delete",
        "status_code": 200,
        "envelope": {"jsonrpc": "2.0", "id": 4, "result": {"deleted": 1}},
    },
)
EXPECTED_EVIDENCE = {
    "rest_routes": EXPECTED_REST_EVIDENCE,
    "jsonrpc": EXPECTED_JSONRPC_EVIDENCE,
}


def assert_equivalence(app: Any, server_kind: ServerKind) -> dict[str, Any]:
    """Start one vendor app and assert both REST routes and JSON-RPC envelopes."""

    rest_routes = assert_route_surface_over_http(app, server_kind, ROUTES)
    server = start_http_server(app, server_kind)
    try:
        jsonrpc = _assert_jsonrpc_widget_crud(server.base_url)
    finally:
        server.stop()
    evidence = {"rest_routes": rest_routes, "jsonrpc": jsonrpc}
    assert evidence == EXPECTED_EVIDENCE
    return evidence


def _assert_jsonrpc_widget_crud(base_url: str) -> tuple[dict[str, Any], ...]:
    import httpx

    calls = (
        (
            "create",
            f"{METHOD_PREFIX}.create",
            {"id": "widget-1", "name": "First"},
            1,
        ),
        ("read_created", f"{METHOD_PREFIX}.read", {"id": "widget-1"}, 2),
        ("list_created", f"{METHOD_PREFIX}.list", {}, 3),
        ("delete", f"{METHOD_PREFIX}.delete", {"id": "widget-1"}, 4),
    )
    observed: list[dict[str, Any]] = []
    with httpx.Client(base_url=base_url, timeout=10.0) as client:
        for step, method, params, request_id in calls:
            response = client.post(
                RPC_PATH,
                json={
                    "jsonrpc": "2.0",
                    "method": method,
                    "params": params,
                    "id": request_id,
                },
            )
            assert response.status_code == 200
            envelope = response.json()
            assert envelope["jsonrpc"] == "2.0"
            assert envelope["id"] == request_id
            assert "result" in envelope, envelope
            observed.append(
                {
                    "step": step,
                    "status_code": response.status_code,
                    "envelope": envelope,
                }
            )
    return tuple(observed)
