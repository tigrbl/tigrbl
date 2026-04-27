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


def test_eventful_protocol_decorators_lower_to_op_ctx_plus_binding_specs() -> None:
    lower = _require("tigrbl_concrete._decorators.eventful", "lower_eventful_protocol_decorator")

    for decorator in ("websocket_ctx", "sse_ctx", "stream_ctx", "webtransport_ctx"):
        lowered = lower(decorator, path="/events", alias="events")
        assert lowered["semantic_root"] == "op_ctx"
        assert lowered["op_spec"]["alias"] == "events"
        assert lowered["binding_specs"]


def test_subevent_ctx_binds_optional_dispatch_handler() -> None:
    lower = _require("tigrbl_concrete._decorators.eventful", "lower_subevent_ctx")

    lowered = lower(
        family="socket",
        subevent="message.received",
        handler_name="on_message",
    )

    assert lowered["kind"] == "subevent_handler"
    assert lowered["family"] == "socket"
    assert lowered["subevent"] == "message.received"
    assert lowered["phase"] == "HANDLER"


@pytest.mark.parametrize(
    "declaration",
    (
        {"decorator": "websocket_ctx", "path": "/socket", "bypass_op_ctx": True},
        {"decorator": "sse_ctx", "path": "/events", "binding": "websocket"},
        {
            "decorator": "subevent_ctx",
            "family": "socket",
            "subevent": "message.received",
            "handler_name": "a",
            "duplicate_handler_name": "b",
        },
    ),
)
def test_eventful_decorator_lowering_rejects_bypass_conflicts_and_ambiguity(
    declaration: dict[str, object],
) -> None:
    validate = _require("tigrbl_concrete._decorators.eventful", "validate_eventful_declaration")

    with pytest.raises(ValueError, match="op_ctx|binding|ambiguous|subevent"):
        validate(declaration)


def test_realtime_verbs_remain_builtin_custom_handlers() -> None:
    lower = _require("tigrbl_concrete._decorators.eventful", "lower_realtime_verb")

    lowered = lower("append_stream")

    assert lowered["kind"] == "builtin_custom_handler"
    assert lowered["semantic_root"] == "op_ctx"
