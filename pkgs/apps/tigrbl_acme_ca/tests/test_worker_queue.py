import asyncio

import pytest

from tigrbl_acme_ca.workers.queue import (
    InMemoryAsyncQueue,
    QueueClosedError,
    from_ctx,
)


@pytest.mark.asyncio
async def test_in_memory_queue_preserves_fifo_order_and_depth() -> None:
    queue = InMemoryAsyncQueue(max_items=2)

    await queue.enqueue({"id": "first"})
    await queue.enqueue({"id": "second"})

    assert queue.max_items == 2
    assert queue.size == 2
    assert await queue.dequeue(timeout=0.01) == {"id": "first"}
    assert await queue.dequeue(timeout=0.01) == {"id": "second"}
    assert queue.size == 0


@pytest.mark.asyncio
async def test_in_memory_queue_applies_backpressure_timeout() -> None:
    queue = InMemoryAsyncQueue(max_items=1)

    await queue.enqueue({"id": "held"})

    with pytest.raises(asyncio.TimeoutError):
        await queue.enqueue({"id": "blocked"}, timeout=0.01)

    assert await queue.dequeue(timeout=0.01) == {"id": "held"}


@pytest.mark.asyncio
async def test_in_memory_queue_dequeue_timeout_returns_none() -> None:
    queue = InMemoryAsyncQueue(max_items=1)

    assert await queue.dequeue(timeout=0.01) is None


@pytest.mark.asyncio
async def test_in_memory_queue_close_rejects_new_work() -> None:
    queue = InMemoryAsyncQueue(max_items=1)

    await queue.enqueue({"id": "drainable"})
    queue.close()

    with pytest.raises(QueueClosedError):
        await queue.enqueue({"id": "new"}, timeout=0.01)

    assert queue.closed is True
    assert await queue.dequeue(timeout=0.01) == {"id": "drainable"}
    assert await queue.dequeue(timeout=0.01) is None


def test_from_ctx_uses_injected_queue_or_bounded_config() -> None:
    injected = InMemoryAsyncQueue(max_items=3)

    assert from_ctx({"task_queue": injected}) is injected

    configured = from_ctx({"config": {"acme.task_queue_max_items": 7}})

    assert isinstance(configured, InMemoryAsyncQueue)
    assert configured.max_items == 7
