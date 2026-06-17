from __future__ import annotations

import pytest

from tigrbl_core._spec import HttpRestBindingSpec, OpSpec, PathSpec
from tigrbl_concrete.webhooks import (
    DefineInboundWebhook,
    InboundWebhookReplayError,
    InboundWebhookSignatureError,
    build_inbound_webhook_ack,
    record_inbound_webhook_idempotency,
    sign_inbound_webhook_body,
    verify_inbound_webhook_signature,
)


def test_inbound_webhook_lowers_to_resource_path_post_rest_op() -> None:
    path = DefineInboundWebhook(
        path="/webhooks/stripe",
        provider="stripe",
        event_type="invoice.paid",
        signing_secret_ref="secret:stripe",
    )

    assert isinstance(path, PathSpec)
    assert path.kind == "resource"
    assert path.path == "/webhooks/stripe"
    assert len(path.ops) == 1

    op = path.ops[0]
    assert isinstance(op, OpSpec)
    assert op.alias == "webhook_stripe_invoice_paid"
    assert op.target == "custom"
    assert op.expose_rpc is False
    assert op.http_methods == ("POST",)
    assert op.status_code == 202

    binding = op.bindings[0]
    assert isinstance(binding, HttpRestBindingSpec)
    assert binding.proto == "https.rest"
    assert binding.methods == ("POST",)
    assert binding.path == "/webhooks/stripe"

    policy = op.extra["webhook"]
    assert policy["direction"] == "inbound"
    assert policy["provider"] == "stripe"
    assert policy["event_type"] == "invoice.paid"
    assert policy["signature"]["secret_ref"] == "secret:stripe"
    assert policy["ack"]["status_code"] == 202


def test_inbound_webhook_signature_verification_accepts_valid_raw_body_signature() -> None:
    body = b'{"type":"invoice.paid","id":"evt_001"}'
    signature = sign_inbound_webhook_body(raw_body=body, secret="secret")

    assert verify_inbound_webhook_signature(
        raw_body=body,
        headers={
            "X-Tigrbl-Signature": signature,
            "X-Tigrbl-Timestamp": "100",
        },
        secret="secret",
        now=100,
    )


def test_inbound_webhook_signature_verification_rejects_bad_signature() -> None:
    with pytest.raises(InboundWebhookSignatureError, match="invalid"):
        verify_inbound_webhook_signature(
            raw_body=b"{}",
            headers={
                "X-Tigrbl-Signature": "sha256=bad",
                "X-Tigrbl-Timestamp": "100",
            },
            secret="secret",
            now=100,
        )


def test_inbound_webhook_signature_verification_rejects_stale_timestamp() -> None:
    body = b"{}"
    signature = sign_inbound_webhook_body(raw_body=body, secret="secret")

    with pytest.raises(InboundWebhookSignatureError, match="stale"):
        verify_inbound_webhook_signature(
            raw_body=body,
            headers={
                "X-Tigrbl-Signature": signature,
                "X-Tigrbl-Timestamp": "100",
            },
            secret="secret",
            now=1000,
            timestamp_tolerance_seconds=10,
        )


def test_inbound_webhook_idempotency_records_once_and_rejects_replay() -> None:
    seen: set[str] = set()

    result = record_inbound_webhook_idempotency(
        idempotency_key="evt_001",
        seen=seen,
    )

    assert result == {"idempotency_key": "evt_001", "accepted": True}
    with pytest.raises(InboundWebhookReplayError, match="duplicate"):
        record_inbound_webhook_idempotency(idempotency_key="evt_001", seen=seen)


def test_inbound_webhook_ack_is_explicit_and_deterministic() -> None:
    assert build_inbound_webhook_ack(idempotency_key="evt_001") == {
        "status_code": 202,
        "body": {"accepted": True, "idempotency_key": "evt_001"},
    }


def test_no_callbackspec_or_webhookspec_public_surface_is_introduced() -> None:
    import tigrbl_core._spec as spec

    assert not hasattr(spec, "CallbackSpec")
    assert not hasattr(spec, "WebhookSpec")
