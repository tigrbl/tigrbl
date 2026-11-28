"""Compatibility helpers for callback delivery and the legacy synchronous API."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from tigrbl_atoms.atoms.transport.callback import (
    _is_transient,
    attempt_callback,
    build_callback_payload,
    sign_callback_payload,
)
from tigrbl_kernel.callbacks import compile_callback_delivery_plan


def deliver_callback(
    payload: Mapping[str, Any],
    *,
    send: Callable[[Mapping[str, Any]], Mapping[str, Any]],
    trace: Callable[[str], None] | None = None,
    retry: Mapping[str, Any] | None = None,
    dead_letter: bool = False,
) -> dict[str, object]:
    max_attempts = int((retry or {}).get("max_attempts", 1))
    attempts = 0
    last_response: Mapping[str, Any] | None = None

    for attempt in range(1, max_attempts + 1):
        attempts = attempt
        if trace and attempt == 1:
            trace("callback.delivery.emit")
        try:
            response = send(payload)
        except Exception as exc:
            if attempt < max_attempts:
                continue
            return {
                "status": "failed",
                "attempts": attempts,
                "completed": False,
                "error_ctx": {
                    "subevent": "callback.delivery.emit",
                    "message": str(exc),
                },
            }
        last_response = response
        status_code = int(response.get("status_code", 0))
        if 200 <= status_code < 300:
            if trace:
                trace("callback.delivery.emit_complete")
            return {
                "status": "delivered",
                "attempts": attempts,
                "completed": True,
                "response": dict(response),
            }
        if not _is_transient(status_code):
            break

    if dead_letter and last_response is not None:
        status_code = int(last_response.get("status_code", 0))
        return {
            "status": "dead_lettered",
            "attempts": attempts,
            "completed": False,
            "dead_letter": {
                "event": payload.get("event"),
                "idempotency_key": payload.get("idempotency_key"),
                "status_code": status_code,
                "body": last_response.get("body"),
            },
        }
    return {
        "status": "failed",
        "attempts": attempts,
        "completed": False,
        "response": dict(last_response or {}),
    }


__all__ = [
    "attempt_callback",
    "build_callback_payload",
    "compile_callback_delivery_plan",
    "deliver_callback",
    "sign_callback_payload",
]
