from __future__ import annotations

from httpx import ASGITransport, Client

from tigrbl_concrete._decorators.eventful import (
    lower_eventful_protocol_decorator,
    lower_on_mapping,
)
from tigrbl_concrete.system.docs.surface import binding_surface
from tigrbl_core._spec.binding_spec import HttpStreamBindingSpec, WsBindingSpec
from tigrbl_kernel.eventkey import build_dispatch_table, pack_event_key
from tigrbl_kernel.eventkey_hooks import compile_hook_buckets
from tigrbl_kernel.lifecycle_matrix import select_subevents
from tigrbl_kernel.subevent_handlers import compile_subevent_handlers
from tigrbl_kernel.transaction_units import compile_subevent_tx_units
from tigrbl_runtime.channel.state import create_channel_state, transition_channel_state
from tigrbl_runtime.protocol.subevent_handlers import dispatch_subevent
from tigrbl_runtime.transactions import run_subevent_tx_unit
from tigrbl_tests.tests.unit.test_declared_surface_docs import _build_app


def test_eventkey_subevent_dispatch_and_hook_buckets_are_integer_keyed() -> None:
    event_key = pack_event_key(op=1, binding=2, exchange=1, family=3, subevent=4, framing=1)
    dispatch_table = build_dispatch_table({event_key: "chain:message"})
    handler_table = compile_subevent_handlers(
        [{"handler_id": "on-message", "family": "socket", "subevent": "message.received"}],
        key_mode="eventkey",
    )
    hook_buckets = compile_hook_buckets(
        hooks=[{"hook_id": "audit", "phase": "HANDLER", "family": "socket", "subevent": "*"}],
        event_catalog=[{"family": "socket", "subevent": "message.received"}],
    )
    handler_key = next(iter(handler_table))

    assert dispatch_table[event_key] == "chain:message"
    assert isinstance(handler_key, int)
    assert dispatch_subevent({"event_key": handler_key}, handler_table) == "on-message"
    assert isinstance(hook_buckets["message.received"]["event_key"], int)


def test_subevent_transaction_units_and_primary_selection_are_fail_closed() -> None:
    units = compile_subevent_tx_units(
        [
            {"family": "message", "subevent": "message.received", "phase": "HANDLER", "tx_unit": "handler"},
            {"family": "message", "subevent": "message.emit_complete", "phase": "POST_EMIT", "tx_unit": "none"},
        ]
    )
    trace: list[str] = []
    result = run_subevent_tx_unit(
        {"family": "message", "subevent": "message.received", "tx_unit": units[("message", "message.received", "HANDLER")]},
        handler=lambda _ctx: {"ok": True},
        trace=trace.append,
    )
    selected = select_subevents(
        {
            "family": "socket",
            "candidates": ("message.decoded", "message.received"),
            "handler_target": "message.received",
        }
    )

    assert trace == ["tx.begin:message.received", "handler.call", "tx.commit:message.received"]
    assert result["ok"] is True
    assert selected == {
        "family": "socket",
        "primary": "message.received",
        "secondary": ("message.decoded",),
    }


def test_eventful_channel_state_and_decorator_lowering_emit_metadata() -> None:
    state = create_channel_state(channel_id="ch-1", binding="websocket", family="message")
    state = transition_channel_state(state, subevent="message.received", payload_size=12)
    state = transition_channel_state(state, subevent="message.emit", payload_size=5)
    ws = lower_eventful_protocol_decorator("websocket_ctx", path="/socket", alias="socket")
    on_handlers = lower_on_mapping(
        family="socket",
        on={"message.received": "handle_message", "session.close": "handle_close"},
    )

    assert state["current_subevent"] == "message.emit"
    assert state["received_count"] == 1
    assert state["emit_count"] == 1
    assert ws["semantic_root"] == "op_ctx"
    assert ws["binding_specs"][0]["proto"] == "ws"
    assert on_handlers[0]["handler_name"] == "handle_message"


def test_declared_surface_binding_metadata_and_cross_projection_parity() -> None:
    stream = binding_surface(HttpStreamBindingSpec(proto="http.stream", path="/widgets/events"))
    socket = binding_surface(WsBindingSpec(proto="ws", path="/socket", framing="jsonrpc"))
    app, model = _build_app()

    with Client(transport=ASGITransport(app=app), base_url="http://test") as client:
        openapi = client.get("/openapi.json").json()
        openrpc = client.get("/openrpc.json").json()

    api_surface = openapi["paths"]["/widget/events"]["get"]["x-tigrbl-surface"]
    rpc_methods = {method["name"]: method for method in openrpc["methods"]}
    rpc_surface = rpc_methods[f"{model.__name__}.socket_rpc"]["x-tigrbl-surface"]

    assert stream["proto"] == "http.stream"
    assert stream["family"] == "stream"
    assert socket["proto"] == "ws"
    assert socket["family"] == "socket"
    assert api_surface["binding"]["proto"] == "http.stream"
    assert api_surface["binding"]["family"] == "stream"
    assert "txScope" not in openapi["paths"]["/widget"]["post"]["x-tigrbl-surface"]
    assert any(binding["proto"] == "ws" and binding["family"] == "socket" for binding in rpc_surface["bindings"])
