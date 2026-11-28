"""Outbound HTTP callback preparation and one-attempt transport atom."""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import http.client
import inspect
import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlsplit

from ... import events as _ev
from ...stages import Egressed, Emitting
from ...types import Atom, BaseCtx


# This carrier event is selected by callback plans outside the request atom chain.
ANCHOR = _ev.CALLBACK_DELIVERY_EMIT


@dataclass(slots=True, kw_only=True)
class CallbackAttemptCtx(BaseCtx[Emitting, Exception]):
    endpoint: str
    payload: Mapping[str, Any]
    timeout: float
    secret: str | None = field(default=None, repr=False)
    send: Callable[..., Any] | None = field(default=None, repr=False)


@dataclass(slots=True, kw_only=True)
class CallbackAttemptedCtx(BaseCtx[Egressed, Exception]):
    outcome: dict[str, Any]


def build_callback_payload(
    *, event: str, data: Mapping[str, Any], idempotency_key: str
) -> dict[str, object]:
    return {
        "event": event,
        "data": dict(data),
        "idempotency_key": idempotency_key,
    }


def sign_callback_payload(
    payload: Mapping[str, Any], *, secret: str
) -> dict[str, object]:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    digest = hmac.new(secret.encode("utf-8"), canonical, hashlib.sha256).hexdigest()
    return {"payload": dict(payload), "signature": f"sha256={digest}"}


def _post_callback(endpoint, body, headers, timeout):
    url = urlsplit(endpoint)
    connection_type = (
        http.client.HTTPSConnection
        if url.scheme == "https"
        else http.client.HTTPConnection
    )
    connection = connection_type(url.hostname, url.port, timeout=timeout)
    path = url.path or "/"
    if url.query:
        path = f"{path}?{url.query}"
    try:
        connection.request("POST", path, body=body, headers=headers)
        response = connection.getresponse()
        return {
            "status_code": response.status,
            "body": response.read(65537)[:65536].decode("utf-8", "replace"),
        }
    finally:
        connection.close()


async def attempt_callback(endpoint, payload, *, timeout, secret=None, send=None):
    """Execute one compiled HTTP attempt and return its observed outcome."""
    body = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()
    headers = {
        "Content-Type": "application/json",
        "Idempotency-Key": payload["idempotency_key"],
    }
    if secret is not None:
        headers["X-Webhook-Signature"] = sign_callback_payload(payload, secret=secret)[
            "signature"
        ]
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


class AtomImpl(Atom[Emitting, Egressed, Exception]):
    name = "transport.callback_attempt"
    anchor = ANCHOR

    async def __call__(
        self, obj: object | None, ctx: CallbackAttemptCtx
    ) -> CallbackAttemptedCtx:
        outcome = await attempt_callback(
            ctx.endpoint,
            ctx.payload,
            timeout=ctx.timeout,
            secret=ctx.secret,
            send=ctx.send,
        )
        return ctx.promote(CallbackAttemptedCtx, outcome=outcome)


INSTANCE = AtomImpl()


__all__ = [
    "ANCHOR",
    "INSTANCE",
    "CallbackAttemptCtx",
    "CallbackAttemptedCtx",
    "attempt_callback",
    "build_callback_payload",
    "sign_callback_payload",
]
