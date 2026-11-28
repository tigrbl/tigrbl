from __future__ import annotations

import pytest

from tigrbl import BackgroundTask


@pytest.mark.asyncio
async def test_background_task_preserves_callable_args_and_kwargs() -> None:
    calls: list[tuple[str, str]] = []

    def task(name: str, *, suffix: str) -> None:
        calls.append((name, suffix))

    background = BackgroundTask(task, "alice", suffix="done")

    assert background.func is task
    assert background.args == ("alice",)
    assert background.kwargs == {"suffix": "done"}

    await background()

    assert calls == [("alice", "done")]


@pytest.mark.asyncio
async def test_background_task_awaits_async_callable() -> None:
    calls: list[str] = []

    async def task(value: str) -> None:
        calls.append(value)

    await BackgroundTask(task, "async")()

    assert calls == ["async"]


@pytest.mark.asyncio
async def test_background_task_exceptions_propagate() -> None:
    def task() -> None:
        raise RuntimeError("background failed")

    with pytest.raises(RuntimeError, match="background failed"):
        await BackgroundTask(task)()
