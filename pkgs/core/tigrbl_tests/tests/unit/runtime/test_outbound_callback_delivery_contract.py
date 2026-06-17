from __future__ import annotations

from tigrbl_runtime.callbacks import (
    build_callback_payload,
    compile_callback_delivery_plan,
    deliver_callback,
    sign_callback_payload,
)


def test_callback_delivery_plan_uses_callback_completion_subevent() -> None:
    plan = compile_callback_delivery_plan(
        event="inventory.updated",
        endpoint="https://example.test/callbacks/inventory",
        signing_secret_ref="secret:callback",
        retry={"max_attempts": 3, "backoff": "exponential"},
    )

    assert plan["event"] == "inventory.updated"
    assert plan["endpoint"] == "https://example.test/callbacks/inventory"
    assert plan["signing"] == {"algorithm": "hmac-sha256", "secret_ref": "secret:callback"}
    assert plan["retry"]["max_attempts"] == 3
    assert plan["completion_subevent"] == "callback.delivery.emit_complete"


def test_callback_payload_signing_is_deterministic_and_idempotent() -> None:
    payload = build_callback_payload(
        event="inventory.updated",
        data={"id": "item-1"},
        idempotency_key="evt-001",
    )
    first = sign_callback_payload(payload, secret="secret")
    second = sign_callback_payload(payload, secret="secret")

    assert payload["idempotency_key"] == "evt-001"
    assert first == second
    assert first["signature"].startswith("sha256=")


def test_successful_callback_delivery_records_callback_trace_events() -> None:
    trace: list[str] = []

    result = deliver_callback(
        {"event": "inventory.updated", "idempotency_key": "evt-001"},
        send=lambda request: {"status_code": 202, "body": "accepted"},
        trace=trace.append,
    )

    assert trace == ["callback.delivery.emit", "callback.delivery.emit_complete"]
    assert result["status"] == "delivered"
    assert result["attempts"] == 1
    assert result["completed"] is True


def test_terminal_callback_delivery_failure_records_dead_letter_metadata() -> None:
    result = deliver_callback(
        {"event": "inventory.updated", "idempotency_key": "evt-001"},
        send=lambda request: {"status_code": 410, "body": "gone"},
        retry={"max_attempts": 3},
        dead_letter=True,
    )

    assert result["status"] == "dead_lettered"
    assert result["attempts"] == 1
    assert result["dead_letter"]["event"] == "inventory.updated"
    assert result["dead_letter"]["status_code"] == 410


def test_callback_timeout_records_error_without_emit_complete() -> None:
    trace: list[str] = []

    def send(_request):
        raise TimeoutError("callback timed out")

    result = deliver_callback(
        {"event": "inventory.updated", "idempotency_key": "evt-001"},
        send=send,
        trace=trace.append,
        retry={"max_attempts": 1},
    )

    assert trace == ["callback.delivery.emit"]
    assert result["status"] == "failed"
    assert result["completed"] is False
    assert result["error_ctx"]["subevent"] == "callback.delivery.emit"
