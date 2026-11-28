from __future__ import annotations

from tigrbl_core._spec.op_spec import OpSpec
from tigrbl_kernel.core import Kernel


def _batch_labels(model: type, alias: str) -> list[str]:
    chains = Kernel()._build_op(model, alias)
    labels: list[str] = []
    for steps in chains.values():
        labels.extend(
            label
            for step in steps
            if "batch" in (label := getattr(step, "__tigrbl_label", ""))
            or "fanout" in label
            or "intent" in label
            or "transport:" in label
        )
    return labels


def test_batch_atoms_are_excluded_by_default() -> None:
    class Widget:
        ops = (OpSpec(alias="create", target="create"),)

    assert _batch_labels(Widget, "create") == []


def test_batch_atoms_are_compiled_when_op_enables_batching() -> None:
    class Widget:
        ops = (
            OpSpec(
                alias="create",
                target="create",
                batch={"enabled": True, "max_size": 4},
            ),
        )

    labels = _batch_labels(Widget, "create")

    assert "atom:batch:admit@batch.admit" in labels
    assert "atom:batch:execute@batch.execute" in labels
    assert "atom:fanout:emit_many@batch.fanout.emit" in labels
    assert labels.index("atom:intent:final_group_key@batch.intent.group_key") < labels.index(
        "atom:batch:admit@batch.admit"
    )


def test_batch_policy_does_not_enable_reads_by_default() -> None:
    class Widget:
        ops = (OpSpec(alias="read", target="read", batch={"enabled": True}),)

    assert _batch_labels(Widget, "read") == []
