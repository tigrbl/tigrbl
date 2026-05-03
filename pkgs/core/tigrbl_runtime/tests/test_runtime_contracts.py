from types import SimpleNamespace

import pytest

from tigrbl_runtime.executors import (
    ExecutorBase,
    NumbaPackedPlanExecutor,
    PackedPlanExecutor,
)
from tigrbl_runtime.runtime import Runtime, RuntimeBase
import tigrbl_runtime.runtime.runtime as runtime_module


def test_runtime_and_executor_contracts_available() -> None:
    assert issubclass(Runtime, RuntimeBase)
    assert issubclass(PackedPlanExecutor, ExecutorBase)
    assert issubclass(NumbaPackedPlanExecutor, ExecutorBase)


def test_runtime_registers_default_executors() -> None:
    runtime = Runtime()
    assert set(runtime.executors) == {"packed", "numba_packed"}


def test_runtime_attaches_self_to_executors() -> None:
    runtime = Runtime()
    assert runtime.executors["packed"].runtime is runtime
    assert runtime.executors["numba_packed"].runtime is runtime


def test_runtime_default_executor_is_numba_packed() -> None:
    runtime = Runtime()
    assert runtime.default_executor == "numba_packed"


@pytest.mark.asyncio
async def test_runtime_skips_channel_prelude_when_executor_requests_it(monkeypatch) -> None:
    calls: list[str] = []

    class _Executor(ExecutorBase):
        name = "test"

        def should_skip_channel_prelude(self, **kwargs):
            calls.append("skip-check")
            return True

        async def invoke(self, **kwargs):
            calls.append("invoke")
            return "ok"

    async def _fail_prepare(*args, **kwargs):
        raise AssertionError("prepare_channel_context should be skipped")

    async def _fail_complete(*args, **kwargs):
        raise AssertionError("complete_channel should be skipped")

    monkeypatch.setattr(runtime_module, "prepare_channel_context", _fail_prepare)
    monkeypatch.setattr(runtime_module, "complete_channel", _fail_complete)

    runtime = Runtime(default_executor="test")
    runtime.register_executor(_Executor())

    result = await runtime.invoke(
        executor="test",
        env=SimpleNamespace(scope={"type": "websocket", "path": "/ws/echo"}),
        ctx={},
        plan=SimpleNamespace(),
        packed_plan=None,
    )

    assert result == "ok"
    assert calls == ["skip-check", "invoke"]
