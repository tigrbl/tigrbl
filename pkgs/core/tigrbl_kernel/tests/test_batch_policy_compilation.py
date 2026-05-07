from __future__ import annotations

from tigrbl_core._spec.op_spec import OpSpec
from tigrbl_kernel.core import Kernel


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
