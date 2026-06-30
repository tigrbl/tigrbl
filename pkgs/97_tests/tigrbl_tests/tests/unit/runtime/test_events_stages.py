from tigrbl.hook.types import PHASES as HOOK_PHASES
from tigrbl.runtime import events as _ev
from tigrbl_kernel import events as _kernel_events
from tigrbl_atoms import HookPhase
from tigrbl_atoms.types import error_phase_for


def test_stages_constant_lists_all_lifecycle_anchors_in_order() -> None:
    """Ensure runtime PHASES exports the complete ingress-to-egress ordered sequence."""
    assert _ev.PHASES == _kernel_events.PHASES
    assert "INGRESS_DISPATCH" in _ev.PHASES
    assert "INGRESS_ROUTE" not in _ev.PHASES


def test_hook_lifecycle_includes_all_error_anchors_in_order() -> None:
    error_anchors = (
        "ON_ERROR",
        "ON_PRE_TX_BEGIN_ERROR",
        "ON_START_TX_ERROR",
        "ON_PRE_HANDLER_ERROR",
        "ON_HANDLER_ERROR",
        "ON_POST_HANDLER_ERROR",
        "ON_PRE_COMMIT_ERROR",
        "ON_TX_COMMIT_ERROR",
        "ON_POST_COMMIT_ERROR",
        "ON_POST_RESPONSE_ERROR",
        "TX_ROLLBACK",
    )

    for anchor in error_anchors:
        assert anchor in HOOK_PHASES

    base_order = HOOK_PHASES[:9]
    assert base_order == (
        "PRE_TX_BEGIN",
        "START_TX",
        "PRE_HANDLER",
        "HANDLER",
        "POST_HANDLER",
        "PRE_COMMIT",
        "TX_COMMIT",
        "POST_COMMIT",
        "POST_RESPONSE",
    )
    assert HOOK_PHASES[9:] == error_anchors


def test_legacy_transaction_phase_names_are_accepted_at_input_boundaries() -> None:
    assert HookPhase("END_TX") is HookPhase.TX_COMMIT
    assert HookPhase("ON_END_TX_ERROR") is HookPhase.ON_TX_COMMIT_ERROR
    assert HookPhase("ON_ROLLBACK") is HookPhase.TX_ROLLBACK
    assert error_phase_for("END_TX") == "ON_TX_COMMIT_ERROR"
    assert _ev.is_error_phase("ON_ROLLBACK") is True
    assert _ev.normalize_phase("ON_ROLLBACK") == "ON_ROLLBACK"
    assert _ev.canonicalize_phase("ON_ROLLBACK") == "TX_ROLLBACK"
