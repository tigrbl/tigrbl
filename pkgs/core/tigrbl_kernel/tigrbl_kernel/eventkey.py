from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

_FIELDS = (
    ("op", 20),
    ("binding", 8),
    ("exchange", 6),
    ("family", 8),
    ("subevent", 10),
    ("framing", 6),
)
_TOTAL_BITS = sum(width for _, width in _FIELDS)


def _validate_field(name: str, value: int, width: int) -> int:
    if not isinstance(value, int) or value < 0 or value >= (1 << width):
        raise ValueError(f"EventKey {name} width overflow or invalid code")
    return value


def pack_event_key(**fields: int) -> int:
    extra = set(fields) - {name for name, _ in _FIELDS}
    if extra:
        raise ValueError("EventKey reserved fields are not allowed")

    key = 0
    shift = _TOTAL_BITS
    for name, width in _FIELDS:
        shift -= width
        key |= _validate_field(name, fields.get(name, 0), width) << shift
    return key


def unpack_event_key(key: int) -> dict[str, int]:
    if not isinstance(key, int) or key < 0:
        raise ValueError("EventKey code must be a non-negative integer")
    if key >> _TOTAL_BITS:
        raise ValueError("EventKey reserved bits or overflow code")

    decoded: dict[str, int] = {}
    shift = _TOTAL_BITS
    for name, width in _FIELDS:
        shift -= width
        decoded[name] = (key >> shift) & ((1 << width) - 1)
    return decoded


def build_dispatch_table(
    entries: Mapping[int, Any] | Iterable[tuple[int, Any]],
) -> dict[int, Any]:
    iterable = entries.items() if isinstance(entries, Mapping) else entries
    table: dict[int, Any] = {}
    for key, value in iterable:
        if not isinstance(key, int):
            raise TypeError("EventKey dispatch table keys must be integer codes, not string selectors")
        unpack_event_key(key)
        if key in table:
            raise ValueError("EventKey duplicate collision in dispatch table")
        table[key] = value
    return table


__all__ = ["build_dispatch_table", "pack_event_key", "unpack_event_key"]
