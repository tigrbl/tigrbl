from __future__ import annotations

import pytest

from tigrbl_kernel.cross_transport import (
    canonical_operation_id,
    compile_equivalence_manifest,
    equivalent_binding_group,
    equivalent_transport_results,
    normalized_transport_result,
    standard_equivalence_corpus,
)


EQUIVALENT_READ_BINDINGS = (
    {"kind": "http.rest", "path": "/items/{id}", "methods": ("GET",)},
    {"kind": "http.jsonrpc", "rpc_method": "Item.read"},
    {"kind": "ws", "path": "/socket", "framing": "jsonrpc", "subprotocols": ("jsonrpc",)},
)


def test_equivalent_bindings_resolve_to_same_canonical_operation_id() -> None:
    manifest = compile_equivalence_manifest("Item.read", EQUIVALENT_READ_BINDINGS)

    assert manifest["op_id"] == "Item.read"
    assert {row["family"] for row in manifest["bindings"]} == {"request", "message"}


def test_equivalent_rest_jsonrpc_ws_and_stream_attempts_compare_normalized_results() -> None:
    rest = {"transport": "http", "http_status": 200, "value": {"id": 1}, "effects": ("read",)}
    jsonrpc = {
        "transport": "jsonrpc",
        "jsonrpc_id": "1",
        "jsonrpc_version": "2.0",
        "value": {"id": 1},
        "effects": ("read",),
    }
    websocket = {"transport": "ws", "ws_opcode": "text", "value": {"id": 1}, "effects": ("read",)}

    assert equivalent_transport_results(rest, jsonrpc, websocket)


def test_transport_specific_envelopes_are_excluded_from_semantic_comparison() -> None:
    assert normalized_transport_result(
        {"transport": "http", "headers": {"x": "1"}, "value": {"ok": True}}
    ) == {"value": {"ok": True}}


def test_non_equivalent_or_unsupported_transport_binding_is_not_forced_into_equivalence() -> None:
    with pytest.raises(ValueError, match="websocket bindings do not accept HTTP methods"):
        compile_equivalence_manifest(
            "Item.read",
            ({"kind": "ws", "path": "/socket", "methods": ("GET",)},),
        )


def test_equivalent_transports_preserve_persistence_effects_and_effect_fences() -> None:
    first = {"value": {"id": 1}, "effects": ("insert:item:1",), "effect_fence": "committed"}
    second = {
        "transport": "jsonrpc",
        "jsonrpc_id": "2",
        "value": {"id": 1},
        "effects": ("insert:item:1",),
        "effect_fence": "committed",
    }

    assert equivalent_transport_results(first, second)


def test_equivalent_transports_preserve_declared_idempotency_behavior() -> None:
    assert equivalent_transport_results(
        {"value": {"created": True}, "idempotency_key": "k1", "duplicate": False},
        {"transport": "http", "value": {"created": True}, "idempotency_key": "k1", "duplicate": False},
    )
    assert not equivalent_transport_results(
        {"value": {"created": True}, "idempotency_key": "k1"},
        {"value": {"created": True}, "idempotency_key": "k2"},
    )


def test_equivalent_transports_preserve_retry_and_replay_parentage() -> None:
    payload = {
        "value": {"ok": True},
        "attempt_id": "attempt-2",
        "parent_attempt_id": "attempt-1",
        "replay_id": "replay-1",
    }

    assert equivalent_transport_results(payload, {"transport": "ws", **payload})


def test_equivalent_transports_preserve_error_and_diagnostic_classification() -> None:
    left = {
        "error": {"code": "not_found", "message": "missing"},
        "diagnostics": {"classification": "client", "trace_id": "http-trace"},
    }
    right = {
        "transport": "jsonrpc",
        "error": {"code": "not_found", "message": "missing"},
        "diagnostics": {"classification": "client", "trace_id": "rpc-trace"},
    }

    assert equivalent_transport_results(left, right)


def test_equivalent_transports_preserve_trace_qlog_correlation() -> None:
    left = {"value": "ok", "diagnostics": {"classification": "ok", "qlog_id": "q1"}}
    right = {"transport": "webtransport", "value": "ok", "diagnostics": {"classification": "ok", "qlog_id": "q2"}}

    assert equivalent_transport_results(left, right)


def test_cross_transport_corpus_covers_standard_bulk_query_stream_and_custom_ops() -> None:
    categories = {case.category for case in standard_equivalence_corpus()}

    assert categories == {"standard", "bulk", "query", "stream", "custom"}
    assert all(canonical_operation_id(case.op_id) == case.op_id for case in standard_equivalence_corpus())


def test_cross_transport_equivalence_respects_delivery_ordering_and_framing_declarations() -> None:
    manifest = compile_equivalence_manifest(
        "Item.tail",
        (
            {"kind": "http.stream", "path": "/items/tail"},
            {"kind": "http.sse", "path": "/items/events"},
            {"kind": "webtransport", "profile": "bidi_stream"},
        ),
    )

    assert {row["family"] for row in manifest["bindings"]} == {"stream"}
    assert {row["framing"] for row in manifest["bindings"]} == {"stream", "sse", "webtransport"}


def test_cross_transport_equivalence_manifest_preserves_runtime_plan_and_schema_identity() -> None:
    manifest = compile_equivalence_manifest(
        "Item.read",
        EQUIVALENT_READ_BINDINGS,
        schema_identity="schema:item:v2",
        runtime_plan_identity="packed-plan:abc123",
    )

    assert manifest["schema_identity"] == "schema:item:v2"
    assert manifest["runtime_plan_identity"] == "packed-plan:abc123"
    assert all(row["fingerprint"] for row in manifest["bindings"])


def test_equivalent_binding_group_rejects_empty_bindings() -> None:
    with pytest.raises(ValueError, match="at least one transport binding"):
        equivalent_binding_group("Item.read", ())
