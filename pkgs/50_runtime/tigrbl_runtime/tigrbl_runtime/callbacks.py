from __future__ import annotations

import asyncio
import hashlib
import http.client
import inspect
from urllib.parse import urlsplit
import hmac
import json
from collections.abc import Callable, Mapping
from typing import Any


def compile_callback_delivery_plan(
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
        "completion_subevent": "callback.delivery.emit_complete",
    }


def build_callback_payload(
    *, event: str, data: Mapping[str, Any], idempotency_key: str
) -> dict[str, object]:
    return {
        "event": event,
        "data": dict(data),
        "idempotency_key": idempotency_key,
    }


def sign_callback_payload(payload: Mapping[str, Any], *, secret: str) -> dict[str, object]:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    digest = hmac.new(secret.encode("utf-8"), canonical, hashlib.sha256).hexdigest()
    return {"payload": dict(payload), "signature": f"sha256={digest}"}


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


def _post_callback(endpoint, body, headers, timeout):
    url = urlsplit(endpoint)
    connection_type = (
        http.client.HTTPSConnection if url.scheme == "https" else http.client.HTTPConnection
    )
    connection = connection_type(url.hostname, url.port, timeout=timeout)
    path = url.path or "/"
    if url.query:
        path = f"{path}?{url.query}"
    try:
        connection.request("POST", path, body=body, headers=headers)
        response = connection.getresponse()
        return {"status_code": response.status, "body": response.read(65537)[:65536].decode("utf-8", "replace")}
    finally:
        connection.close()


async def attempt_callback(endpoint, payload, *, timeout, secret=None, send=None):
    """Execute one compiled HTTP attempt and return its observed outcome."""
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    headers = {
        "Content-Type": "application/json",
        "Idempotency-Key": payload["idempotency_key"],
    }
    if secret is not None:
        headers["X-Webhook-Signature"] = sign_callback_payload(payload, secret=secret)["signature"]
    sender = send or _post_callback
    try:
        if inspect.iscoroutinefunction(sender):
            pending = sender(endpoint, body, headers, timeout)
        else:
            pending = asyncio.to_thread(sender, endpoint, body, headers, timeout)
        response = await asyncio.wait_for(pending, timeout=timeout)
        code = int(response["status_code"])
    except (TimeoutError, asyncio.TimeoutError):
        return {"status": "unknown", "error": "timeout", "retryable": True}
    except Exception as exc:
        return {"status": "unknown", "error": type(exc).__name__, "retryable": True}
    return {
        "status": "delivered" if 200 <= code < 300 else "failed",
        "http_status": code,
        "response_body": response.get("body"),
        "retryable": _is_transient(code),
    }


def _is_transient(status_code: int) -> bool:
    return status_code == 429 or 500 <= status_code < 600


__all__ = [
    "attempt_callback",
    "build_callback_payload",
    "compile_callback_delivery_plan",
    "deliver_callback",
    "sign_callback_payload",
]
