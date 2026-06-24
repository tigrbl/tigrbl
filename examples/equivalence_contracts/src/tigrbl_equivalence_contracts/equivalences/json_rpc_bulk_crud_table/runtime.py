"""Runtime proof for the JsonRpcBulkCrudTable table-class JSON-RPC surface."""

from __future__ import annotations

from typing import Any

from tigrbl_equivalence_contracts.runtime import ServerKind, start_http_server

RPC_PATH = "/rpc"
METHOD_PREFIX = "WidgetJsonRpcBulkCrudTable"
EXPECTED_JSONRPC_BULK_EVIDENCE = (
    {
        "step": "bulk_create",
        "status_code": 200,
        "envelope": {
            "jsonrpc": "2.0",
            "id": 1,
            "result": [
                {"id": "widget-1", "name": "First"},
                {"id": "widget-2", "name": "Second"},
            ],
        },
    },
    {
        "step": "bulk_update",
        "status_code": 200,
        "envelope": {
            "jsonrpc": "2.0",
            "id": 2,
            "result": [
                {"id": "widget-1", "name": "First Updated"},
                {"id": "widget-2", "name": "Second Updated"},
            ],
        },
    },
    {
        "step": "bulk_replace",
        "status_code": 200,
        "envelope": {
            "jsonrpc": "2.0",
            "id": 3,
            "result": [
                {"id": "widget-1", "name": "First Replaced"},
                {"id": "widget-2", "name": "Second Replaced"},
            ],
        },
    },
    {
        "step": "list_replaced",
        "status_code": 200,
        "envelope": {
            "jsonrpc": "2.0",
            "id": 4,
            "result": [
                {"id": "widget-1", "name": "First Replaced"},
                {"id": "widget-2", "name": "Second Replaced"},
            ],
        },
    },
    {
        "step": "bulk_delete",
        "status_code": 200,
        "envelope": {"jsonrpc": "2.0", "id": 5, "result": {"deleted": 2}},
    },
    {
        "step": "list_deleted",
        "status_code": 200,
        "envelope": {"jsonrpc": "2.0", "id": 6, "result": []},
    },
)


def assert_equivalence(app: Any, server_kind: ServerKind) -> tuple[dict[str, Any], ...]:
    """Start one vendor app and assert bulk JSON-RPC envelopes over HTTP."""

    server = start_http_server(app, server_kind)
    try:
        evidence = _assert_jsonrpc_bulk_widget_flow(server.base_url)
    finally:
        server.stop()
    assert evidence == EXPECTED_JSONRPC_BULK_EVIDENCE
    return evidence


def _assert_jsonrpc_bulk_widget_flow(base_url: str) -> tuple[dict[str, Any], ...]:
    import httpx

    calls = (
        (
            "bulk_create",
            {
                "jsonrpc": "2.0",
                "method": f"{METHOD_PREFIX}.bulk_create",
                "params": [
                    {"id": "widget-1", "name": "First"},
                    {"id": "widget-2", "name": "Second"},
                ],
                "id": 1,
            },
        ),
        (
            "bulk_update",
            {
                "jsonrpc": "2.0",
                "method": f"{METHOD_PREFIX}.bulk_update",
                "params": [
                    {"id": "widget-1", "name": "First Updated"},
                    {"id": "widget-2", "name": "Second Updated"},
                ],
                "id": 2,
            },
        ),
        (
            "bulk_replace",
            {
                "jsonrpc": "2.0",
                "method": f"{METHOD_PREFIX}.bulk_replace",
                "params": [
                    {"id": "widget-1", "name": "First Replaced"},
                    {"id": "widget-2", "name": "Second Replaced"},
                ],
                "id": 3,
            },
        ),
        (
            "list_replaced",
            {
                "jsonrpc": "2.0",
                "method": f"{METHOD_PREFIX}.list",
                "params": {},
                "id": 4,
            },
        ),
        (
            "bulk_delete",
            {
                "jsonrpc": "2.0",
                "method": f"{METHOD_PREFIX}.bulk_delete",
                "params": ["widget-1", "widget-2"],
                "id": 5,
            },
        ),
        (
            "list_deleted",
            {
                "jsonrpc": "2.0",
                "method": f"{METHOD_PREFIX}.list",
                "params": {},
                "id": 6,
            },
        ),
    )
    observed: list[dict[str, Any]] = []
    with httpx.Client(base_url=base_url, timeout=10.0) as client:
        for step, payload in calls:
            response = client.post(RPC_PATH, json=payload)
            assert response.status_code == 200
            envelope = response.json()
            assert envelope["jsonrpc"] == "2.0"
            assert envelope["id"] == payload["id"]
            assert "result" in envelope, envelope
            observed.append(
                {
                    "step": step,
                    "status_code": response.status_code,
                    "envelope": envelope,
                }
            )
    return tuple(observed)
