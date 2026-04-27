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


def test_protocol_anchor_order_contains_dispatch_framing_transport_and_completion() -> None:
    anchor_order = _require("tigrbl_runtime.protocol.anchors", "canonical_protocol_anchor_order")

    order = tuple(anchor_order("http.stream", "stream.chunk"))

    assert order.index("dispatch.exchange.select") < order.index("dispatch.family.derive")
    assert order.index("dispatch.subevent.derive") < order.index("framing.encode")
    assert order.index("framing.encode") < order.index("transport.emit")
    assert order.index("transport.emit") < order.index("transport.emit_complete")


def test_protocol_error_anchors_are_ordered_on_governed_error_edges_only() -> None:
    anchor_order = _require("tigrbl_runtime.protocol.anchors", "canonical_protocol_anchor_order")

    ok_order = tuple(anchor_order("http.rest", "request.received", edge="ok"))
    err_order = tuple(anchor_order("http.rest", "request.received", edge="err"))

    assert "err.ctx.build" not in ok_order
    assert "err.classify" not in ok_order
    assert err_order.index("err.ctx.build") < err_order.index("err.classify")
    assert err_order.index("err.classify") < err_order.index("err.transport.shape")


def test_python_and_rust_protocol_anchor_traces_match() -> None:
    python_trace = _require("tigrbl_runtime.protocol.anchors", "python_protocol_anchor_trace")
    rust_trace = _require("tigrbl_runtime.protocol.anchors", "rust_protocol_anchor_trace")

    case = {"binding": "websocket", "subevent": "message.received", "messages": ["ping"]}

    assert tuple(python_trace(case)) == tuple(rust_trace(case))

