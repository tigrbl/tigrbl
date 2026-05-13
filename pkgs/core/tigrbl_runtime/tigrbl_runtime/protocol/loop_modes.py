from __future__ import annotations

from collections.abc import Iterable


def build_loop_controller(
    *,
    mode: str,
    binding: str,
    subevent_handlers: Iterable[str] = (),
) -> dict[str, object]:
    if mode not in {"owner", "dispatch"}:
        raise ValueError(f"unsupported runtime loop mode {mode!r}")
    handlers = tuple(subevent_handlers or ())
    return {
        "mode": mode,
        "binding": binding,
        "subevent_handlers": handlers,
        "dispatches_subevents": mode == "dispatch",
        "owner_controls_receive": mode == "owner",
    }


__all__ = ["build_loop_controller"]
