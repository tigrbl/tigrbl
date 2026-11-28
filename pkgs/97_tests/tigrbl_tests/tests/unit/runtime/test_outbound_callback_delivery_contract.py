from __future__ import annotations

import pytest

from tigrbl_atoms import events
from tigrbl_atoms.atoms.transport.callback import (
    ANCHOR,
    INSTANCE,
    CallbackAttemptCtx,
    CallbackAttemptedCtx,
)
from tigrbl_kernel.atoms import _discover_atoms, _inject_atoms
from tigrbl_kernel.callbacks import compile_callback_attempt
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
    assert plan["signing"] == {
        "algorithm": "hmac-sha256",
        "secret_ref": "secret:callback",
    }
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


def test_kernel_discovers_callback_atom_without_injecting_it_into_request_phases():
    registered = [atom for atom in _discover_atoms() if atom[0] == ANCHOR]
    assert registered == [(ANCHOR, INSTANCE)]
    assert events.get_anchor_info(ANCHOR).explicit_only
    chain = {}
    _inject_atoms(chain, registered, persistent=True)
    assert chain == {}
    assert (
        compile_callback_attempt().__tigrbl_atom_name__ == "transport.callback_attempt"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("code", "status", "retryable"),
    [
        (202, "delivered", False),
        (429, "failed", True),
        (503, "failed", True),
        (410, "failed", False),
        (None, "unknown", True),
    ],
)
async def test_compiled_callback_atom_sends_one_attempt(code, status, retryable):
    calls = []

    async def send(endpoint, body, headers, timeout):
        calls.append((endpoint, body, headers, timeout))
        if code is None:
            raise TimeoutError
        return {"status_code": code, "body": "response"}

    context = CallbackAttemptCtx(
        endpoint="https://test/hooks",
        payload={"idempotency_key": "event-1"},
        timeout=2,
        secret="test-secret",
        send=send,
    )
    result = await compile_callback_attempt()(context)

    assert isinstance(result, CallbackAttemptedCtx)
    assert result.outcome["status"] == status
    assert result.outcome["retryable"] is retryable
    if code is None:
        assert result.outcome["error"] == "timeout"
    else:
        assert result.outcome["http_status"] == code
        assert result.outcome["response_body"] == "response"
    ((endpoint, body, headers, timeout),) = calls
    assert (endpoint, body, timeout) == (
        "https://test/hooks",
        b'{"idempotency_key":"event-1"}',
        2,
    )
    assert headers["Idempotency-Key"] == "event-1"
    assert (
        headers["X-Webhook-Signature"]
        == sign_callback_payload(context.payload, secret="test-secret")["signature"]
    )
