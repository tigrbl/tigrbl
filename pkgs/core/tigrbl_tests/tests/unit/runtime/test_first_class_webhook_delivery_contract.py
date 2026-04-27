from __future__ import annotations

import importlib

import pytest


def _require(module_name: str, attr_name: str):
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        pytest.xfail(f"{module_name} is not implemented")
    value = getattr(module, attr_name, None)
    if value is None:
        pytest.xfail(f"{module_name}.{attr_name} is not implemented")
    return value


def test_webhook_delivery_plan_compiles_event_payload_and_endpoint_metadata() -> None:
    compile_plan = _require("tigrbl_runtime.webhooks", "compile_webhook_delivery_plan")

    plan = compile_plan(
        event="inventory.updated",
        endpoint="https://example.test/hooks/inventory",
        signing_secret_ref="secret:webhook",
        retry={"max_attempts": 3, "backoff": "exponential"},
    )

    assert plan["event"] == "inventory.updated"
    assert plan["endpoint"] == "https://example.test/hooks/inventory"
    assert plan["signing"] == {"algorithm": "hmac-sha256", "secret_ref": "secret:webhook"}
    assert plan["retry"]["max_attempts"] == 3
    assert plan["completion_subevent"] == "webhook.delivery.emit_complete"


def test_webhook_payload_signing_is_deterministic_and_includes_idempotency_key() -> None:
    build_payload = _require("tigrbl_runtime.webhooks", "build_webhook_payload")
    sign = _require("tigrbl_runtime.webhooks", "sign_webhook_payload")

    payload = build_payload(
        event="inventory.updated",
        data={"id": "item-1"},
        idempotency_key="evt-001",
    )
    first = sign(payload, secret="secret")
    second = sign(payload, secret="secret")

    assert payload["idempotency_key"] == "evt-001"
    assert first == second
    assert first["signature"].startswith("sha256=")


def test_successful_webhook_delivery_records_completion_status() -> None:
    deliver = _require("tigrbl_runtime.webhooks", "deliver_webhook")
    trace: list[str] = []

    result = deliver(
        {"event": "inventory.updated", "idempotency_key": "evt-001"},
        send=lambda request: {"status_code": 202, "body": "accepted"},
        trace=trace.append,
    )

    assert trace == ["webhook.delivery.emit", "webhook.delivery.emit_complete"]
    assert result["status"] == "delivered"
    assert result["attempts"] == 1
    assert result["completed"] is True


def test_transient_webhook_failure_retries_with_backoff_before_success() -> None:
    deliver = _require("tigrbl_runtime.webhooks", "deliver_webhook")
    attempts: list[int] = []

    def send(_request):
        attempts.append(len(attempts) + 1)
        if len(attempts) < 3:
            return {"status_code": 503, "body": "try later"}
        return {"status_code": 200, "body": "ok"}

    result = deliver(
        {"event": "inventory.updated", "idempotency_key": "evt-001"},
        send=send,
        retry={"max_attempts": 3, "backoff": "exponential"},
    )

    assert attempts == [1, 2, 3]
    assert result["status"] == "delivered"
    assert result["attempts"] == 3


def test_terminal_webhook_failure_records_dead_letter_metadata() -> None:
    deliver = _require("tigrbl_runtime.webhooks", "deliver_webhook")

    result = deliver(
        {"event": "inventory.updated", "idempotency_key": "evt-001"},
        send=lambda request: {"status_code": 410, "body": "gone"},
        retry={"max_attempts": 3},
        dead_letter=True,
    )

    assert result["status"] == "dead_lettered"
    assert result["attempts"] == 1
    assert result["dead_letter"]["event"] == "inventory.updated"
    assert result["dead_letter"]["status_code"] == 410


def test_webhook_timeout_records_error_without_emit_complete() -> None:
    deliver = _require("tigrbl_runtime.webhooks", "deliver_webhook")
    trace: list[str] = []

    def send(_request):
        raise TimeoutError("webhook timed out")

    result = deliver(
        {"event": "inventory.updated", "idempotency_key": "evt-001"},
        send=send,
        trace=trace.append,
        retry={"max_attempts": 1},
    )

    assert trace == ["webhook.delivery.emit"]
    assert result["status"] == "failed"
    assert result["completed"] is False
    assert result["error_ctx"]["subevent"] == "webhook.delivery.emit"
