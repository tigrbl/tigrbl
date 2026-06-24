"""Runtime proof for the JsonRpcOlapTable table-class JSON-RPC surface."""

from __future__ import annotations

from typing import Any

from tigrbl_equivalence_contracts.runtime import ServerKind, start_http_server

RPC_PATH = "/rpc"
METHOD_PREFIX = "WidgetJsonRpcOlapTable"
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


def assert_equivalence(app: Any, server_kind: ServerKind) -> tuple[dict[str, Any], ...]:
    """Start one vendor app and assert read-only OLAP JSON-RPC envelopes."""

    server = start_http_server(app, server_kind)
    try:
        evidence = _assert_jsonrpc_olap_widget_flow(server.base_url)
    finally:
        server.stop()
    assert evidence == EXPECTED_JSONRPC_OLAP_EVIDENCE
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
