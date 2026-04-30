from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def create_channel_state(
    *,
    channel_id: str,
    binding: str,
    family: str,
    peer: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "channel_id": channel_id,
        "binding": binding,
        "family": family,
        "peer": dict(peer or {}),
        "open": True,
        "closed": False,
        "received_count": 0,
        "emit_count": 0,
        "completion_state": "idle",
    }


def transition_channel_state(
    state: Mapping[str, Any],
    *,
    subevent: str,
    payload_size: int | None = None,
    close_code: int | None = None,
    close_reason: str | None = None,
) -> dict[str, Any]:
    if state.get("closed"):
        raise ValueError("channel state transition rejected after closed")
    next_state = dict(state)
    next_state["current_subevent"] = subevent
    if payload_size is not None:
        next_state["last_payload_size"] = payload_size
    if subevent.endswith(".received"):
        next_state["received_count"] = int(next_state.get("received_count", 0)) + 1
    if subevent.endswith(".emit"):
        next_state["emit_count"] = int(next_state.get("emit_count", 0)) + 1
        next_state["completion_state"] = "pending"
    if subevent.endswith(".emit_complete"):
        next_state["completion_state"] = "complete"
    if subevent.endswith(".close"):
        next_state["open"] = False
        next_state["closed"] = True
        next_state["close_code"] = close_code
        if close_reason is not None:
            next_state["close_reason"] = close_reason
    return next_state


def build_channel_error_ctx(
    state: Mapping[str, Any],
    *,
    subevent: str,
    phase: str,
    exc: BaseException,
) -> dict[str, Any]:
    return {
        "channel_id": state.get("channel_id"),
        "binding": state.get("binding"),
        "family": state.get("family"),
        "subevent": subevent,
        "phase": phase,
        "message": str(exc),
    }


__all__ = [
    "build_channel_error_ctx",
    "create_channel_state",
    "transition_channel_state",
]
