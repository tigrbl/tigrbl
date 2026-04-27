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


async def _async_messages() -> object:
    for item in ("one", "two", "close"):
        yield item


@pytest.mark.asyncio
async def test_loop_region_executor_continues_until_governed_break_condition() -> None:
    execute_loop = _require("tigrbl_runtime.executors.loop_regions", "execute_loop_region")

    trace = await execute_loop(
        {
            "loop_id": "ws.receive",
            "role": "message",
            "producer": _async_messages(),
            "break_on": "close",
            "subevent": "message.received",
        }
    )

    assert trace["items"] == ["one", "two"]
    assert trace["exit_reason"] == "break"
    assert trace["closed"] is True


@pytest.mark.asyncio
async def test_loop_region_executor_routes_loop_local_errors_to_errorctx() -> None:
    execute_loop = _require("tigrbl_runtime.executors.loop_regions", "execute_loop_region")

    async def failing_producer() -> object:
        yield "first"
        raise RuntimeError("stream broke")

    result = await execute_loop(
        {
            "loop_id": "stream.outbound",
            "role": "stream",
            "producer": failing_producer(),
            "subevent": "stream.chunk",
        }
    )

    assert result["items"] == ["first"]
    assert result["error_ctx"]["subevent"] == "stream.chunk"
    assert result["error_ctx"]["retry_or_disconnect"] in {"retry", "disconnect", "error"}

