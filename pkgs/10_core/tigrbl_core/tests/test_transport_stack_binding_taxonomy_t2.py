import pytest

from tigrbl_core._spec.transport_stack import (
    BINDING_STACK_PROJECTIONS,
    H2_WS,
    H3_WS,
    H3_WT,
    H3_WT_WS,
    BindingStackError,
    binding_stack_maturity,
    classify_binding_stack,
    compose_h3_binding_projections,
    require_binding_stack,
)


def test_binding_stack_normalization_is_case_and_whitespace_tolerant():
    assert classify_binding_stack(" H3 + WT ").stack == H3_WT
    assert classify_binding_stack("H2+WS").stack == H2_WS


def test_unknown_and_non_string_binding_stack_inputs_fail_closed():
    for stack in ("h4", "ws-over-wt", ""):
        with pytest.raises(BindingStackError):
            classify_binding_stack(stack)
    with pytest.raises(BindingStackError):
        classify_binding_stack(object())  # type: ignore[arg-type]


def test_binding_projection_registry_view_is_immutable():
    with pytest.raises(TypeError):
        BINDING_STACK_PROJECTIONS["local"] = BINDING_STACK_PROJECTIONS[H3_WT]  # type: ignore[index]


def test_binding_maturity_and_draft_runtime_gate_are_enforced():
    assert binding_stack_maturity(H3_WT) == "active-draft"
    with pytest.raises(BindingStackError):
        require_binding_stack(" H3 + WT ", allow_draft=False)
    with pytest.raises(BindingStackError):
        require_binding_stack(f" {H3_WT_WS.upper()} ")


def test_h3_binding_projection_rejects_duplicate_and_non_h3_carriers():
    with pytest.raises(BindingStackError):
        compose_h3_binding_projections(H3_WS, H3_WS)
    with pytest.raises(BindingStackError):
        compose_h3_binding_projections(H3_WT, "h2+wt")
    assert compose_h3_binding_projections(H3_WT, H3_WS) == (H3_WT, H3_WS)
