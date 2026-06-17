from __future__ import annotations

import hashlib
import hmac
import json
import re
import time
from collections.abc import Callable, Mapping
from typing import Any

from tigrbl_core._spec import HttpRestBindingSpec, OpSpec, PathSpec


class InboundWebhookError(ValueError):
    pass


class InboundWebhookSignatureError(InboundWebhookError):
    pass


class InboundWebhookReplayError(InboundWebhookError):
    pass


def define_inbound_webhook(
    *,
    path: str,
    provider: str,
    event_type: str,
    handler: Callable[..., Any] | None = None,
    alias: str | None = None,
    proto: str = "https.rest",
    request_model: Any | None = None,
    response_model: Any | None = None,
    signature_header: str = "X-Tigrbl-Signature",
    signing_secret_ref: str | None = None,
    timestamp_header: str | None = "X-Tigrbl-Timestamp",
    timestamp_tolerance_seconds: int = 300,
    idempotency_header: str = "Idempotency-Key",
    ack_status_code: int = 202,
    failure_status_code: int = 401,
) -> PathSpec:
    selected_alias = alias or _webhook_alias(provider=provider, event_type=event_type)
    policy = {
        "direction": "inbound",
        "provider": provider,
        "event_type": event_type,
        "signature": {
            "algorithm": "hmac-sha256",
            "header": signature_header,
            "secret_ref": signing_secret_ref,
            "timestamp_header": timestamp_header,
            "timestamp_tolerance_seconds": timestamp_tolerance_seconds,
        },
        "idempotency": {"header": idempotency_header},
        "ack": {
            "status_code": ack_status_code,
            "failure_status_code": failure_status_code,
        },
    }
    binding = HttpRestBindingSpec(
        proto=proto,  # type: ignore[arg-type]
        methods=("POST",),
        path=path,
    )
    op = OpSpec(
        alias=selected_alias,
        target="custom",
        expose_rpc=False,
        bindings=(binding,),
        http_methods=("POST",),
        status_code=ack_status_code,
        request_model=request_model,
        response_model=response_model,
        handler=handler,
        extra={"webhook": policy},
    )
    return PathSpec(path=path, kind="resource", name=selected_alias, ops=(op,))


def verify_inbound_webhook_signature(
    *,
    raw_body: bytes,
    headers: Mapping[str, str],
    secret: str,
    signature_header: str = "X-Tigrbl-Signature",
    timestamp_header: str | None = "X-Tigrbl-Timestamp",
    timestamp_tolerance_seconds: int | None = 300,
    now: float | None = None,
) -> bool:
    normalized = {str(key).lower(): str(value) for key, value in headers.items()}
    signature = normalized.get(signature_header.lower())
    if not signature:
        raise InboundWebhookSignatureError("missing inbound webhook signature")

    if timestamp_header and timestamp_tolerance_seconds is not None:
        raw_timestamp = normalized.get(timestamp_header.lower())
        if raw_timestamp is None:
            raise InboundWebhookSignatureError("missing inbound webhook timestamp")
        try:
            timestamp = int(raw_timestamp)
        except ValueError as exc:
            raise InboundWebhookSignatureError("invalid inbound webhook timestamp") from exc
        reference = int(now if now is not None else time.time())
        if abs(reference - timestamp) > int(timestamp_tolerance_seconds):
            raise InboundWebhookSignatureError("stale inbound webhook timestamp")

    expected = sign_inbound_webhook_body(raw_body=raw_body, secret=secret)
    if not hmac.compare_digest(signature, expected):
        raise InboundWebhookSignatureError("invalid inbound webhook signature")
    return True


def sign_inbound_webhook_body(*, raw_body: bytes, secret: str) -> str:
    digest = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def record_inbound_webhook_idempotency(
    *,
    idempotency_key: str,
    seen: set[str],
) -> dict[str, object]:
    if idempotency_key in seen:
        raise InboundWebhookReplayError("duplicate inbound webhook idempotency key")
    seen.add(idempotency_key)
    return {"idempotency_key": idempotency_key, "accepted": True}


def build_inbound_webhook_ack(
    *,
    idempotency_key: str,
    status_code: int = 202,
    body: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    return {
        "status_code": status_code,
        "body": dict(body or {"accepted": True, "idempotency_key": idempotency_key}),
    }


def _webhook_alias(*, provider: str, event_type: str) -> str:
    token = f"{provider}_{event_type}".lower()
    token = re.sub(r"[^a-z0-9_]+", "_", token).strip("_")
    token = re.sub(r"_+", "_", token)
    return f"webhook_{token or 'event'}"


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
    "InboundWebhookError",
    "InboundWebhookReplayError",
    "InboundWebhookSignatureError",
    "build_inbound_webhook_ack",
    "build_webhook_payload",
    "compile_webhook_delivery_plan",
    "define_inbound_webhook",
    "deliver_webhook",
    "record_inbound_webhook_idempotency",
    "sign_inbound_webhook_body",
    "sign_webhook_payload",
    "verify_inbound_webhook_signature",
]
