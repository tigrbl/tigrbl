from __future__ import annotations

from collections.abc import Iterable


_RECEIVE_CAPABILITIES = {"recv", "receive"}


def select_loop_mode(
    *,
    binding: str,
    subevent_handlers: Iterable[str] = (),
    explicit_mode: str | None = None,
    capabilities: Iterable[str] = (),
) -> str:
    handlers = tuple(subevent_handlers or ())
    caps = {str(capability) for capability in capabilities or ()}
    if explicit_mode not in {None, "owner", "dispatch"}:
        raise ValueError(f"unsupported loop mode {explicit_mode!r}")

    if explicit_mode == "owner" and handlers:
        raise ValueError("owner loop mode cannot be selected with dispatch handlers")
    if explicit_mode == "dispatch":
        if not handlers:
            raise ValueError("dispatch loop mode requires subevent handlers")
        if caps and caps.isdisjoint(_RECEIVE_CAPABILITIES):
            raise ValueError("dispatch loop mode requires receive capability")
        return "dispatch"
    if explicit_mode == "owner":
        return "owner"
    return "dispatch" if handlers else "owner"


__all__ = ["select_loop_mode"]
