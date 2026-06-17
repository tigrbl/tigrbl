from __future__ import annotations

from tigrbl_core._spec import HttpRestBindingSpec, OpSpec, PathSpec
from tigrbl_concrete.webhooks import (
    DefineWebhook,
    Webhook,
    defineWebhook,
)


def test_webhook_lowers_to_resource_path_post_rest_op() -> None:
    path = DefineWebhook(
        path="/webhooks/stripe",
        provider="stripe",
        event_type="invoice.paid",
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


def test_webhook_shortcut_lowers_to_resource_path_post_rest_op() -> None:
    path = defineWebhook(
        path="/webhooks/github",
        provider="github",
        event_type="push",
    )

    assert path.path == "/webhooks/github"
    assert path.ops[0].alias == "webhook_github_push"
    assert path.ops[0].extra["webhook"]["direction"] == "inbound"


def test_webhook_concrete_object_is_declarative_only() -> None:
    webhook = Webhook(
        path="/webhooks/linear",
        provider="linear",
        event_type="issue.created",
    )

    assert webhook.path == "/webhooks/linear"
    assert webhook.provider == "linear"
    assert webhook.event_type == "issue.created"
    assert not hasattr(webhook, "lower")


def test_webhook_decorator_attaches_lowered_path_spec_to_handler() -> None:
    from tigrbl_concrete._decorators import webhook

    @webhook(path="/webhooks/slack", provider="slack", event_type="message")
    def handle_slack(payload: dict[str, object]) -> dict[str, bool]:
        return {"accepted": True}

    path = handle_slack.__tigrbl_webhook_path_spec__

    assert isinstance(path, PathSpec)
    assert path.path == "/webhooks/slack"
    assert path.ops[0].handler is handle_slack
    assert path.ops[0].extra["webhook"]["direction"] == "inbound"


def test_webhook_public_surface_avoids_inbound_symbol_names() -> None:
    import tigrbl_concrete.webhooks as webhooks

    assert not [name for name in webhooks.__all__ if "Inbound" in name]
    assert not [name for name in webhooks.__all__ if "Signature" in name]
    assert not [name for name in webhooks.__all__ if "Idempotency" in name]
    assert "inbound webhook" in (DefineWebhook.__doc__ or "")


def test_no_callbackspec_or_webhookspec_public_surface_is_introduced() -> None:
    import tigrbl_core._spec as spec

    assert not hasattr(spec, "CallbackSpec")
    assert not hasattr(spec, "WebhookSpec")
