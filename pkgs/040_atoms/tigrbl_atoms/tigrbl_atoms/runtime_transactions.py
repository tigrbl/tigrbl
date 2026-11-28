from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any


def run_subevent_tx_unit(
    ctx: Mapping[str, Any],
    *,
    handler: Callable[[Mapping[str, Any]], Any],
    trace: Callable[[str], None] | None = None,
    capture_errors: bool = False,
) -> Any:
    subevent = str(ctx.get("subevent", ""))
    tx_unit = str(ctx.get("tx_unit", "none"))
    transactional = tx_unit != "none"

    def record(item: str) -> None:
        if trace is not None:
            trace(item)

    try:
        if transactional:
            record(f"tx.begin:{subevent}")
        record("handler.call")
        result = handler(ctx)
        if transactional:
            record(f"tx.commit:{subevent}")
        return result
    except Exception as exc:
        if transactional:
            record(f"tx.rollback:{subevent}")
        if not capture_errors:
            raise
        return {
            "error_ctx": {
                "subevent": subevent,
                "rollback": tx_unit,
                "message": str(exc),
            }
        }


__all__ = ["run_subevent_tx_unit"]
