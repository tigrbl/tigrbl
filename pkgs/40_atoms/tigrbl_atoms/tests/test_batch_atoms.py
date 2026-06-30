from __future__ import annotations

import importlib
from types import SimpleNamespace

import pytest

from tigrbl_atoms import events as _ev
from tigrbl_atoms.atoms import REGISTRY
from tigrbl_atoms.atoms.batch import _scheduler
from tigrbl_atoms.atoms.batch import admit, await_seal, execute, seal_check


NEW_ATOMS = (
    "tigrbl_atoms.atoms.transport.unit_capture",
    "tigrbl_atoms.atoms.transport.sink_bind",
    "tigrbl_atoms.atoms.intent.build",
    "tigrbl_atoms.atoms.intent.prekey",
    "tigrbl_atoms.atoms.intent.final_group_key",
    "tigrbl_atoms.atoms.batch.admit",
    "tigrbl_atoms.atoms.batch.dedupe",
    "tigrbl_atoms.atoms.batch.seal_check",
    "tigrbl_atoms.atoms.batch.await_seal",
    "tigrbl_atoms.atoms.batch.tx_begin",
    "tigrbl_atoms.atoms.batch.prepare_execute",
    "tigrbl_atoms.atoms.batch.execute",
    "tigrbl_atoms.atoms.batch.result_slots",
    "tigrbl_atoms.atoms.batch.precommit_validate",
    "tigrbl_atoms.atoms.batch.commit",
    "tigrbl_atoms.atoms.batch.cleanup",
    "tigrbl_atoms.atoms.batch.reject_admission",
    "tigrbl_atoms.atoms.batch.abort_group",
    "tigrbl_atoms.atoms.batch.error_project",
    "tigrbl_atoms.atoms.fanout.shape",
    "tigrbl_atoms.atoms.fanout.emit_many",
)


def test_new_batch_atom_modules_are_importable_with_valid_anchors() -> None:
    for module_name in NEW_ATOMS:
        module = importlib.import_module(module_name)
        assert callable(module.INSTANCE)
        assert module.ANCHOR in _ev.PHASES or _ev.is_valid_event(module.ANCHOR)


def test_batch_atoms_use_first_class_batch_anchors() -> None:
    expected = {
        "tigrbl_atoms.atoms.transport.unit_capture": _ev.BATCH_TRANSPORT_UNIT_CAPTURE,
        "tigrbl_atoms.atoms.transport.sink_bind": _ev.BATCH_TRANSPORT_SINK_BIND,
        "tigrbl_atoms.atoms.intent.build": _ev.BATCH_INTENT_BUILD,
        "tigrbl_atoms.atoms.intent.prekey": _ev.BATCH_PREKEY,
        "tigrbl_atoms.atoms.intent.final_group_key": _ev.BATCH_GROUP_KEY,
        "tigrbl_atoms.atoms.batch.admit": _ev.BATCH_ADMIT,
        "tigrbl_atoms.atoms.batch.dedupe": _ev.BATCH_DEDUPE,
        "tigrbl_atoms.atoms.batch.seal_check": _ev.BATCH_SEAL_CHECK,
        "tigrbl_atoms.atoms.batch.await_seal": _ev.BATCH_AWAIT_SEAL,
        "tigrbl_atoms.atoms.batch.tx_begin": _ev.BATCH_TX_BEGIN,
        "tigrbl_atoms.atoms.batch.prepare_execute": _ev.BATCH_PREPARE_EXECUTE,
        "tigrbl_atoms.atoms.batch.execute": _ev.BATCH_EXECUTE,
        "tigrbl_atoms.atoms.batch.result_slots": _ev.BATCH_RESULT_SLOTS,
        "tigrbl_atoms.atoms.batch.precommit_validate": _ev.BATCH_PRECOMMIT_VALIDATE,
        "tigrbl_atoms.atoms.batch.commit": _ev.BATCH_COMMIT,
        "tigrbl_atoms.atoms.batch.cleanup": _ev.BATCH_CLEANUP,
        "tigrbl_atoms.atoms.batch.reject_admission": _ev.BATCH_REJECT_ADMISSION,
        "tigrbl_atoms.atoms.batch.abort_group": _ev.BATCH_ABORT_GROUP,
        "tigrbl_atoms.atoms.batch.error_project": _ev.BATCH_ERROR_PROJECT,
        "tigrbl_atoms.atoms.fanout.shape": _ev.BATCH_EGRESS_SHAPE,
        "tigrbl_atoms.atoms.fanout.emit_many": _ev.BATCH_FANOUT_EMIT,
    }
    for module_name, anchor in expected.items():
        assert importlib.import_module(module_name).ANCHOR == anchor


def test_new_batch_atoms_are_registered() -> None:
    expected = {
        ("transport", "unit_capture"),
        ("transport", "sink_bind"),
        ("intent", "build"),
        ("intent", "prekey"),
        ("intent", "final_group_key"),
        ("batch", "admit"),
        ("batch", "dedupe"),
        ("batch", "seal_check"),
        ("batch", "await_seal"),
        ("batch", "tx_begin"),
        ("batch", "prepare_execute"),
        ("batch", "execute"),
        ("batch", "result_slots"),
        ("batch", "precommit_validate"),
        ("batch", "commit"),
        ("batch", "cleanup"),
        ("batch", "reject_admission"),
        ("batch", "abort_group"),
        ("batch", "error_project"),
        ("fanout", "shape"),
        ("fanout", "emit_many"),
    }
    assert expected <= set(REGISTRY)


def test_batch_admission_is_inert_when_batching_is_not_enabled() -> None:
    ctx = SimpleNamespace(temp={})

    admit._run(None, ctx)

    assert "batch" not in ctx.temp


def test_batch_admission_seals_opt_in_group() -> None:
    ctx = SimpleNamespace(
        batch_policy={"enabled": True},
        temp={
            "intent": {
                "final_group_key": ("engine", "tenant", "op"),
                "batch_policy": {"enabled": True, "max_count": 1},
                "payload_ref": {"name": "Ada"},
                "force_seal": True,
            },
            "transport": {"sink_index": 2, "sink_family": "http"},
        },
    )

    admit._run(None, ctx)
    seal_check._run(None, ctx)
    await_seal._run(None, ctx)

    group = ctx.temp["batch_group"]
    assert group.sealed is True
    assert len(group.admissions) == 1
    assert group.admissions[0].sink_index == 2


def test_batch_admission_seals_by_max_bytes() -> None:
    ctx = SimpleNamespace(
        batch_policy={"enabled": True, "max_size": 64, "max_bytes": 3},
        temp={
            "intent": {
                "final_group_key": ("engine", "tenant", "op"),
                "payload_ref": b"abcd",
                "payload_bytes": 4,
            },
            "transport": {"sink_index": 0, "sink_family": "http"},
        },
    )

    admit._run(None, ctx)
    seal_check._run(None, ctx)

    assert ctx.temp["batch_should_seal"] is True


@pytest.mark.asyncio
async def test_batch_execute_uses_executemany() -> None:
    class Db:
        def __init__(self) -> None:
            self.calls = []

        async def executemany(self, statement, parameter_sets):
            self.calls.append((statement, parameter_sets))
            return [{"id": 1}, {"id": 2}]

    db = Db()
    ctx = SimpleNamespace(
        db=db,
        temp={
            "batch_group": object(),
            "batch_statement": "insert",
            "batch_parameter_sets": [{"name": "Ada"}, {"name": "Grace"}],
        },
    )

    await execute._run(None, ctx)

    assert db.calls == [("insert", [{"name": "Ada"}, {"name": "Grace"}])]
    assert ctx.temp["batch_raw_results"] == [{"id": 1}, {"id": 2}]
    assert ctx.result == [{"id": 1}, {"id": 2}]


def test_scheduler_enabled_is_explicit() -> None:
    assert _scheduler.enabled(SimpleNamespace(temp={})) is False
    assert (
        _scheduler.enabled(
            SimpleNamespace(temp={}, batch_policy={"enabled": True})
        )
        is True
    )
