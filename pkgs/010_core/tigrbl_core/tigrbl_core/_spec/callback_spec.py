from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from math import isfinite
from typing import Any, Literal
from urllib.parse import urlsplit

from .serde import SerdeMixin

CallbackTiming = Literal["post_commit", "worker", "after_emit", "pre_commit"]
CallbackDurability = Literal["none", "results", "attempts", "attempts_and_results"]


@dataclass(frozen=True)
class CallbackSpec(SerdeMixin):
    """Authoring input for outbound delivery attached to an existing op."""

    ops: str | tuple[str, ...]
    event: str
    destination: str
    payload: Callable[..., Any]
    delivery: CallbackTiming = "post_commit"
    durability: CallbackDurability = "none"
    timeout_seconds: float = 5.0
    max_attempts: int = 1
    retry_delay_seconds: float = 1.0
    total_timeout_seconds: float = 10.0
    emit_wait_seconds: float = 300.0
    signing_secret_ref: str | None = None
    session_factory: Callable[..., Any] | None = None
    resolve_secret: Callable[..., Any] | None = None
    send: Callable[..., Any] | None = None
    record_intent: Callable[..., Any] | None = None
    record_outcome: Callable[..., Any] | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.ops, str):
            object.__setattr__(self, "ops", tuple(self.ops))
        aliases = (self.ops,) if isinstance(self.ops, str) else self.ops
        if not aliases or any(
            not isinstance(alias, str) or not alias or alias == "*" for alias in aliases
        ):
            raise ValueError("CallbackSpec requires explicit source operation aliases")
        if not self.event or not callable(self.payload):
            raise ValueError("CallbackSpec requires an event and payload builder")
        url = urlsplit(self.destination)
        if (
            url.scheme not in {"http", "https"}
            or not url.hostname
            or url.username
            or url.fragment
        ):
            raise ValueError("Callback destination must be an absolute HTTP(S) URL")
        if self.delivery not in {"post_commit", "worker", "after_emit", "pre_commit"}:
            raise ValueError("Invalid callback timing")
        if self.durability not in {
            "none",
            "results",
            "attempts",
            "attempts_and_results",
        }:
            raise ValueError("Invalid callback durability")
        if not all(
            isfinite(value) and value > 0
            for value in (
                self.timeout_seconds,
                self.total_timeout_seconds,
                self.emit_wait_seconds,
            )
        ):
            raise ValueError("Callback timeouts must be finite and positive")
        if (
            isinstance(self.max_attempts, bool)
            or not isinstance(self.max_attempts, int)
            or self.max_attempts < 1
        ):
            raise ValueError("Callback max_attempts must be a positive integer")
        if not isfinite(self.retry_delay_seconds) or self.retry_delay_seconds < 0:
            raise ValueError("Callback retry delay must be finite and nonnegative")
        if self.durability != "none" and self.session_factory is None:
            raise ValueError("Durable callback policies require a session_factory")
        if self.delivery == "worker" and self.durability not in {
            "attempts",
            "attempts_and_results",
        }:
            raise ValueError("Worker delivery requires durable attempts")
        if self.record_intent is not None and self.durability not in {
            "attempts",
            "attempts_and_results",
        }:
            raise ValueError("record_intent requires durable attempts")
        if self.record_outcome is not None and self.durability not in {
            "results",
            "attempts_and_results",
        }:
            raise ValueError("record_outcome requires durable results")
        if self.signing_secret_ref and self.resolve_secret is None:
            raise ValueError(
                "A callback signing secret reference requires resolve_secret"
            )
