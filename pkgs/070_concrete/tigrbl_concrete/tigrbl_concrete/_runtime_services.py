"""Integration point between concrete lowering and its declared runtime dependency."""
from __future__ import annotations

from typing import Any
from tigrbl_runtime import lowering_services as _services

__all__ = _services.__all__


def __getattr__(name: str) -> Any:
    return getattr(_services, name)
