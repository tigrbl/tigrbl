from __future__ import annotations

import pytest

from tigrbl_atoms.protocol_runtime import (
    run_http_rest_chain,
    run_transport_emit,
    run_websocket_chain,
)
from tigrbl_atoms.atoms.framing.app_frame import decode_app_frame, encode_app_frame
from tigrbl_atoms.atoms.framing.codec import decode_frame, encode_frame
from tigrbl_atoms.atoms.transport.asgi_channel import (
    complete_channel_state,
    message_payload,
    payload_size,
    session_payload_events,
    webtransport_payload_event,
    webtransport_structured_payload_events,
)
from tigrbl_atoms.atoms.transport.completion_fence import emit_with_fence
from tigrbl_atoms.runtime_callbacks import register_callback, run_callback_fence
from tigrbl_atoms.runtime_channel import create_channel_state, transition_channel_state
from tigrbl_atoms.runtime_loop_regions import execute_loop_region
from tigrbl_atoms.runtime_transactions import run_subevent_tx_unit


@pytest.mark.asyncio
async def test_atom_owned_protocol_steps_execute_without_runtime_policy_synthesis() -> (
    None
):
    sent: list[dict[str, object]] = []

    rest = await run_http_rest_chain(
        {
            "payload": {"item_id": 7},
            "handler": lambda payload: {"ok": True, "payload": payload},
            "send": sent.append,
        }
    )
    websocket = await run_websocket_chain(
        {
            "scope": {"scheme": "ws"},
            "messages": (
                {"type": "websocket.receive", "text": "hello"},
                {"type": "websocket.disconnect", "code": 1001, "reason": "done"},
            ),
        }
    )

    assert rest["completion_fence"] == "POST_EMIT"
    assert rest["trace"][-1] == "transport.emit_complete"
    assert sent[0]["type"] == "http.response.start"
    assert sent[1]["type"] == "http.response.body"
    assert websocket["received_text"] == ["hello"]
    assert websocket["close_code"] == 1001


def test_atom_owned_callback_channel_and_transaction_steps_are_concrete_behaviors() -> (
    None
):
    descriptor = register_callback(name="audit", kind="hook", phase="POST_HANDLER")
    trace: list[str] = []
    callback_result = run_callback_fence(
        descriptor,
        callback=lambda ctx: {"seen": ctx["op_id"]},
        ctx={"op_id": "Inventory.read"},
        trace=trace.append,
    )

    state = create_channel_state(
        channel_id="ch-1", binding="websocket", family="message"
    )
    state = transition_channel_state(state, subevent="message.received", payload_size=4)
    state = transition_channel_state(state, subevent="message.emit", payload_size=2)
    tx_trace: list[str] = []
    tx_result = run_subevent_tx_unit(
        {"subevent": "message.received", "tx_unit": "handler"},
        handler=lambda ctx: {"subevent": ctx["subevent"]},
        trace=tx_trace.append,
    )
    emit_result = run_transport_emit(
        {"subevent": "message.emit", "payload": b"ok"},
        send=lambda event: "ack",
    )

    assert callback_result == {"seen": "Inventory.read"}
    assert trace == ["callback_fence_enter:audit", "callback_fence_exit:audit"]
    assert state["received_count"] == 1
    assert state["emit_count"] == 1
    assert state["completion_state"] == "pending"
    assert tx_trace == [
        "tx.begin:message.received",
        "handler.call",
        "tx.commit:message.received",
    ]
    assert tx_result == {"subevent": "message.received"}
    assert emit_result["completed"] is True


def test_atom_owned_asgi_channel_payload_steps_are_concrete_behaviors() -> None:
    session_events = session_payload_events(
        {"ok": True},
        accept_type="websocket.accept",
        send_type="websocket.send",
        close_type="websocket.close",
    )
    stream_event = webtransport_payload_event(
        base={
            "type": "webtransport.stream.receive",
            "session_id": "s1",
            "stream_id": 4,
            "stream_direction": "bidi",
            "framing": "bytes",
        },
        payload={"ok": True},
    )
    datagram_events = webtransport_structured_payload_events(
        session_id="s1",
        inbound={
            "type": "webtransport.datagram.receive",
            "session_id": "s1",
            "datagram_id": "d1",
            "framing": "bytes",
        },
        payload={"datagrams": [{"payload": "pong"}]},
    )
    state: dict[str, object] = {}

    assert message_payload({"text": "hello"}) == b"hello"
    assert payload_size({"data": b"abc"}) == 3
    assert session_events == (
        {"type": "websocket.accept"},
        {"type": "websocket.send", "text": '{"ok":true}'},
        {"type": "websocket.close", "code": 1000},
    )
    assert stream_event == {
        "type": "webtransport.stream.send",
        "session_id": "s1",
        "stream_id": 4,
        "stream_direction": "bidi",
        "framing": "bytes",
        "data": b'{"ok":true}',
        "more": False,
    }
    assert datagram_events == [
        {
            "type": "webtransport.datagram.send",
            "session_id": "s1",
            "datagram_id": "d1",
            "data": b"pong",
            "framing": "bytes",
        }
    ]
    assert complete_channel_state(state) == {
        "completed": True,
        "completion_fence": "POST_EMIT",
    }


@pytest.mark.asyncio
async def test_atom_owned_framing_completion_and_loop_steps_execute() -> None:
    frame = encode_app_frame(kind=3, payload=b"hello")
    json_body = encode_frame("json", {"ok": True})
    sent: list[dict[str, object]] = []

    async def _send(event: dict[str, object]) -> str:
        sent.append(event)
        return "ack"

    completion = await emit_with_fence(
        {"subevent": "message.emit", "payload": b"ok"},
        send=_send,
    )
    loop_result = await execute_loop_region(
        {"producer": ("a", "stop", "b"), "break_on": "stop"}
    )

    assert decode_app_frame(frame)["payload"] == b"hello"
    assert decode_frame("json", json_body) == {"ok": True}
    assert completion["completed"] is True
    assert completion["completion_fence"] == "POST_EMIT"
    assert sent == [{"subevent": "message.emit", "payload": b"ok"}]
    assert loop_result == {"items": ["a"], "exit_reason": "break", "closed": True}
