from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any


ACK_VALUES = {"ack", "sent", "complete", "completed"}


def _completion_name(subevent: str) -> str:
    return subevent if subevent.endswith("_complete") else f"{subevent}_complete"


async def emit_with_fence(
    event: dict[str, Any],
    *,
    send: Callable[[dict[str, Any]], Awaitable[Any]],
    trace: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    subevent = str(event.get("subevent", "message.emit"))
    completed_subevent = _completion_name(subevent)
    result: dict[str, Any] = {
        "completion_fence": "POST_EMIT",
        "completed": False,
        "completed_subevent": completed_subevent,
    }
    try:
        send_result = await send(event)
    except Exception as exc:
        result["error_ctx"] = {"subevent": subevent, "message": str(exc)}
        return result

    values = send_result if isinstance(send_result, tuple) else (send_result,)
    if any(value in ACK_VALUES for value in values):
        if trace is not None:
            trace(completed_subevent)
        result["completed"] = True
    return result


__all__ = ["ACK_VALUES", "emit_with_fence"]
