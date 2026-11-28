import pytest
from tigrbl_spec.schema import identity_fields, validate_payload

from tigrbl import (
    CallbackSpec,
    DefineCallback,
    DefineWebhook,
    WebhookSpec,
    callback_ctx,
    webhook_ctx,
)


def receive(ctx):
    return ctx["payload"]


def payload(ctx):
    return ctx["result"]


def test_public_authoring_specs_round_trip():
    webhook = WebhookSpec(
        path="/hooks", provider="billing", event_type="paid", handler=receive
    )
    callback = CallbackSpec(
        ops="pay",
        event="paid",
        destination="https://example.test/hooks",
        payload=payload,
    )
    assert WebhookSpec.from_json(webhook.to_json()) == webhook
    assert CallbackSpec.from_json(callback.to_json()) == callback
    for declaration in (webhook, callback):
        name = type(declaration).__name__
        payload_data = {**identity_fields(name), **declaration.to_dict()}
        assert validate_payload(name, payload_data) == payload_data
    assert (
        DefineWebhook(
            path=webhook.path,
            provider=webhook.provider,
            event_type=webhook.event_type,
            handler=receive,
        )
        .ops[0]
        .handler
        is receive
    )
    assert (
        webhook_ctx(path="/hooks", provider="billing", event_type="paid")(receive)
        is receive
    )
    assert isinstance(
        DefineCallback(
            ops="pay", event="paid", destination=callback.destination, payload=payload
        ),
        CallbackSpec,
    )
    assert isinstance(
        callback_ctx(ops="pay", event="paid", destination=callback.destination)(
            payload
        ),
        CallbackSpec,
    )


@pytest.mark.parametrize(
    "options",
    [
        {"ops": "*"},
        {"timeout_seconds": 0},
        {"max_attempts": 0},
        {"delivery": "worker"},
        {"destination": "file:///tmp/test"},
    ],
)
def test_invalid_callback_authoring(options):
    with pytest.raises(ValueError):
        CallbackSpec(
            **{
                "ops": "pay",
                "event": "paid",
                "destination": "https://example.test/hooks",
                "payload": payload,
                **options,
            }
        )
