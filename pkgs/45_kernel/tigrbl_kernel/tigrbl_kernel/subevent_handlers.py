from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from .eventkey import pack_event_key


def _code(value: str, *, modulo: int = 251) -> int:
    return sum(ord(ch) for ch in value) % modulo


def _event_key(family: str, subevent: str) -> int:
    return pack_event_key(
        op=0,
        binding=0,
        exchange=0,
        family=_code(family),
        subevent=_code(subevent, modulo=1021),
        framing=0,
    )


def compile_subevent_handlers(
    handlers: Iterable[Mapping[str, Any]],
    *,
    key_mode: str = "tuple",
    allow_multi: bool = False,
    loop_mode: str = "dispatch",
) -> dict[Any, dict[str, Any]]:
    if loop_mode == "owner":
        raise ValueError("owner loop mode cannot include dispatch subevent handlers")

    grouped: dict[tuple[str, str], list[Mapping[str, Any]]] = {}
    for handler in handlers:
        if handler.get("kind") == "hook" or "phase" in handler and handler.get("kind") != "subevent_handler":
            raise ValueError("phase-bound hook cannot be used as subevent_ctx handler")
        key = (str(handler["family"]), str(handler["subevent"]))
        grouped.setdefault(key, []).append(handler)

    table: dict[Any, dict[str, Any]] = {}
    for (family, subevent), bucket in grouped.items():
        if len(bucket) > 1 and not allow_multi:
            raise ValueError("ambiguous subevent handler order for EventKey")
        ordered = sorted(bucket, key=lambda item: int(item.get("order", 0)))
        out = {"handler_ids": tuple(str(item["handler_id"]) for item in ordered)}
        key: Any = _event_key(family, subevent) if key_mode == "eventkey" else (family, subevent)
        table[key] = out
    return table


__all__ = ["compile_subevent_handlers"]
