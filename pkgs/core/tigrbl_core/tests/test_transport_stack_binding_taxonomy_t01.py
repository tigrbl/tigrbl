import pytest

from tigrbl_core._spec.transport_stack import (
    ACTIVE_DRAFT,
    H11,
    H2_WT,
    H3_WS,
    H3_WT,
    H3_WT_WS,
    STABLE_RFC,
    BindingStackError,
    binding_stack_maturity,
    classify_binding_stack,
    compose_h3_binding_projections,
    require_binding_stack,
)


def test_binding_projection_classifies_stable_and_draft_stacks():
    assert binding_stack_maturity(H11) == STABLE_RFC
    assert classify_binding_stack(H3_WS).source == "RFC 9220"
    assert classify_binding_stack(H3_WT).maturity == ACTIVE_DRAFT
    assert classify_binding_stack(H2_WT).binding_profile == "webtransport-h2-capsule-lane"


def test_draft_binding_projections_require_runtime_capability_when_gate_is_closed():
    assert classify_binding_stack(H3_WT).requires_runtime_capability is True
    with pytest.raises(BindingStackError):
        require_binding_stack(H3_WT, allow_draft=False)


def test_invalid_nested_stack_binding_rejected():
    assert classify_binding_stack(H3_WT_WS).valid is False
    with pytest.raises(BindingStackError):
        require_binding_stack(H3_WT_WS)


def test_shared_h3_listener_keeps_binding_projections_separate():
    assert compose_h3_binding_projections("h3", H3_WT, H3_WS) == ("h3", H3_WT, H3_WS)
    with pytest.raises(BindingStackError):
        compose_h3_binding_projections(H3_WT_WS)
