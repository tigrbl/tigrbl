from tigrbl_atoms.atoms.ingress.identity import (
    invocation_identity,
    prepare_transport_identity,
    webtransport_lane_identity,
)
import pytest


def wt_scope(session):
    return {
        "type": "webtransport",
        "session_id": session,
        "extensions": {"tigr.transport_identity": {
            "version": 1, "connection_id": "quic-1",
            "transport_session_id": session, "request_id": f"connect-{session}",
        }},
    }


def test_session_stream_and_datagram_identities_are_distinct():
    first_scope, next_scope = wt_scope("wt-1"), wt_scope("wt-2")
    first = prepare_transport_identity(first_scope)
    second = prepare_transport_identity(next_scope)
    assert first["connection_id"] == second["connection_id"]
    assert first["correlation_id"] != second["correlation_id"]
    assert first["opening_request_id"] == "connect-wt-1"
    assert "request_id" not in first
    stream = webtransport_lane_identity(first_scope, {"stream_id": 0}, first)
    another = webtransport_lane_identity(first_scope, {"stream_id": 4}, first)
    assert stream["stream_correlation_id"] != another["stream_correlation_id"]
    assert stream == webtransport_lane_identity(first_scope, {"stream_id": 0}, first)
    datagram = webtransport_lane_identity(first_scope, {"datagram_id": "d"}, stream)
    assert "stream_id" not in datagram and "stream_correlation_id" not in datagram
    assert datagram["correlation_id"] == stream["correlation_id"] == first["correlation_id"]
    assert invocation_identity(stream)["invocation_id"] != invocation_identity(stream)["invocation_id"]
    with pytest.raises(ValueError, match="another session"):
        webtransport_lane_identity(first_scope, {"session_id": "wt-2", "stream_id": 0}, first)


def test_scope_fallback_and_trusted_correlation():
    legacy = prepare_transport_identity({"type": "webtransport", "session_id": "legacy"})
    assert legacy["transport_session_id"] == "legacy"
    assert "connection_id" not in legacy
    headers = [(b"x-correlation-id", b"upstream")]
    untrusted = prepare_transport_identity({"type": "http", "headers": headers})
    trusted = prepare_transport_identity({
        "type": "http", "headers": headers, "state": {"tigrbl_trusted_correlation": True}
    })
    assert untrusted["correlation_id"] != "upstream"
    assert trusted["correlation_id"] == "upstream"


def test_conflicting_scope_ids_fail():
    scope = wt_scope("canonical")
    scope["session_id"] = "legacy"
    with pytest.raises(ValueError, match="conflicting"):
        prepare_transport_identity(scope)


def test_trace_snapshot_retains_independent_w3c_and_runtime_ids():
    from types import SimpleNamespace
    from tigrbl_kernel.trace import snapshot

    trace_id = "3" * 32
    parent_id = "4" * 16
    scope = {"type": "http", "headers": [(b"traceparent", f"00-{trace_id}-{parent_id}-01".encode())]}
    request = prepare_transport_identity(scope)
    invocation = invocation_identity(request)
    trace = snapshot(SimpleNamespace(temp={"identity": invocation}))["identity"]
    assert request["parent_span_id"] == parent_id
    assert trace["trace_id"] == trace_id
    assert trace["parent_span_id"] == request["span_id"]
    assert trace["correlation_id"] == request["correlation_id"]
    assert trace["invocation_id"] != request["request_id"]
