from __future__ import annotations

import hashlib
import hmac
import json
from collections.abc import Callable, Mapping
from typing import Any


def compile_webhook_delivery_plan(
    *,
    event: str,
    endpoint: str,
    signing_secret_ref: str | None = None,
    retry: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    return {
        "event": event,
        "endpoint": endpoint,
        "signing": {"algorithm": "hmac-sha256", "secret_ref": signing_secret_ref},
        "retry": dict(retry or {"max_attempts": 1}),
        "completion_subevent": "webhook.delivery.emit_complete",
    }


def build_webhook_payload(
    *, event: str, data: Mapping[str, Any], idempotency_key: str
) -> dict[str, object]:
    return {
        "event": event,
        "data": dict(data),
        "idempotency_key": idempotency_key,
    }


def sign_webhook_payload(payload: Mapping[str, Any], *, secret: str) -> dict[str, object]:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    digest = hmac.new(secret.encode("utf-8"), canonical, hashlib.sha256).hexdigest()
    return {"payload": dict(payload), "signature": f"sha256={digest}"}


def deliver_webhook(
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
            trace("webhook.delivery.emit")
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
                    "subevent": "webhook.delivery.emit",
                    "message": str(exc),
                },
            }
        last_response = response
        status_code = int(response.get("status_code", 0))
        if 200 <= status_code < 300:
            if trace:
                trace("webhook.delivery.emit_complete")
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


def _is_transient(status_code: int) -> bool:
    return status_code == 429 or 500 <= status_code < 600


__all__ = [
    "build_webhook_payload",
    "compile_webhook_delivery_plan",
    "deliver_webhook",
    "sign_webhook_payload",
]
