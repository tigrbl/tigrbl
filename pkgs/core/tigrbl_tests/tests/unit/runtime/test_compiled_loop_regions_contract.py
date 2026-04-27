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


def test_websocket_receive_loop_compiles_continue_close_and_error_edges() -> None:
    compile_loop = _require("tigrbl_kernel.loop_regions", "compile_loop_region")

    region = compile_loop(
        {
            "loop_id": "ws.receive",
            "binding": "websocket",
            "role": "message",
            "producer_type": "receive",
            "break_conditions": ("websocket.disconnect",),
            "subevent": "message.received",
        }
    )

    assert region["loop_id"] == "ws.receive"
    assert region["continue_target"]
    assert region["exit_target"] == "transport.close"
    assert region["err_target"] in {"ON_HANDLER_ERROR", "ON_ERROR", "transport.close"}


def test_sse_and_http_stream_loops_compile_completion_fences() -> None:
    compile_loop = _require("tigrbl_kernel.loop_regions", "compile_loop_region")

    sse = compile_loop(
        {
            "loop_id": "sse.stream",
            "binding": "http.sse",
            "role": "stream",
            "producer_type": "async_iterator",
            "break_conditions": ("producer.exhausted", "disconnect"),
        }
    )
    stream = compile_loop(
        {
            "loop_id": "http.stream",
            "binding": "http.stream",
            "role": "stream",
            "producer_type": "iterator",
            "break_conditions": ("producer.exhausted", "disconnect"),
        }
    )

    assert sse["completion_fence"] == "POST_EMIT"
    assert stream["completion_fence"] == "POST_EMIT"
    assert sse["ok_child"]["kind"] == "ok"
    assert stream["err_child"]["kind"] == "err"


@pytest.mark.parametrize(
    "bad_region",
    (
        {"loop_id": "bad.unbounded", "binding": "websocket", "role": "message"},
        {
            "loop_id": "bad.tx",
            "binding": "http.sse",
            "role": "stream",
            "producer_type": "async_iterator",
            "break_conditions": ("disconnect",),
            "transaction_unit": "per_chunk",
        },
    ),
)
def test_compiled_loop_regions_fail_closed_for_missing_break_or_illegal_tx(
    bad_region: dict[str, object]
) -> None:
    compile_loop = _require("tigrbl_kernel.loop_regions", "compile_loop_region")

    with pytest.raises(ValueError, match="loop|break|transaction|eligible|err"):
        compile_loop(bad_region)


def test_loop_local_error_compiles_errorctx_metadata() -> None:
    compile_loop = _require("tigrbl_kernel.loop_regions", "compile_loop_region")

    region = compile_loop(
        {
            "loop_id": "stream.outbound",
            "binding": "http.stream",
            "role": "stream",
            "producer_type": "async_iterator",
            "break_conditions": ("producer.exhausted", "disconnect"),
            "subevent": "stream.chunk",
        }
    )

    assert region["error_ctx"]["binding"] == "http.stream"
    assert region["error_ctx"]["subevent"] == "stream.chunk"
    assert region["error_ctx"]["rollback_required"] is False


def test_datagram_loop_region_compiles_single_packet_exit_policy() -> None:
    compile_loop = _require("tigrbl_kernel.loop_regions", "compile_loop_region")

    region = compile_loop(
        {
            "loop_id": "udp.datagram.receive",
            "binding": "udp.datagram",
            "role": "datagram",
            "producer_type": "receive_once",
            "break_conditions": ("packet.received", "transport.close"),
            "subevent": "datagram.received",
        }
    )

    assert region["loop_id"] == "udp.datagram.receive"
    assert region["role"] == "datagram"
    assert region["exit_target"] in {"transport.close", "POST_EMIT"}
    assert region["error_ctx"]["subevent"] == "datagram.received"


def test_message_loop_region_keeps_continue_and_close_targets_distinct() -> None:
    compile_loop = _require("tigrbl_kernel.loop_regions", "compile_loop_region")

    region = compile_loop(
        {
            "loop_id": "message.consume",
            "binding": "internal.message",
            "role": "message",
            "producer_type": "subscription",
            "break_conditions": ("message.ack", "consumer.cancelled"),
            "subevent": "message.received",
        }
    )

    assert region["continue_target"] != region["exit_target"]
    assert region["ok_child"]["target"] == region["continue_target"]
    assert region["err_child"]["target"] == region["err_target"]


def test_loop_region_declares_transaction_boundary_eligibility() -> None:
    compile_loop = _require("tigrbl_kernel.loop_regions", "compile_loop_region")

    region = compile_loop(
        {
            "loop_id": "stream.tx",
            "binding": "http.stream",
            "role": "stream",
            "producer_type": "iterator",
            "break_conditions": ("producer.exhausted", "disconnect"),
            "transaction_unit": "per_stream",
        }
    )

    assert region["transaction_unit"] == "per_stream"
    assert region["transaction_boundary_eligible"] is True
