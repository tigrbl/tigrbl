from __future__ import annotations

import importlib
from pathlib import Path


_SHIM_EXPORTS = (
    (
        "tigrbl_runtime.protocol.http_unary",
        "run_http_rest_chain",
        "tigrbl_atoms.protocol_runtime",
    ),
    (
        "tigrbl_runtime.protocol.http_unary",
        "run_http_jsonrpc_chain",
        "tigrbl_atoms.protocol_runtime",
    ),
    (
        "tigrbl_runtime.protocol.http_stream",
        "run_http_stream_chain",
        "tigrbl_atoms.protocol_runtime",
    ),
    ("tigrbl_runtime.protocol.sse", "run_sse_chain", "tigrbl_atoms.protocol_runtime"),
    (
        "tigrbl_runtime.protocol.websocket",
        "run_websocket_chain",
        "tigrbl_atoms.protocol_runtime",
    ),
    (
        "tigrbl_runtime.protocol.lifespan_chain",
        "run_lifespan_chain",
        "tigrbl_atoms.protocol_runtime",
    ),
    (
        "tigrbl_runtime.protocol.static_files",
        "run_static_file_chain",
        "tigrbl_atoms.protocol_runtime",
    ),
    (
        "tigrbl_runtime.protocol.webtransport",
        "validate_webtransport_scope",
        "tigrbl_atoms.protocol_runtime",
    ),
    (
        "tigrbl_runtime.protocol.transport_atoms",
        "run_transport_emit",
        "tigrbl_atoms.protocol_runtime",
    ),
    (
        "tigrbl_runtime.protocol.subevent_handlers",
        "dispatch_subevent",
        "tigrbl_atoms.protocol_runtime",
    ),
    (
        "tigrbl_runtime.protocol._iterators",
        "iter_items",
        "tigrbl_atoms.protocol_runtime",
    ),
    (
        "tigrbl_runtime.protocol._iterators",
        "aclose_if_supported",
        "tigrbl_atoms.protocol_runtime",
    ),
    ("tigrbl_runtime.callbacks", "register_callback", "tigrbl_atoms.runtime_callbacks"),
    (
        "tigrbl_runtime.callbacks",
        "run_callback_fence",
        "tigrbl_atoms.runtime_callbacks",
    ),
    (
        "tigrbl_runtime.channel.state",
        "create_channel_state",
        "tigrbl_atoms.runtime_channel",
    ),
    (
        "tigrbl_runtime.channel.state",
        "transition_channel_state",
        "tigrbl_atoms.runtime_channel",
    ),
    (
        "tigrbl_runtime.transactions",
        "run_subevent_tx_unit",
        "tigrbl_atoms.runtime_transactions",
    ),
    (
        "tigrbl_runtime.protocol.app_frame_codec",
        "encode_app_frame",
        "tigrbl_atoms.atoms.framing.app_frame",
    ),
    (
        "tigrbl_runtime.protocol.app_frame_codec",
        "decode_app_frame",
        "tigrbl_atoms.atoms.framing.app_frame",
    ),
    (
        "tigrbl_runtime.protocol.app_frame_codec",
        "decode_app_frames",
        "tigrbl_atoms.atoms.framing.app_frame",
    ),
    (
        "tigrbl_runtime.protocol.app_frame_codec",
        "FrameStreamDecoder",
        "tigrbl_atoms.atoms.framing.app_frame",
    ),
    (
        "tigrbl_runtime.protocol.framing_atoms",
        "decode_frame",
        "tigrbl_atoms.atoms.framing.codec",
    ),
    (
        "tigrbl_runtime.protocol.framing_atoms",
        "encode_frame",
        "tigrbl_atoms.atoms.framing.codec",
    ),
    (
        "tigrbl_runtime.protocol.completion_fence",
        "emit_with_fence",
        "tigrbl_atoms.atoms.transport.completion_fence",
    ),
    (
        "tigrbl_runtime.executors.loop_regions",
        "execute_loop_region",
        "tigrbl_atoms.runtime_loop_regions",
    ),
    (
        "tigrbl_runtime.channel.asgi",
        "_message_payload",
        "tigrbl_atoms.atoms.transport.asgi_channel",
        "message_payload",
    ),
    (
        "tigrbl_runtime.channel.asgi",
        "_webtransport_payload_size",
        "tigrbl_atoms.atoms.transport.asgi_channel",
        "payload_size",
    ),
    (
        "tigrbl_runtime.channel.asgi",
        "_webtransport_payload_event",
        "tigrbl_atoms.atoms.transport.asgi_channel",
        "webtransport_payload_event",
    ),
    (
        "tigrbl_runtime.channel.asgi",
        "_webtransport_structured_payload_events",
        "tigrbl_atoms.atoms.transport.asgi_channel",
        "webtransport_structured_payload_events",
    ),
    (
        "tigrbl_runtime.protocol.anchors",
        "canonical_protocol_anchor_order",
        "tigrbl_kernel.protocol_anchors",
    ),
    (
        "tigrbl_runtime.protocol.anchors",
        "python_protocol_anchor_trace",
        "tigrbl_kernel.protocol_anchors",
    ),
    (
        "tigrbl_runtime.protocol.anchors",
        "rust_protocol_anchor_trace",
        "tigrbl_kernel.protocol_anchors",
    ),
    (
        "tigrbl_runtime.protocol.dispatch_atoms",
        "derive_runtime_event",
        "tigrbl_kernel.dispatch_taxonomy",
    ),
    (
        "tigrbl_runtime.protocol.dispatch_atoms",
        "resolve_operation",
        "tigrbl_kernel.dispatch_taxonomy",
    ),
    (
        "tigrbl_runtime.protocol.loop_modes",
        "build_loop_controller",
        "tigrbl_kernel.loop_modes",
    ),
    (
        "tigrbl_runtime.runtime.events",
        "PHASES",
        "tigrbl_kernel.events",
    ),
    (
        "tigrbl_runtime.runtime.events",
        "order_events",
        "tigrbl_kernel.events",
    ),
    (
        "tigrbl_runtime.runtime.events",
        "prune_events_for_persist",
        "tigrbl_kernel.events",
    ),
    (
        "tigrbl_runtime.channel.asgi",
        "normalize_exchange",
        "tigrbl_kernel.channel_taxonomy",
    ),
    (
        "tigrbl_runtime.channel.asgi",
        "_channel_family",
        "tigrbl_kernel.channel_taxonomy",
        "channel_family",
    ),
    (
        "tigrbl_runtime.channel.asgi",
        "_channel_kind",
        "tigrbl_kernel.channel_taxonomy",
        "channel_kind",
    ),
    (
        "tigrbl_runtime.channel.asgi",
        "_subevents",
        "tigrbl_kernel.channel_taxonomy",
        "channel_subevents",
    ),
    (
        "tigrbl_runtime.channel.asgi",
        "_webtransport_event_metadata",
        "tigrbl_kernel.channel_taxonomy",
        "webtransport_event_metadata",
    ),
)


def test_runtime_surfaces_delegate_to_authoritative_implementations() -> None:
    for item in _SHIM_EXPORTS:
        runtime_module_name, attr_name, target_module_name, *target_attr = item
        runtime_module = importlib.import_module(runtime_module_name)
        target_module = importlib.import_module(target_module_name)
        assert getattr(runtime_module, attr_name) is getattr(
            target_module, target_attr[0] if target_attr else attr_name
        )


def test_packed_executor_source_avoids_runtime_shadow_compiler_helpers() -> None:
    packed_module = importlib.import_module("tigrbl_runtime.executors.packed")
    source = Path(packed_module.__file__).read_text(encoding="utf-8")

    forbidden = (
        "tigrbl_runtime.protocol.http_unary",
        "tigrbl_runtime.protocol.http_stream",
        "tigrbl_runtime.protocol.sse",
        "tigrbl_runtime.protocol.websocket",
        "tigrbl_runtime.protocol.lifespan_chain",
        "tigrbl_runtime.protocol.static_files",
        "tigrbl_runtime.protocol.transport_atoms",
        "tigrbl_runtime.protocol.subevent_handlers",
        "tigrbl_runtime.callbacks",
        "tigrbl_runtime.transactions",
    )

    assert all(name not in source for name in forbidden)


def test_packed_executor_private_helpers_delegate_to_owner_packages() -> None:
    from tigrbl_atoms.atoms.transport.websocket_unary import DirectWebSocketUnary
    from tigrbl_kernel.packed_access import http_method_id, stable_name_hash64
    from tigrbl_runtime.executors import packed
    from tigrbl_runtime.executors.packed import PackedPlanExecutor

    assert packed._DirectWebSocketUnary is DirectWebSocketUnary
    assert PackedPlanExecutor._http_method_id("POST") == http_method_id("POST")
    assert PackedPlanExecutor._stable_name_hash64("/items") == stable_name_hash64(
        "/items"
    )
