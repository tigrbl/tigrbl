from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def stats(ctx: Mapping[str, Any]) -> dict[str, Any]:
    """Return MemLRU statistics from the runtime-provided engine session."""
    session = ctx.get("db")
    if session is None:
        raise RuntimeError("MemLRU stats requires an engine session")
    return session.stats()


__all__ = ["stats"]
