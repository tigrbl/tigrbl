from tigrbl.hook.types import PHASES as HOOK_PHASES
from tigrbl.runtime import events as _ev


def test_stages_constant_lists_all_lifecycle_anchors_in_order() -> None:
    """Ensure runtime PHASES exports the complete ingress-to-egress ordered sequence."""
    assert _ev.PHASES == (
        "INGRESS_BEGIN",
        "INGRESS_PARSE",
        "INGRESS_ROUTE",
        "PRE_TX_BEGIN",
        "START_TX",
        "PRE_HANDLER",
        "HANDLER",
        "POST_HANDLER",
        "PRE_COMMIT",
        "END_TX",
        "POST_COMMIT",
        "EGRESS_SHAPE",
        "EGRESS_FINALIZE",
        "POST_RESPONSE",
        "ON_ERROR",
        "ON_PRE_TX_BEGIN_ERROR",
        "ON_START_TX_ERROR",
        "ON_PRE_HANDLER_ERROR",
        "ON_HANDLER_ERROR",
        "ON_POST_HANDLER_ERROR",
        "ON_PRE_COMMIT_ERROR",
        "ON_END_TX_ERROR",
        "ON_POST_COMMIT_ERROR",
        "ON_POST_RESPONSE_ERROR",
        "ON_ROLLBACK",
    )


def test_hook_lifecycle_includes_all_error_anchors_in_order() -> None:
    error_anchors = (
        "ON_ERROR",
        "ON_PRE_TX_BEGIN_ERROR",
        "ON_START_TX_ERROR",
        "ON_PRE_HANDLER_ERROR",
        "ON_HANDLER_ERROR",
        "ON_POST_HANDLER_ERROR",
        "ON_PRE_COMMIT_ERROR",
        "ON_END_TX_ERROR",
        "ON_POST_COMMIT_ERROR",
        "ON_POST_RESPONSE_ERROR",
        "ON_ROLLBACK",
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
        "END_TX",
        "POST_COMMIT",
        "POST_RESPONSE",
    )
    assert HOOK_PHASES[9:] == error_anchors
