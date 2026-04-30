from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def dispatch_subevent(event: Mapping[str, Any], table: Mapping[Any, Mapping[str, Any]]) -> str | None:
    key: Any
    if "event_key" in event:
        key = event["event_key"]
    else:
        key = (event.get("family"), event.get("subevent"))
    bucket = table.get(key)
    if bucket is None:
        return None
    handlers = tuple(bucket.get("handler_ids", ()))
    return handlers[0] if handlers else None


__all__ = ["dispatch_subevent"]
