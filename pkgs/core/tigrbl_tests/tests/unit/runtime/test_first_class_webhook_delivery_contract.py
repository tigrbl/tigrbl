from __future__ import annotations

import importlib

import pytest


def test_runtime_does_not_own_first_class_webhook_delivery_surface() -> None:
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("tigrbl_runtime.webhooks")


def test_outbound_webhook_delivery_uses_callback_runtime_alias() -> None:
    callbacks = importlib.import_module("tigrbl_runtime.callbacks")

    plan = callbacks.compile_callback_delivery_plan(
        event="inventory.updated",
        endpoint="https://example.test/hooks/inventory",
        signing_secret_ref="secret:webhook",
        retry={"max_attempts": 3, "backoff": "exponential"},
    )

    assert plan["event"] == "inventory.updated"
    assert plan["endpoint"] == "https://example.test/hooks/inventory"
    assert plan["retry"]["max_attempts"] == 3
    assert plan["completion_subevent"] == "callback.delivery.emit_complete"
