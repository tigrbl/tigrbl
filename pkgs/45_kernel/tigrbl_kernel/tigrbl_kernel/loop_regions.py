from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def compile_loop_region(region: Mapping[str, Any]) -> dict[str, object]:
    loop_id = region.get("loop_id")
    binding = str(region.get("binding") or "")
    role = str(region.get("role") or "")
    producer_type = region.get("producer_type")
    breaks = tuple(region.get("break_conditions") or ())
    transaction_unit = str(region.get("transaction_unit") or "none")

    if not loop_id or not binding or not role or not producer_type or not breaks:
        raise ValueError("loop region requires producer, break, transaction, and err metadata")
    if binding == "http.sse" and transaction_unit == "per_chunk":
        raise ValueError("loop region transaction unit per_chunk is not eligible for http.sse")

    continue_target = f"{loop_id}.continue"
    exit_target = "transport.close"
    err_target = str(region.get("err_target") or _default_err_target(binding))
    completion_fence = "POST_EMIT" if binding in {"http.sse", "http.stream"} else None

    compiled = {
        "loop_id": loop_id,
        "binding": binding,
        "role": role,
        "producer_type": producer_type,
        "break_conditions": breaks,
        "continue_target": continue_target,
        "exit_target": exit_target,
        "err_target": err_target,
        "completion_fence": completion_fence,
        "ok_child": {"kind": "ok", "target": continue_target},
        "err_child": {"kind": "err", "target": err_target},
        "subevent": region.get("subevent"),
        "transaction_unit": transaction_unit,
        "transaction_boundary_eligible": transaction_unit
        in {"per_stream", "per_message", "per_datagram"},
        "error_ctx": {
            "binding": binding,
            "subevent": region.get("subevent"),
            "loop_id": loop_id,
            "rollback_required": False,
        },
    }
    return compiled


def _default_err_target(binding: str) -> str:
    if binding in {"websocket", "ws", "internal.message"}:
        return "ON_HANDLER_ERROR"
    if binding in {"http.stream", "http.sse", "udp.datagram"}:
        return "transport.close"
    return "ON_ERROR"


__all__ = ["compile_loop_region"]
