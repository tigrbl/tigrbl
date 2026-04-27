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


def test_opchannel_handshake_accepts_adapter_with_required_capabilities() -> None:
    handshake = _require("tigrbl_runtime.channel.capabilities", "verify_opchannel_capabilities")

    result = handshake(
        required=("accept", "recv", "send", "close"),
        adapter={"capabilities": ("accept", "recv", "send", "close", "events")},
    )

    assert result["passed"] is True
    assert result["capability_mask"] & result["required_mask"] == result["required_mask"]


@pytest.mark.parametrize(
    ("required", "adapter"),
    (
        (("accept", "recv", "send"), {"capabilities": ("send",)}),
        (("datagrams.recv", "datagrams.send"), {"capabilities": ("recv", "send")}),
        (("chunks.send",), {"capabilities": (), "stale": True}),
    ),
)
def test_opchannel_handshake_fails_before_execution_when_capabilities_are_missing(
    required: tuple[str, ...], adapter: dict[str, object]
) -> None:
    handshake = _require("tigrbl_runtime.channel.capabilities", "verify_opchannel_capabilities")

    with pytest.raises(ValueError, match="capability|adapter|missing|stale"):
        handshake(required=required, adapter=adapter)


def test_kernel_plan_stores_capability_requirements_not_live_adapter() -> None:
    compile_requirements = _require(
        "tigrbl_kernel.opchannel_capabilities", "compile_capability_requirements"
    )

    plan = compile_requirements(binding="websocket", subevent="message.received")

    assert plan["required"] == ("accept", "recv", "send", "close")
    assert "adapter" not in plan
    assert isinstance(plan["required_mask"], int)

