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


def test_subevent_handler_dispatch_selects_exact_eventkey_handler() -> None:
    compile_handlers = _require("tigrbl_kernel.subevent_handlers", "compile_subevent_handlers")
    dispatch = _require("tigrbl_runtime.protocol.subevent_handlers", "dispatch_subevent")

    table = compile_handlers(
        [
            {"handler_id": "on-message", "family": "socket", "subevent": "message.received"},
            {"handler_id": "on-close", "family": "socket", "subevent": "session.close"},
        ]
    )

    assert dispatch({"family": "socket", "subevent": "message.received"}, table) == "on-message"
    assert dispatch({"family": "socket", "subevent": "session.close"}, table) == "on-close"


def test_ordered_multi_handler_dispatch_preserves_declared_order() -> None:
    compile_handlers = _require("tigrbl_kernel.subevent_handlers", "compile_subevent_handlers")

    table = compile_handlers(
        [
            {"handler_id": "audit", "family": "event_stream", "subevent": "message.emit", "order": 10},
            {"handler_id": "notify", "family": "event_stream", "subevent": "message.emit", "order": 20},
        ],
        allow_multi=True,
    )

    assert table[("event_stream", "message.emit")]["handler_ids"] == ("audit", "notify")


def test_ambiguous_subevent_handlers_fail_compilation() -> None:
    compile_handlers = _require("tigrbl_kernel.subevent_handlers", "compile_subevent_handlers")

    with pytest.raises(ValueError, match="ambiguous|handler|order|EventKey"):
        compile_handlers(
            [
                {"handler_id": "a", "family": "socket", "subevent": "message.received"},
                {"handler_id": "b", "family": "socket", "subevent": "message.received"},
            ]
        )


def test_phase_bound_hook_cannot_be_used_as_subevent_handler() -> None:
    compile_handlers = _require("tigrbl_kernel.subevent_handlers", "compile_subevent_handlers")

    with pytest.raises(ValueError, match="hook|subevent_ctx|handler"):
        compile_handlers(
            [
                {
                    "handler_id": "bad-hook",
                    "kind": "hook",
                    "phase": "HANDLER",
                    "family": "socket",
                    "subevent": "message.received",
                }
            ]
        )

