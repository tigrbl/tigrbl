from __future__ import annotations

import importlib

import pytest


def _require(module_name: str, attr_name: str):
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        pytest.xfail(f"{module_name} is not implemented")
    value = getattr(module, attr_name, None)
    if value is None:
        pytest.xfail(f"{module_name}.{attr_name} is not implemented")
    return value


def _sync_chunks():
    yield b"a"
    yield b"b"


async def _async_chunks():
    yield b"a"
    yield b"b"


@pytest.mark.asyncio
async def test_iterator_producer_normalizes_sync_and_async_iterators() -> None:
    normalize = _require("tigrbl_runtime.protocol.iterators", "normalize_iterator_producer")

    sync_producer = normalize(_sync_chunks(), chunk_type="bytes")
    async_producer = normalize(_async_chunks(), chunk_type="bytes")

    assert [item async for item in sync_producer] == [b"a", b"b"]
    assert [item async for item in async_producer] == [b"a", b"b"]


@pytest.mark.asyncio
async def test_iterator_producer_normalizes_single_yield_callable() -> None:
    normalize = _require("tigrbl_runtime.protocol.iterators", "normalize_iterator_producer")

    producer = normalize(lambda: b"only", chunk_type="bytes")

    assert [item async for item in producer] == [b"only"]


@pytest.mark.asyncio
async def test_iterator_producer_preserves_empty_iterator_completion() -> None:
    normalize = _require("tigrbl_runtime.protocol.iterators", "normalize_iterator_producer")

    producer = normalize(iter(()), chunk_type="bytes")

    assert [item async for item in producer] == []


@pytest.mark.asyncio
async def test_iterator_producer_maps_exceptions_and_runs_finalization() -> None:
    normalize = _require("tigrbl_runtime.protocol.iterators", "normalize_iterator_producer")
    finalized: list[str] = []

    def failing():
        yield b"ok"
        raise RuntimeError("broken")

    producer = normalize(failing(), chunk_type="bytes", finalizer=lambda: finalized.append("done"))

    with pytest.raises(RuntimeError, match="broken"):
        [item async for item in producer]
    assert finalized == ["done"]


@pytest.mark.asyncio
async def test_iterator_producer_runs_finalizer_on_consumer_cancellation() -> None:
    normalize = _require("tigrbl_runtime.protocol.iterators", "normalize_iterator_producer")
    finalized: list[str] = []

    async def chunks():
        yield b"a"
        yield b"b"

    producer = normalize(chunks(), chunk_type="bytes", finalizer=lambda: finalized.append("done"))
    assert await anext(producer) == b"a"
    await producer.aclose()

    assert finalized == ["done"]


@pytest.mark.asyncio
async def test_iterator_producer_rejects_invalid_chunk_type_before_transport_emit() -> None:
    normalize = _require("tigrbl_runtime.protocol.iterators", "normalize_iterator_producer")

    async def invalid():
        yield {"not": "bytes"}

    producer = normalize(invalid(), chunk_type="bytes")
    with pytest.raises(TypeError, match="chunk|bytes"):
        [item async for item in producer]


@pytest.mark.asyncio
async def test_iterator_producer_cannot_be_reiterated_after_close() -> None:
    normalize = _require("tigrbl_runtime.protocol.iterators", "normalize_iterator_producer")

    producer = normalize(_sync_chunks(), chunk_type="bytes")
    assert await anext(producer) == b"a"
    await producer.aclose()

    with pytest.raises(RuntimeError, match="closed|exhausted|reiterate"):
        await anext(producer)
