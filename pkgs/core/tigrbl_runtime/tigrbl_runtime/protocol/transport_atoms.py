from __future__ import annotations

from collections.abc import Callable
from typing import Any


def run_transport_emit(
    event: dict[str, Any],
    *,
    send: Callable[[dict[str, Any]], object],
    trace: Callable[[str], None] | None = None,
) -> dict[str, object]:
    if trace is not None:
        trace("transport.emit")
    result = send(dict(event))
    completed = result == "ack"
    if completed and trace is not None:
        trace("transport.emit_complete")
    return {"completed": completed, "result": result}


__all__ = ["run_transport_emit"]
