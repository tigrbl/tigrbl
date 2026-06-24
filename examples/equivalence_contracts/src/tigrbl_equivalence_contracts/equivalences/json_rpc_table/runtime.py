"""Runtime proof for the JsonRpcTable table-class HTTP JSON-RPC surface."""

from __future__ import annotations

from typing import Any

from tigrbl_equivalence_contracts.runtime import ServerKind, start_http_server

RPC_PATH = "/rpc"
METHOD_PREFIX = "WidgetJsonRpcTable"
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
    {
        "step": "list_deleted",
        "status_code": 200,
        "envelope": {"jsonrpc": "2.0", "id": 5, "result": []},
    },
)


def assert_equivalence(app: Any, server_kind: ServerKind) -> tuple[dict[str, Any], ...]:
    """Start one vendor app and assert JSON-RPC envelopes over HTTP."""

    server = start_http_server(app, server_kind)
    try:
        evidence = _assert_jsonrpc_widget_crud(server.base_url)
    finally:
        server.stop()
    assert evidence == EXPECTED_JSONRPC_EVIDENCE
    return evidence


def _assert_jsonrpc_widget_crud(base_url: str) -> tuple[dict[str, Any], ...]:
    import httpx

    calls = (
        (
            "create",
            {
                "jsonrpc": "2.0",
                "method": f"{METHOD_PREFIX}.create",
                "params": {"id": "widget-1", "name": "First"},
                "id": 1,
            },
        ),
        (
            "read_created",
            {
                "jsonrpc": "2.0",
                "method": f"{METHOD_PREFIX}.read",
                "params": {"id": "widget-1"},
                "id": 2,
            },
        ),
        (
            "list_created",
            {
                "jsonrpc": "2.0",
                "method": f"{METHOD_PREFIX}.list",
                "params": {},
                "id": 3,
            },
        ),
        (
            "delete",
            {
                "jsonrpc": "2.0",
                "method": f"{METHOD_PREFIX}.delete",
                "params": {"id": "widget-1"},
                "id": 4,
            },
        ),
        (
            "list_deleted",
            {
                "jsonrpc": "2.0",
                "method": f"{METHOD_PREFIX}.list",
                "params": {},
                "id": 5,
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
            assert "result" in envelope
            observed.append(
                {
                    "step": step,
                    "status_code": response.status_code,
                    "envelope": envelope,
                }
            )
    return tuple(observed)
