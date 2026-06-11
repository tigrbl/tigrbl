from __future__ import annotations

import pytest

from tigrbl_core._spec.hook_spec import HookSpec
from tigrbl_kernel.channel_taxonomy import (
    channel_family,
    channel_kind,
    channel_subevents,
    normalize_exchange,
    select_webtransport_hooks,
    webtransport_event_metadata,
)
from tigrbl_kernel.dispatch_taxonomy import derive_runtime_event, resolve_operation
from tigrbl_kernel.loop_modes import build_loop_controller
from tigrbl_kernel.protocol_anchors import canonical_protocol_anchor_order


def _noop(**kwargs):
    return kwargs


def test_kernel_owns_protocol_anchor_policy() -> None:
    ok_order = canonical_protocol_anchor_order("http.stream", "stream.chunk")
    err_order = canonical_protocol_anchor_order(
        "http.rest",
        "request.received",
        edge="err",
    )

    assert ok_order.index("dispatch.subevent.derive") < ok_order.index("transport.emit")
    assert "err.ctx.build" not in ok_order
    assert err_order[-3:] == (
        "err.ctx.build",
        "err.classify",
        "err.transport.shape",
    )


def test_kernel_owns_dispatch_taxonomy_and_operation_resolution() -> None:
    event = derive_runtime_event(
        {"binding": "websocket", "method": "send", "path": "/socket"}
    )
    operation = resolve_operation(event)

    assert event["exchange"] == "bidirectional_stream"
    assert event["family"] == "socket"
    assert event["subevent"] == "message.received"
    assert operation["op_code"] == "websocket:message.received:send"


@pytest.mark.parametrize(
    "event",
    (
        {"binding": "unknown.transport"},
        {"binding": "http.rest", "subevent": "receive"},
    ),
)
def test_kernel_dispatch_taxonomy_fails_closed(event: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        derive_runtime_event(event)


def test_kernel_owns_loop_controller_metadata() -> None:
    controller = build_loop_controller(
        mode="dispatch",
        binding="websocket",
        subevent_handlers=("message.received",),
    )

    assert controller == {
        "mode": "dispatch",
        "binding": "websocket",
        "subevent_handlers": ("message.received",),
        "dispatches_subevents": True,
        "owner_controls_receive": False,
    }


def test_kernel_owns_channel_kind_family_and_subevents() -> None:
    assert normalize_exchange("bidirectional") == "bidirectional_stream"
    assert channel_kind("websocket", "bidirectional") == "websocket"
    assert channel_family("websocket", "bidirectional") == "socket"
    assert channel_subevents("webtransport", "request_response") == (
        "connect",
        "receive",
        "emit",
        "complete",
        "disconnect",
    )


def test_kernel_owns_webtransport_event_metadata() -> None:
    metadata = webtransport_event_metadata(
        direction="receive",
        message={
            "type": "webtransport.datagram.receive",
            "session_id": "s1",
            "datagram_id": "d1",
        },
    )

    assert metadata["binding"] == "webtransport"
    assert metadata["family"] == "datagram"
    assert metadata["lane"] == "datagram"
    assert metadata["subevent"] == "datagram.received"


def test_kernel_owns_webtransport_hook_selection_policy() -> None:
    receive_hook = HookSpec(
        phase="PRE_HANDLER",
        fn=_noop,
        bindings=("webtransport",),
        family=("stream",),
    )
    send_hook = HookSpec(
        phase="POST_RESPONSE",
        fn=_noop,
        bindings=("webtransport",),
        family=("stream",),
    )
    metadata = {
        "binding": "webtransport",
        "family": "stream",
        "lane": "bidi_stream",
        "subevent": "stream.chunk.received",
    }

    assert select_webtransport_hooks(
        (receive_hook, send_hook),
        direction="receive",
        metadata=metadata,
    ) == (receive_hook,)
    assert select_webtransport_hooks(
        (receive_hook, send_hook),
        direction="send",
        metadata=metadata,
    ) == (send_hook,)
