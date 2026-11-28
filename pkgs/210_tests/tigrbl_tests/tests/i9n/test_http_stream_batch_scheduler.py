from __future__ import annotations

from types import SimpleNamespace

import pytest

from tigrbl_atoms.atoms.batch import admit, await_seal, execute, result_slots
from tigrbl_atoms.atoms.batch import prepare_execute, seal_check
from tigrbl_atoms.atoms.fanout import emit_many, shape
from tigrbl_atoms.atoms.intent import build as intent_build
from tigrbl_atoms.atoms.intent import final_group_key
from tigrbl_atoms.atoms.transport import sink_bind, unit_capture


class StreamDb:
    def __init__(self) -> None:
        self.loops = []

    async def executeloop(self, statements):
        self.loops.append(list(statements))
        return [
            {
                "statement": statement,
                "chunk": bytes(payload).decode("utf-8"),
            }
            for statement, payload in statements
        ]


class StreamSink:
    def __init__(self) -> None:
        self.emitted = []

    async def emit_many(self, payloads):
        self.emitted.append(list(payloads))


def _admit_stream_chunk(
    ctx,
    *,
    chunk_id: int,
    statement: str,
    sink: StreamSink,
) -> None:
    payload = memoryview(f"chunk-{chunk_id}".encode("utf-8"))
    ctx.transport_unit_kind = "http.stream.chunk"
    ctx.transport_unit = payload
    ctx.payload_ref = payload
    ctx.correlation_id = f"stream-{chunk_id}"
    ctx.transport_sink = sink
    ctx.transport_sink_index = chunk_id - 1
    ctx.transport_sink_family = "http.stream"
    unit_capture._run(None, ctx)
    sink_bind._run(None, ctx)
    intent_build._run(None, ctx)
    ctx.temp["intent"]["statement"] = statement
    ctx.temp["intent"]["force_seal"] = chunk_id == 2
    final_group_key._run(None, ctx)
    admit._run(None, ctx)
    seal_check._run(None, ctx)
    await_seal._run(None, ctx)


@pytest.mark.asyncio
async def test_http_stream_batch_scheduler_uses_executeloop_for_chunks() -> None:
    sink = StreamSink()
    ctx = SimpleNamespace(
        db=StreamDb(),
        op="append_chunk",
        model=object,
        batch_policy={"enabled": True, "max_size": 2},
        temp={},
    )

    _admit_stream_chunk(ctx, chunk_id=1, statement="append_orders", sink=sink)
    _admit_stream_chunk(ctx, chunk_id=2, statement="append_audit", sink=sink)
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

    assert ctx.temp["batch_execution_kind"] == "executeloop"
    assert [statement for statement, _payload in ctx.db.loops[0]] == [
        "append_orders",
        "append_audit",
    ]
    assert [payload["correlation_id"] for payload in sink.emitted[0]] == [
        "stream-1",
        "stream-2",
    ]
    assert [payload["result"]["chunk"] for payload in sink.emitted[0]] == [
        "chunk-1",
        "chunk-2",
    ]
