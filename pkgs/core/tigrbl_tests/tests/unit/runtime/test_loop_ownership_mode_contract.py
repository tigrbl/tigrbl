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


def test_loop_mode_defaults_to_dispatch_when_subevent_handlers_exist() -> None:
    select_mode = _require("tigrbl_kernel.loop_modes", "select_loop_mode")

    mode = select_mode(
        binding="websocket",
        subevent_handlers=("message.received",),
        explicit_mode=None,
    )

    assert mode == "dispatch"


def test_loop_mode_defaults_to_owner_without_subevent_handlers() -> None:
    select_mode = _require("tigrbl_kernel.loop_modes", "select_loop_mode")

    mode = select_mode(binding="websocket", subevent_handlers=(), explicit_mode=None)

    assert mode == "owner"


@pytest.mark.parametrize(
    "config",
    (
        {"binding": "websocket", "subevent_handlers": ("message.received",), "explicit_mode": "owner"},
        {"binding": "sse", "subevent_handlers": (), "explicit_mode": "dispatch"},
    ),
)
def test_loop_mode_rejects_ambiguous_or_unserviceable_policy(config: dict[str, object]) -> None:
    select_mode = _require("tigrbl_kernel.loop_modes", "select_loop_mode")

    with pytest.raises(ValueError, match="loop|mode|owner|dispatch|handler|capability"):
        select_mode(**config)

