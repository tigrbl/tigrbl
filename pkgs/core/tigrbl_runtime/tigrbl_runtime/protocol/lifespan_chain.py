from __future__ import annotations

from collections.abc import Callable
from typing import Any


def run_lifespan_chain(
    *,
    event: str,
    handlers: tuple[Callable[[dict[str, Any]], object], ...] = (),
    initial_state: dict[str, Any] | None = None,
    trace: Callable[[str], None] | None = None,
    capture_errors: bool = False,
) -> dict[str, object]:
    if event not in {"startup", "shutdown"}:
        raise ValueError("lifespan event must be startup or shutdown")
    state = dict(initial_state or {})
    if "ready" in state:
        state.pop("ready")

    def emit(atom: str) -> None:
        if trace:
            trace(atom)

    emit(f"lifespan.{event}.received")
    try:
        for handler in handlers:
            emit(f"lifespan.{event}.handler")
            handler(state)
    except Exception as exc:
        if not capture_errors:
            raise
        return {
            "ready": False,
            "completed": False,
            "state": state,
            "error_ctx": {
                "subevent": f"lifespan.{event}",
                "phase": "HANDLER",
                "message": str(exc),
            },
        }

    ready = event == "startup"
    emit(f"lifespan.{event}.complete")
    return {"ready": ready, "completed": True, "state": state}


__all__ = ["run_lifespan_chain"]
