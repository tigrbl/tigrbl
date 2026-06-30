"""RFC 8785-style canonical JSON helpers for proof-bound payloads."""

from __future__ import annotations

import json
import math
from decimal import Decimal
from typing import Any


def _reject_non_finite_numbers(value: Any) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("JCS canonical JSON requires finite JSON numbers")
    if isinstance(value, Decimal) and not value.is_finite():
        raise ValueError("JCS canonical JSON requires finite JSON numbers")
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("JCS canonical JSON object keys must be strings")
            _reject_non_finite_numbers(item)
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            _reject_non_finite_numbers(item)


def canonicalize(payload: Any) -> str:
    """Return deterministic UTF-8 JSON text with sorted object members."""

    _reject_non_finite_numbers(payload)
    return json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def canonical_json_bytes(payload: Any) -> bytes:
    """Return deterministic UTF-8 JSON bytes with JCS rejection semantics."""

    return canonicalize(payload).encode("utf-8")


__all__ = ["canonical_json_bytes", "canonicalize"]
