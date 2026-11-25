from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


def compile_callback_metadata(
    callbacks: Iterable[Mapping[str, Any]],
) -> list[dict[str, object]]:
    compiled: list[dict[str, object]] = []
    for callback in callbacks:
        name = str(callback["name"])
        language = str(callback.get("language") or "python")
        row = {
            "name": name,
            "kind": callback.get("kind"),
            "language": language,
            "phase": callback.get("phase"),
            "callback_ref": name,
            "ffi_boundary": language,
        }
        compiled.append({key: value for key, value in row.items() if value is not None})
    return compiled


def callback_hook_phases(timing: str, *, durable_intent: bool) -> tuple[str, ...]:
    """Select legal source-operation phases for callback preparation and delivery."""
    if timing == "pre_commit":
        return ("PRE_COMMIT",)
    if timing == "worker":
        if not durable_intent:
            raise ValueError("Worker callbacks require durable intent")
        return ("PRE_COMMIT",)
    if timing not in {"post_commit", "after_emit"}:
        raise ValueError(f"Unsupported callback timing: {timing}")
    return ("PRE_COMMIT", "POST_COMMIT") if durable_intent else ("POST_COMMIT",)


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


__all__ = [
    "callback_hook_phases",
    "compile_callback_delivery_plan",
    "compile_callback_metadata",
]
