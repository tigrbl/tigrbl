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


def compile_hook_buckets(
    *,
    hooks: Iterable[Mapping[str, Any]],
    event_catalog: Iterable[Mapping[str, Any]],
    allow_ordered_multi: bool = False,
) -> dict[str, dict[str, Any]]:
    events = tuple(event_catalog)
    by_family: dict[str, list[Mapping[str, Any]]] = {}
    for event in events:
        by_family.setdefault(str(event["family"]), []).append(event)

    exact: dict[tuple[str, str], list[Mapping[str, Any]]] = {}
    wildcards: dict[str, list[Mapping[str, Any]]] = {}
    for hook in hooks:
        family = str(hook["family"])
        subevent = str(hook["subevent"])
        if subevent == "*":
            wildcards.setdefault(family, []).append(hook)
        else:
            if not any(
                str(event["family"]) == family and str(event["subevent"]) == subevent
                for event in events
            ):
                raise ValueError("event catalog does not contain hook selector")
            exact.setdefault((family, subevent), []).append(hook)

    buckets: dict[str, dict[str, Any]] = {}
    for event in events:
        family = str(event["family"])
        subevent = str(event["subevent"])
        selected = exact.get((family, subevent)) or wildcards.get(family) or []
        if not selected:
            continue
        if len(selected) > 1 and not allow_ordered_multi:
            raise ValueError("hook bucket collision is ambiguous")
        ordered = sorted(selected, key=lambda hook: int(hook.get("order", 0)))
        buckets[subevent] = {
            "event_key": _event_key(family, subevent),
            "hook_ids": tuple(str(hook["hook_id"]) for hook in ordered),
        }
    return buckets


def lookup_hook_bucket(event_key: int, table: Mapping[int, tuple[str, ...]]) -> tuple[str, ...] | None:
    if not isinstance(event_key, int):
        raise TypeError("EventKey lookup requires an integer code, not a string selector")
    return table.get(event_key)


__all__ = ["compile_hook_buckets", "lookup_hook_bucket"]
