from __future__ import annotations

from types import SimpleNamespace

import pytest

from tigrbl_atoms.atoms.batch import admit, await_seal, execute, result_slots
from tigrbl_atoms.atoms.batch import prepare_execute, seal_check
from tigrbl_atoms.atoms.fanout import emit_many, shape
from tigrbl_atoms.atoms.intent import build as intent_build
from tigrbl_atoms.atoms.intent import final_group_key
from tigrbl_atoms.atoms.transport import sink_bind, unit_capture


class WebSocketDb:
    def __init__(self) -> None:
        self.calls = []

    async def executemany(self, statement, parameter_sets):
        self.calls.append((statement, list(parameter_sets)))
        return [
            {"sent": payload["text"], "socket": payload["socket"]}
            for payload in parameter_sets
        ]


class WebSocketSink:
    def __init__(self, name: str) -> None:
        self.name = name
        self.emitted = []

    async def emit_many(self, payloads):
        self.emitted.append(list(payloads))


def _admit_message(
    ctx,
    *,
    message_id: int,
    sink: WebSocketSink,
) -> None:
    ctx.transport_unit_kind = "websocket.message"
    ctx.transport_unit = {"type": "websocket.receive", "text": f"msg-{message_id}"}
    ctx.payload_ref = {"socket": sink.name, "text": f"msg-{message_id}"}
    ctx.correlation_id = f"ws-{message_id}"
    ctx.transport_sink = sink
    ctx.transport_sink_index = message_id - 1
    ctx.transport_sink_family = "websocket"
    unit_capture._run(None, ctx)
    sink_bind._run(None, ctx)
    intent_build._run(None, ctx)
    ctx.temp["intent"]["statement"] = "send_socket_message"
    ctx.temp["intent"]["force_seal"] = message_id == 2
    final_group_key._run(None, ctx)
    admit._run(None, ctx)
    seal_check._run(None, ctx)
    await_seal._run(None, ctx)


@pytest.mark.asyncio
async def test_websocket_batch_scheduler_fans_out_only_own_emissions() -> None:
    first_sink = WebSocketSink("socket-a")
    second_sink = WebSocketSink("socket-b")
    ctx = SimpleNamespace(
        db=WebSocketDb(),
        op="send_message",
        model=object,
        batch_policy={"enabled": True, "max_size": 2},
        temp={},
    )

    _admit_message(ctx, message_id=1, sink=first_sink)
    _admit_message(ctx, message_id=2, sink=second_sink)
    group = ctx.temp["batch_group"]

    prepare_execute._run(None, ctx)
    await execute._run(None, ctx)
    result_slots._run(None, ctx)

    ctx.temp["fanout_payloads"] = []
    for admission in group.admissions:
        ctx.temp["batch_admission"] = admission
        shape._run(None, ctx)
        ctx.temp["fanout_payloads"].append((admission, ctx.temp["fanout_payload"]))
    await emit_many._run(None, ctx)

    assert ctx.db.calls == [
        (
            "send_socket_message",
            [
                {"socket": "socket-a", "text": "msg-1"},
                {"socket": "socket-b", "text": "msg-2"},
            ],
        )
    ]
    assert first_sink.emitted == [
        [
            {
                "admission_id": group.admissions[0].admission_id,
                "correlation_id": "ws-1",
                "result": {"sent": "msg-1", "socket": "socket-a"},
            }
        ]
    ]
    assert second_sink.emitted == [
        [
            {
                "admission_id": group.admissions[1].admission_id,
                "correlation_id": "ws-2",
                "result": {"sent": "msg-2", "socket": "socket-b"},
            }
        ]
    ]
