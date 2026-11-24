from __future__ import annotations

from types import SimpleNamespace

from tigrbl_kernel import Kernel
from tigrbl_atoms.types import EdgeTarget


def test_kernel_plan_compiles_typed_ok_err_phase_tree_nodes() -> None:
    class Model:
        ops = SimpleNamespace(
            by_alias={
                "create": [
                    SimpleNamespace(
                        alias="create",
                        target="create",
                        persist="default",
                        bindings=(),
                    )
                ]
            }
        )

    app = SimpleNamespace(tables=(Model,))

    plan = Kernel(atoms=[]).compile_plan(app)

    nodes = plan.phase_trees[0]
    assert nodes
    assert tuple(plan.packed.phase_tree_nodes) == nodes  # type: ignore[union-attr]
    assert all(node.ok_child.kind == "ok" for node in nodes)
    assert all(node.err_child.kind == "err" for node in nodes)
    assert nodes[-1].ok_child.target.kind == "terminal"
    assert nodes[-1].ok_child.target.ref == "ok"

    handler = next(node for node in nodes if node.phase == "HANDLER")
    assert handler.err_child.target.kind == "rollback"
    assert handler.err_child.target.ref == "TX_ROLLBACK"
    assert handler.err_child.target.fallback == "ON_HANDLER_ERROR"


def test_legacy_rollback_edge_target_normalizes_to_tx_rollback() -> None:
    target = EdgeTarget.rollback("ON_ROLLBACK", fallback="ON_END_TX_ERROR")

    assert target.ref == "TX_ROLLBACK"
    assert target.fallback == "ON_TX_COMMIT_ERROR"
