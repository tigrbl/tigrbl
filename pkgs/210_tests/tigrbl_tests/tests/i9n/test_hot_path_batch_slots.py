from __future__ import annotations

from types import SimpleNamespace

from tigrbl_atoms.atoms.batch import admit, await_seal, prepare_execute, seal_check
from tigrbl_atoms.atoms.intent import build as intent_build
from tigrbl_atoms.atoms.intent import final_group_key
from tigrbl_atoms.atoms.transport import sink_bind, unit_capture


def test_batch_prepare_uses_slot_rows_without_payload_dict_materialization() -> None:
    hot = SimpleNamespace(
        slot_field_names=("id", "name"),
        slot_field_index={"id": 0, "name": 1},
        slot_values=[1, "Ada"],
        slot_present=bytearray([1, 1]),
        assembled_slot_values=None,
        assembled_slot_present=None,
        body_view=memoryview(b'{"id":1,"name":"Ada"}'),
    )
    ctx = SimpleNamespace(
        op="create",
        model=object,
        batch_policy={"enabled": True, "max_size": 1},
        payload_ref=None,
        transport_sink_index=0,
        transport_sink_family="http",
        temp={"hot_ctx": hot},
    )

    unit_capture.hot_run(None, ctx)
    sink_bind.hot_run(None, ctx)
    intent_build.hot_run(None, ctx)
    ctx.temp["intent"]["statement"] = "insert"
    final_group_key.hot_run(None, ctx)
    admit._run(None, ctx)
    seal_check._run(None, ctx)
    await_seal._run(None, ctx)
    prepare_execute.hot_run(None, ctx)

    group = ctx.temp["batch_group"]
    admission = group.admissions[0]
    assert admission.slot_payload is not None
    assert admission.parameter_row == (1, "Ada")
    assert group.parameter_columns == ("id", "name")
    assert group.parameter_rows == [(1, "Ada")]
    assert ctx.temp["batch_parameter_sets"] == [(1, "Ada")]
