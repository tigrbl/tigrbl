from __future__ import annotations

import pytest

from tigrbl_runtime.protocol._iterators import aclose_if_supported, iter_items


@pytest.mark.asyncio
async def test_iter_items_preserves_async_iteration_order_without_prebuffering() -> None:
    produced: list[int] = []

    async def source():
        for idx in range(3):
            produced.append(idx)
            yield idx

    seen: list[int] = []
    async for item in iter_items(source()):
        seen.append(item)
        if len(seen) == 2:
            break

    assert seen == [0, 1]
    assert produced == [0, 1]


@pytest.mark.asyncio
async def test_iter_items_accepts_sync_iterables() -> None:
    seen: list[int] = []
    async for item in iter_items(iter((1, 2, 3))):
        seen.append(item)

    assert seen == [1, 2, 3]


@pytest.mark.asyncio
async def test_iter_items_treats_bytes_as_single_item() -> None:
    seen: list[object] = []
    async for item in iter_items(b"abc"):
        seen.append(item)

    assert seen == [b"abc"]


@pytest.mark.asyncio
async def test_aclose_if_supported_finalizes_async_generators() -> None:
    finalized: list[str] = []

    async def source():
        try:
            yield 1
            yield 2
        finally:
            finalized.append("done")

    gen = source()
    async for item in iter_items(gen):
        assert item == 1
        break

    await aclose_if_supported(gen)

    assert finalized == ["done"]
