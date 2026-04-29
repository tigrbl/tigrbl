from __future__ import annotations

import pytest

from tigrbl import (
    SessionSpec,
    SseBindingSpec,
    WebTransportBindingSpec,
    WsBindingSpec,
    readonly,
    session_spec,
    tx_repeatable_read,
)
from tigrbl_core._spec.session_spec import tx_read_committed, tx_serializable


def test_sessionspec_normalizes_aliases_and_emits_adapter_kwargs() -> None:
    spec = session_spec(
        {
            "iso": "repeatable_read",
            "readonly": True,
            "max_retries": 3,
            "statement_timeout_ms": 2_000,
            "tenant_id": "tenant-a",
            "trace_id": "trace-001",
        }
    )

    kwargs = spec.to_kwargs()

    assert spec.isolation == "repeatable_read"
    assert spec.read_only is True
    assert kwargs["max_retries"] == 3
    assert kwargs["statement_timeout_ms"] == 2_000
    assert kwargs["tenant_id"] == "tenant-a"
    assert kwargs["trace_id"] == "trace-001"


def test_sessionspec_merge_uses_higher_scope_non_none_precedence() -> None:
    app_policy = SessionSpec(isolation="read_committed", read_only=False, max_retries=1)
    op_policy = SessionSpec(read_only=True, statement_timeout_ms=500)

    merged = app_policy.merge(op_policy)

    assert merged.isolation == "read_committed"
    assert merged.read_only is True
    assert merged.max_retries == 1
    assert merged.statement_timeout_ms == 500


def test_sessionspec_helpers_create_named_transaction_profiles() -> None:
    assert tx_read_committed(read_only=True) == SessionSpec(
        isolation="read_committed", read_only=True
    )
    assert tx_repeatable_read(read_only=False) == SessionSpec(
        isolation="repeatable_read", read_only=False
    )
    assert tx_serializable().isolation == "serializable"
    assert readonly() == SessionSpec(read_only=True)


def test_sessionspec_factory_rejects_mapping_and_kwargs_together() -> None:
    with pytest.raises(ValueError, match="either a mapping/spec or kwargs"):
        session_spec({"isolation": "read_committed"}, read_only=True)


def test_sessionspec_adapter_kwargs_include_declared_defaults_and_hints() -> None:
    spec = session_spec(
        isolation="read_committed",
        read_only=True,
        lock_timeout_ms=500,
        fetch_rows=100,
        cache_read=True,
        cache_write=False,
        namespace="inventory",
    )

    assert spec.to_kwargs() == {
        "isolation": "read_committed",
        "read_only": True,
        "autobegin": True,
        "max_retries": 0,
        "backoff_ms": 0,
        "backoff_jitter": True,
        "lock_timeout_ms": 500,
        "fetch_rows": 100,
        "cache_read": True,
        "cache_write": False,
        "namespace": "inventory",
    }


def test_sessionspec_roundtrips_observability_and_consistency_metadata() -> None:
    spec = SessionSpec(
        isolation="serializable",
        consistency="bounded_staleness",
        staleness_ms=250,
        min_lsn="0000000000000100",
        as_of_ts="2026-04-29T12:00:00Z",
        rls_context={"tenant": "tenant-a"},
        tenant_id="tenant-a",
        role="readonly_analyst",
        trace_id="trace-001",
        query_tag="inventory-read",
        tag="api:v1",
        tracing_sample=0.25,
        kms_key_alias="tenant-a/data",
        classification="confidential",
        audit=True,
        idempotency_key="req-001",
        page_snapshot="snapshot-001",
    )

    restored = SessionSpec.from_json(spec.to_json())

    assert restored == spec
    assert restored.rls_context == {"tenant": "tenant-a"}
    assert restored.min_lsn == "0000000000000100"
    assert restored.as_of_ts == "2026-04-29T12:00:00Z"
    assert restored.tenant_id == "tenant-a"
    assert restored.role == "readonly_analyst"
    assert restored.trace_id == "trace-001"
    assert restored.tag == "api:v1"
    assert restored.tracing_sample == 0.25
    assert restored.kms_key_alias == "tenant-a/data"
    assert restored.classification == "confidential"
    assert restored.audit is True
    assert restored.page_snapshot == "snapshot-001"


def test_sse_bindingspec_declares_server_stream_sse_get_contract() -> None:
    binding = SseBindingSpec(proto="https.sse", path="/events")
    restored = SseBindingSpec.from_dict(binding.to_dict())

    assert restored == binding
    assert restored.methods == ("GET",)
    assert restored.exchange == "server_stream"
    assert restored.framing == "sse"


def test_ws_bindingspec_preserves_bidirectional_subprotocol_metadata() -> None:
    binding = WsBindingSpec(
        proto="wss",
        path="/socket",
        subprotocols=("jsonrpc", "v1"),
    )
    restored = WsBindingSpec.from_json(binding.to_json())

    assert restored == binding
    assert restored.exchange == "bidirectional_stream"
    assert restored.framing == "text"
    assert restored.subprotocols == ("jsonrpc", "v1")
    assert not hasattr(restored, "methods")


def test_webtransport_bindingspec_preserves_webtransport_framing() -> None:
    binding = WebTransportBindingSpec(path="/transport")
    restored = WebTransportBindingSpec.from_json(binding.to_json())

    assert restored == binding
    assert restored.proto == "webtransport"
    assert restored.exchange == "bidirectional_stream"
    assert restored.framing == "webtransport"
    assert restored.exchange != "request_response"
