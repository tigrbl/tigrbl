from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any


class CallbackRuntimeError(ValueError):
    def __init__(self, message: str, *, metadata: Mapping[str, object]) -> None:
        super().__init__(message)
        self.metadata = dict(metadata)


def register_callback(
    *, name: str, kind: str, language: str = "python", phase: str | None = None
) -> dict[str, object]:
    descriptor = {
        "name": name,
        "kind": kind,
        "language": language,
        "phase": phase,
        "callback_fence": "required",
    }
    return {key: value for key, value in descriptor.items() if value is not None}


def run_callback_fence(
    descriptor: Mapping[str, Any],
    *,
    callback: Callable[[Mapping[str, Any]], object] | None,
    ctx: Mapping[str, Any],
    trace: Callable[[str], None] | None = None,
    capture_errors: bool = False,
) -> object:
    name = str(descriptor.get("name") or "")
    kind = str(descriptor.get("kind") or "")
    if callback is None:
        raise CallbackRuntimeError(
            f"callback missing: {name}",
            metadata={"callback": name, "kind": kind, "error": "callback_missing"},
        )

    if trace:
        trace(f"callback_fence_enter:{name}")
    try:
        result = callback(ctx)
    except Exception as exc:
        if not capture_errors:
            raise
        return {
            "ok": False,
            "error_ctx": {
                "callback": name,
                "kind": kind,
                "phase": descriptor.get("phase"),
                "message": str(exc),
            },
        }
    if trace:
        trace(f"callback_fence_exit:{name}")
    return result


def encode_callback_descriptor(descriptor: Mapping[str, Any]) -> dict[str, object]:
    return dict(descriptor)


def decode_callback_descriptor(encoded: Mapping[str, Any]) -> dict[str, object]:
    return dict(encoded)


__all__ = [
    "CallbackRuntimeError",
    "decode_callback_descriptor",
    "encode_callback_descriptor",
    "register_callback",
    "run_callback_fence",
]
