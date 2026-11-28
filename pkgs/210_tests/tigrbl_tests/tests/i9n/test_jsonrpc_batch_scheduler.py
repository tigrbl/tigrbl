from __future__ import annotations

from types import SimpleNamespace

import pytest

from tigrbl_atoms.atoms.batch import admit, await_seal, execute, result_slots
from tigrbl_atoms.atoms.batch import prepare_execute, seal_check
from tigrbl_atoms.atoms.fanout import emit_many, shape
from tigrbl_atoms.atoms.intent import build as intent_build
from tigrbl_atoms.atoms.intent import final_group_key
from tigrbl_atoms.atoms.transport import sink_bind, unit_capture


class JsonRpcDb:
    def __init__(self) -> None:
        self.calls = []

    async def executemany(self, statement, parameter_sets):
        self.calls.append((statement, list(parameter_sets)))
        return [
            {"jsonrpc": "2.0", "id": params["id"], "result": params["params"]}
            for params in parameter_sets
        ]


class JsonRpcSink:
    def __init__(self) -> None:
        self.emitted = []

    async def emit_many(self, payloads):
        self.emitted.append(list(payloads))


def _admit_jsonrpc(ctx, *, rpc_id: int, sink: JsonRpcSink) -> None:
    ctx.transport_unit_kind = "http.jsonrpc.request"
    ctx.transport_unit = {
        "jsonrpc": "2.0",
        "method": "Widget.create",
        "params": {"name": f"widget-{rpc_id}"},
        "id": rpc_id,
    }
    ctx.payload_ref = ctx.transport_unit
    ctx.correlation_id = f"rpc-{rpc_id}"
    ctx.transport_sink = sink
    ctx.transport_sink_index = rpc_id - 1
    ctx.transport_sink_family = "http.jsonrpc"
    unit_capture._run(None, ctx)
    sink_bind._run(None, ctx)
    intent_build._run(None, ctx)
    ctx.temp["intent"]["statement"] = "insert_widget"
    ctx.temp["intent"]["force_seal"] = rpc_id == 2
    final_group_key._run(None, ctx)
    admit._run(None, ctx)
    seal_check._run(None, ctx)
    await_seal._run(None, ctx)


@pytest.mark.asyncio
async def test_jsonrpc_batch_scheduler_executemany_fans_out_by_rpc_id() -> None:
    sink = JsonRpcSink()
    ctx = SimpleNamespace(
        db=JsonRpcDb(),
        op="create",
        model=object,
        batch_policy={"enabled": True, "max_size": 2},
        temp={},
    )

    _admit_jsonrpc(ctx, rpc_id=1, sink=sink)
    _admit_jsonrpc(ctx, rpc_id=2, sink=sink)
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
            "insert_widget",
            [
                {
                    "jsonrpc": "2.0",
                    "method": "Widget.create",
                    "params": {"name": "widget-1"},
                    "id": 1,
                },
                {
                    "jsonrpc": "2.0",
                    "method": "Widget.create",
                    "params": {"name": "widget-2"},
                    "id": 2,
                },
            ],
        )
    ]
    assert [payload["correlation_id"] for payload in sink.emitted[0]] == [
        "rpc-1",
        "rpc-2",
    ]
    assert [payload["result"]["id"] for payload in sink.emitted[0]] == [1, 2]
