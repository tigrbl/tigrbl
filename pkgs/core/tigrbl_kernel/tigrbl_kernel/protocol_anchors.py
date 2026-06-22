from __future__ import annotations

from typing import Any


def canonical_protocol_anchor_order(
    binding: str,
    subevent: str,
    *,
    edge: str = "ok",
) -> tuple[str, ...]:
    del binding, subevent
    order = [
        "dispatch.exchange.select",
        "dispatch.family.derive",
        "dispatch.subevent.derive",
        "framing.decode",
        "framing.encode",
        "transport.emit",
        "transport.emit_complete",
    ]
    if edge == "err":
        order.extend(("err.ctx.build", "err.classify", "err.transport.shape"))
    return tuple(order)


def python_protocol_anchor_trace(case: dict[str, Any]) -> tuple[str, ...]:
    return canonical_protocol_anchor_order(
        str(case.get("binding")),
        str(case.get("subevent")),
    )


__all__ = [
    "canonical_protocol_anchor_order",
    "python_protocol_anchor_trace",
]
