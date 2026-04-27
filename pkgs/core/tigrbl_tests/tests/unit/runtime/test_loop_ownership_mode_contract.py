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


@pytest.mark.parametrize(
    ("binding", "handlers"),
    (
        ("websocket", ("message.received",)),
        ("webtransport", ("datagram.received",)),
        ("stream", ("chunk.received",)),
    ),
)
def test_loop_mode_defaults_to_dispatch_for_handler_driven_bindings(
    binding: str,
    handlers: tuple[str, ...],
) -> None:
    select_mode = _require("tigrbl_kernel.loop_modes", "select_loop_mode")

    mode = select_mode(binding=binding, subevent_handlers=handlers, explicit_mode=None)

    assert mode == "dispatch"


def test_loop_mode_defaults_to_owner_without_subevent_handlers() -> None:
    select_mode = _require("tigrbl_kernel.loop_modes", "select_loop_mode")

    mode = select_mode(binding="websocket", subevent_handlers=(), explicit_mode=None)

    assert mode == "owner"


@pytest.mark.parametrize("binding", ("websocket", "sse", "stream"))
def test_loop_mode_defaults_to_owner_when_no_dispatch_handlers_are_declared(
    binding: str,
) -> None:
    select_mode = _require("tigrbl_kernel.loop_modes", "select_loop_mode")

    mode = select_mode(binding=binding, subevent_handlers=(), explicit_mode=None)

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


def test_loop_mode_accepts_explicit_dispatch_when_capabilities_cover_receive_loop() -> None:
    select_mode = _require("tigrbl_kernel.loop_modes", "select_loop_mode")

    mode = select_mode(
        binding="websocket",
        subevent_handlers=("message.received",),
        explicit_mode="dispatch",
        capabilities=("accept", "recv", "send", "close"),
    )

    assert mode == "dispatch"


def test_loop_mode_accepts_explicit_owner_when_no_subevent_handlers_exist() -> None:
    select_mode = _require("tigrbl_kernel.loop_modes", "select_loop_mode")

    mode = select_mode(
        binding="websocket",
        subevent_handlers=(),
        explicit_mode="owner",
        capabilities=("accept", "recv", "send", "close"),
    )

    assert mode == "owner"


def test_runtime_loop_trace_marks_owner_control_without_dispatch_selection() -> None:
    build_loop = _require("tigrbl_runtime.protocol.loop_modes", "build_loop_controller")

    controller = build_loop(mode="owner", binding="websocket")

    assert controller["mode"] == "owner"
    assert controller["dispatches_subevents"] is False
    assert controller["owner_controls_receive"] is True


def test_runtime_loop_trace_marks_dispatch_control_with_subevent_selection() -> None:
    build_loop = _require("tigrbl_runtime.protocol.loop_modes", "build_loop_controller")

    controller = build_loop(
        mode="dispatch",
        binding="websocket",
        subevent_handlers=("message.received",),
    )

    assert controller["mode"] == "dispatch"
    assert controller["dispatches_subevents"] is True
    assert controller["owner_controls_receive"] is False
