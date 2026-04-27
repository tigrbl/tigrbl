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


def test_channel_state_initializes_with_identity_and_open_status() -> None:
    create_state = _require("tigrbl_runtime.channel.state", "create_channel_state")

    state = create_state(
        channel_id="ch-1",
        binding="websocket",
        family="message",
        peer={"host": "127.0.0.1", "port": 5000},
    )

    assert state["channel_id"] == "ch-1"
    assert state["binding"] == "websocket"
    assert state["family"] == "message"
    assert state["open"] is True
    assert state["closed"] is False
    assert state["peer"]["host"] == "127.0.0.1"


def test_channel_state_tracks_receive_emit_and_completion_transitions() -> None:
    create_state = _require("tigrbl_runtime.channel.state", "create_channel_state")
    transition = _require("tigrbl_runtime.channel.state", "transition_channel_state")
    state = create_state(channel_id="ch-1", binding="websocket", family="message")

    state = transition(state, subevent="message.received", payload_size=12)
    assert state["current_subevent"] == "message.received"
    assert state["received_count"] == 1
    assert state["last_payload_size"] == 12

    state = transition(state, subevent="message.emit", payload_size=5)
    assert state["emit_count"] == 1
    assert state["completion_state"] == "pending"

    state = transition(state, subevent="message.emit_complete")
    assert state["completion_state"] == "complete"


def test_channel_state_records_close_code_reason_and_final_subevent() -> None:
    create_state = _require("tigrbl_runtime.channel.state", "create_channel_state")
    transition = _require("tigrbl_runtime.channel.state", "transition_channel_state")
    state = create_state(channel_id="ch-1", binding="websocket", family="session")

    state = transition(state, subevent="session.close", close_code=1001, close_reason="going away")

    assert state["open"] is False
    assert state["closed"] is True
    assert state["close_code"] == 1001
    assert state["close_reason"] == "going away"
    assert state["current_subevent"] == "session.close"


def test_channel_error_context_includes_channel_state_metadata() -> None:
    create_state = _require("tigrbl_runtime.channel.state", "create_channel_state")
    build_error = _require("tigrbl_runtime.channel.state", "build_channel_error_ctx")
    state = create_state(channel_id="ch-err", binding="http.sse", family="stream")

    error_ctx = build_error(
        state,
        subevent="stream.chunk.emit",
        phase="POST_EMIT",
        exc=RuntimeError("emit failed"),
    )

    assert error_ctx["channel_id"] == "ch-err"
    assert error_ctx["binding"] == "http.sse"
    assert error_ctx["family"] == "stream"
    assert error_ctx["subevent"] == "stream.chunk.emit"
    assert error_ctx["phase"] == "POST_EMIT"
    assert "emit failed" in error_ctx["message"]


def test_channel_state_rejects_transition_after_close() -> None:
    create_state = _require("tigrbl_runtime.channel.state", "create_channel_state")
    transition = _require("tigrbl_runtime.channel.state", "transition_channel_state")
    state = create_state(channel_id="ch-closed", binding="websocket", family="message")
    state = transition(state, subevent="session.close", close_code=1000)

    with pytest.raises(ValueError, match="channel|closed|state|transition"):
        transition(state, subevent="message.emit")
