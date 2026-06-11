from __future__ import annotations

from tigrbl_kernel.loop_modes import select_loop_mode
from tigrbl_kernel.protocol_completion import compile_completion_fence
from tigrbl_kernel.protocol_legality_matrix import generate_legality_matrix
from tigrbl_kernel.segment_fusion import fuse_segments
from tigrbl_kernel.protocol_anchors import canonical_protocol_anchor_order
from tigrbl_kernel.dispatch_taxonomy import derive_runtime_event
from tigrbl_kernel.loop_modes import build_loop_controller


def test_two_axis_lifecycle_matrix_contract() -> None:
    matrix = generate_legality_matrix()

    assert {"http.rest", "websocket", "webtransport.datagram"} <= {
        row["binding"] for row in matrix
    }
    assert all("INGRESS_ROUTE" not in row["phase"] for row in matrix)


def test_eventkey_bit_coded_dispatch_contract() -> None:
    event = derive_runtime_event({"binding": "websocket", "path": "/socket"})

    assert event["exchange"] == "bidirectional_stream"
    assert event["family"] == "socket"


def test_opchannel_capability_handshake_contract() -> None:
    assert (
        select_loop_mode(
            binding="websocket",
            subevent_handlers=("message.received",),
            explicit_mode="dispatch",
            capabilities=("accept", "recv", "send", "close"),
        )
        == "dispatch"
    )


def test_subevent_handler_dispatch_contract() -> None:
    controller = build_loop_controller(
        mode="dispatch",
        binding="websocket",
        subevent_handlers=("message.received",),
    )

    assert controller["dispatches_subevents"] is True


def test_owner_dispatch_loop_modes_contract() -> None:
    assert select_loop_mode(binding="websocket", subevent_handlers=()) == "owner"
    assert select_loop_mode(binding="websocket", subevent_handlers=("message.received",)) == "dispatch"


def test_completion_fence_emit_complete_contract() -> None:
    fence = compile_completion_fence({"binding": "http.stream", "transport": "stream"})

    assert fence["completion_fence"] == "POST_EMIT"
    assert fence["runtime_owned"] is True


def test_segment_fusion_barrier_policy_contract() -> None:
    fused = fuse_segments(
        [
            {"segment_id": "ingress", "class": "pure_ingress", "atoms": ("ingress.parse",)},
            {"segment_id": "dispatch", "class": "pure_dispatch", "atoms": ("dispatch.select",)},
            {"segment_id": "emit", "class": "transport.emit", "atoms": ("transport.emit",)},
        ]
    )

    assert [segment["segment_id"] for segment in fused] == ["ingress+dispatch", "emit"]


def test_eventful_protocol_decorator_surface_contract() -> None:
    event = derive_runtime_event({"binding": "http.sse", "path": "/events"})

    assert event["family"] == "event_stream"
    assert event["subevent"] == "message.emit"


def test_primary_secondary_subevent_selection_contract() -> None:
    order = canonical_protocol_anchor_order("http.stream", "stream.chunk")

    assert order.index("dispatch.subevent.derive") < order.index("transport.emit")


def test_eventkey_hook_bucket_compilation_contract() -> None:
    matrix = generate_legality_matrix()

    assert any(
        row["binding"] == "websocket" and row["subevent"] == "session.open"
        for row in matrix
    )
