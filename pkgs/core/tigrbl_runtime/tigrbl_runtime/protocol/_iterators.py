from __future__ import annotations

from collections.abc import AsyncIterator, Iterable
from typing import Any


async def iter_items(source: object) -> AsyncIterator[object]:
    if isinstance(source, (bytes, bytearray, memoryview, str)):
        yield source
        return
    if hasattr(source, "__aiter__"):
        async for item in source:  # type: ignore[union-attr]
            yield item
        return
    if isinstance(source, Iterable):
        for item in source:
            yield item


async def aclose_if_supported(source: object) -> None:
    close = getattr(source, "aclose", None)
    if callable(close):
        await close()


__all__ = ["aclose_if_supported", "iter_items"]
