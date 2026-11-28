"""Runtime proof for the JsonRpcOltpTable table-class JSON-RPC surface."""

from __future__ import annotations

from typing import Any

from tigrbl_equivalence_contracts.runtime import ServerKind, start_http_server

RPC_PATH = "/rpc"
METHOD_PREFIX = "WidgetJsonRpcOltpTable"
EXPECTED_JSONRPC_OLTP_EVIDENCE = (
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
        "step": "count_created",
        "status_code": 200,
        "envelope": {"jsonrpc": "2.0", "id": 2, "result": {"count": 1}},
    },
    {
        "step": "exists_created",
        "status_code": 200,
        "envelope": {"jsonrpc": "2.0", "id": 3, "result": {"exists": True}},
    },
    {
        "step": "list_created",
        "status_code": 200,
        "envelope": {
            "jsonrpc": "2.0",
            "id": 4,
            "result": [{"id": "widget-1", "name": "First"}],
        },
    },
    {
        "step": "delete",
        "status_code": 200,
        "envelope": {"jsonrpc": "2.0", "id": 5, "result": {"deleted": 1}},
    },
)


def assert_equivalence(app: Any, server_kind: ServerKind) -> tuple[dict[str, Any], ...]:
    """Start one vendor app and assert OLTP JSON-RPC envelopes over HTTP."""

    server = start_http_server(app, server_kind)
    try:
        evidence = _assert_jsonrpc_oltp_widget_flow(server.base_url)
    finally:
        server.stop()
    assert evidence == EXPECTED_JSONRPC_OLTP_EVIDENCE
    return evidence


def _assert_jsonrpc_oltp_widget_flow(base_url: str) -> tuple[dict[str, Any], ...]:
    import httpx

    calls = (
        ("create", f"{METHOD_PREFIX}.create", {"id": "widget-1", "name": "First"}, 1),
        ("count_created", f"{METHOD_PREFIX}.count", {}, 2),
        ("exists_created", f"{METHOD_PREFIX}.exists", {"id": "widget-1"}, 3),
        ("list_created", f"{METHOD_PREFIX}.list", {}, 4),
        ("delete", f"{METHOD_PREFIX}.delete", {"id": "widget-1"}, 5),
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
