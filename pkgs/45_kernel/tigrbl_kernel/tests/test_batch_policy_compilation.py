from __future__ import annotations

from dataclasses import dataclass

from tigrbl_core._spec.op_spec import OpSpec
from tigrbl_kernel.core import Kernel


@dataclass
class AppFixture:
    tables: tuple[type, ...]


def _labels(model: type, alias: str) -> list[str]:
    return Kernel().plan_labels(model, alias)


def test_enabled_batch_policy_compiles_scheduler_atoms() -> None:
    class Widget:
        ops = (
            OpSpec(alias="create", target="create", batch={"enabled": True}),
        )

    labels = _labels(Widget, "create")

    assert "PRE_TX_BEGIN:atom:batch:admit@batch.admit" in labels
    assert "HANDLER:atom:batch:execute@batch.execute" in labels


def test_disabled_batch_policy_omits_scheduler_atoms() -> None:
    class Widget:
        ops = (OpSpec(alias="create", target="create"),)

    assert not any("batch:" in label for label in _labels(Widget, "create"))


def test_read_batch_policy_requires_allow_reads() -> None:
    class Reader:
        ops = (OpSpec(alias="read", target="read", batch={"enabled": True}),)

    class AllowedReader:
        ops = (
            OpSpec(
                alias="read",
                target="read",
                batch={"enabled": True, "allow_reads": True},
            ),
        )

    assert not any("batch:" in label for label in _labels(Reader, "read"))
    assert any("batch:" in label for label in _labels(AllowedReader, "read"))


def test_packed_hot_op_plan_carries_batch_policy_metadata() -> None:
    class Widget:
        ops = (
            OpSpec(
                alias="create",
                target="create",
                batch={
                    "enabled": True,
                    "max_size": 7,
                    "max_queue_depth": 99,
                    "max_in_flight": 3,
                    "overflow_policy": "reject",
                },
            ),
        )

    plan = Kernel().compile_plan(AppFixture(tables=(Widget,)))
    packed = plan.packed
    assert packed is not None

    hot = packed.hot_op_plans[0]

    assert hot.batch_policy_id == packed.program_batch_policy_ids[0]
    assert packed.batch_policy_table[hot.batch_policy_id] == hot.batch
    assert hot.batch.enabled is True
    assert hot.batch.max_size == 7
    assert hot.batch.max_queue_depth == 99
    assert hot.batch.max_in_flight == 3
    assert hot.batch.overflow_policy == "reject"
