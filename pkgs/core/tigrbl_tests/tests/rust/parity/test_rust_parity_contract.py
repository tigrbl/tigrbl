from __future__ import annotations

from tigrbl_kernel import build_rust_kernel, build_rust_parity_snapshot
from tigrbl_runtime.rust import (
    rust_parity_snapshot,
    rust_transport_trace,
    reference_parity_snapshot,
    reference_transport_trace,
)
from tigrbl_runtime import rust_transport_trace


def _rust_parity_spec() -> dict[str, object]:
    return {
        "name": "rust-parity-demo",
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


def test_rust_parity_snapshot_matches_reference_contract() -> None:
    spec = _rust_parity_spec()
    expected = reference_parity_snapshot(spec)
    observed = rust_parity_snapshot(spec)
    assert observed == expected
    assert observed["packed_plan"] == {"segments": 5, "hot_paths": 1, "fused_steps": 5}
    assert observed["docs"]["openapi_paths"] == ["/widgets", "/rpc/widgets.read"]
    assert observed["docs"]["asyncapi_channels"] == ["/events", "/ws", "/transport"]


def test_build_rust_kernel_attaches_parity_snapshot_without_marking_claimable() -> None:
    plan = build_rust_kernel(_rust_parity_spec())
    assert plan.backend == "rust"
    assert plan.parity_snapshot == build_rust_parity_snapshot(_rust_parity_spec())
    assert plan.claimable is False


def test_rust_transport_traces_match_reference_contract() -> None:
    for transport in ("rest", "jsonrpc", "sse", "ws", "wss", "webtransport"):
        expected = reference_transport_trace(
            transport,
            include_hook=True,
            include_error=True,
            include_docs=True,
        )
        assert rust_transport_trace(
            transport,
            include_hook=True,
            include_error=True,
            include_docs=True,
        ) == expected
        assert rust_transport_trace(
            transport,
            include_hook=True,
            include_error=True,
            include_docs=True,
        ) == expected
