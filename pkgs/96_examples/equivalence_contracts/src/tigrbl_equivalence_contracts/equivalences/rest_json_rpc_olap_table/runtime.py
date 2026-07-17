"""Runtime proof for the RestJsonRpcOlapTable REST and JSON-RPC surfaces."""

from __future__ import annotations

from typing import Any

from tigrbl_equivalence_contracts.runtime import (
    ServerKind,
    assert_route_surface_over_http,
    start_http_server,
)

RPC_PATH = "/rpc"
METHOD_PREFIX = "WidgetRestJsonRpcOlapTable"
ROUTES = (
    ("/widgetrestjsonrpcolaptable", ("GET", "POST")),
    ("/widgetrestjsonrpcolaptable/{item_id}", ("GET",)),
)
EXPECTED_REST_EVIDENCE = tuple({"path": path, "methods": tuple(methods)} for path, methods in ROUTES)
EXPECTED_JSONRPC_OLAP_EVIDENCE = (
    {
        "step": "count_empty",
        "status_code": 200,
        "envelope": {"jsonrpc": "2.0", "id": 1, "result": {"count": 0}},
    },
    {
        "step": "exists_missing",
        "status_code": 200,
        "envelope": {"jsonrpc": "2.0", "id": 2, "result": {"exists": False}},
    },
    {
        "step": "list_empty",
        "status_code": 200,
        "envelope": {"jsonrpc": "2.0", "id": 3, "result": []},
    },
    {
        "step": "aggregate_empty",
        "status_code": 200,
        "envelope": {
            "jsonrpc": "2.0",
            "id": 4,
            "result": {"field": "name", "op": "sum", "value": 0, "count": 0},
        },
    },
    {
        "step": "group_by_empty",
        "status_code": 200,
        "envelope": {
            "jsonrpc": "2.0",
            "id": 5,
            "result": {"field": "name", "agg": "count", "groups": []},
        },
    },
)
EXPECTED_EVIDENCE = {
    "rest_routes": EXPECTED_REST_EVIDENCE,
    "jsonrpc": EXPECTED_JSONRPC_OLAP_EVIDENCE,
}


def assert_equivalence(app: Any, server_kind: ServerKind) -> dict[str, Any]:
    """Start one vendor app and assert OLAP REST routes plus JSON-RPC envelopes."""

    rest_routes = assert_route_surface_over_http(app, server_kind, ROUTES)
    server = start_http_server(app, server_kind)
    try:
        jsonrpc = _assert_jsonrpc_olap_widget_flow(server.base_url)
    finally:
        server.stop()
    evidence = {"rest_routes": rest_routes, "jsonrpc": jsonrpc}
    assert evidence == EXPECTED_EVIDENCE
    return evidence


def _assert_jsonrpc_olap_widget_flow(base_url: str) -> tuple[dict[str, Any], ...]:
    import httpx

    calls = (
        ("count_empty", f"{METHOD_PREFIX}.count", {}, 1),
        ("exists_missing", f"{METHOD_PREFIX}.exists", {"id": "widget-1"}, 2),
        ("list_empty", f"{METHOD_PREFIX}.list", {}, 3),
        ("aggregate_empty", f"{METHOD_PREFIX}.aggregate", {"field": "name"}, 4),
        ("group_by_empty", f"{METHOD_PREFIX}.group_by", {"field": "name"}, 5),
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
