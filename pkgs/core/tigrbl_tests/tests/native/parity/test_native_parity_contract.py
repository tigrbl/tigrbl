from __future__ import annotations

from tigrbl_kernel import build_native_kernel, build_native_parity_snapshot
from tigrbl_native import (
    native_parity_snapshot,
    native_transport_trace,
    reference_parity_snapshot,
    reference_transport_trace,
)
from tigrbl_runtime import transport_parity_trace


def _phase4_spec() -> dict[str, object]:
    return {
        "name": "phase4-demo",
        "bindings": [
            {
                "alias": "create_widget",
                "transport": "rest",
                "hooks": [{"phase": "pre_handler"}],
                "op": {
                    "target": "create",
                    "route": "/widgets",
                    "exchange": "request_response",
                    "tx_scope": "read_write",
                },
            },
            {
                "alias": "rpc_read_widget",
                "transport": "jsonrpc",
                "op": {
                    "target": "read",
                    "route": "/rpc/widgets.read",
                    "exchange": "request_response",
                    "tx_scope": "read_only",
                },
            },
            {
                "alias": "events",
                "transport": "sse",
                "op": {
                    "target": "subscribe",
                    "route": "/events",
                    "exchange": "server_stream",
                    "tx_scope": "none",
                    "subevents": ["chunk"],
                },
            },
            {
                "alias": "socket",
                "transport": "ws",
                "family": "bidirectional",
                "op": {
                    "target": "publish",
                    "route": "/ws",
                    "exchange": "bidirectional_stream",
                    "tx_scope": "none",
                    "subevents": ["message"],
                },
            },
            {
                "alias": "transport",
                "transport": "webtransport",
                "op": {
                    "target": "send_datagram",
                    "route": "/transport",
                    "exchange": "bidirectional_stream",
                    "tx_scope": "none",
                    "subevents": ["datagram"],
                },
            },
        ],
    }


def test_native_parity_snapshot_matches_reference_contract() -> None:
    spec = _phase4_spec()
    expected = reference_parity_snapshot(spec)
    observed = native_parity_snapshot(spec)
    assert observed == expected
    assert observed["packed_plan"] == {"segments": 5, "hot_paths": 1, "fused_steps": 5}
    assert observed["docs"]["openapi_paths"] == ["/widgets", "/rpc/widgets.read"]
    assert observed["docs"]["asyncapi_channels"] == ["/events", "/ws", "/transport"]


def test_build_native_kernel_attaches_parity_snapshot_without_marking_claimable() -> None:
    plan = build_native_kernel(_phase4_spec())
    assert plan.backend == "rust"
    assert plan.parity_snapshot == build_native_parity_snapshot(_phase4_spec())
    assert plan.claimable is False


def test_transport_parity_traces_match_reference_contract() -> None:
    for transport in ("rest", "jsonrpc", "sse", "ws", "wss", "webtransport"):
        expected = reference_transport_trace(
            transport,
            include_hook=True,
            include_error=True,
            include_docs=True,
        )
        assert native_transport_trace(
            transport,
            include_hook=True,
            include_error=True,
            include_docs=True,
        ) == expected
        assert transport_parity_trace(
            transport,
            include_hook=True,
            include_error=True,
            include_docs=True,
        ) == expected
