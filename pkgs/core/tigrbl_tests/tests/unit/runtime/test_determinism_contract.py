from __future__ import annotations

import pytest

from tigrbl_core._spec import OpSpec, TableProfileSpec
from tigrbl_core._spec.table_profile_bindings import lower_binding_tokens_for_ops
from tigrbl_kernel.cross_transport import (
    compile_equivalence_manifest,
    equivalent_transport_results,
    normalized_transport_result,
)
from tigrbl_kernel.protocol_bindings import compile_binding_protocol_plan
from tigrbl_kernel.runtime_contracts import (
    attempt_record,
    compile_retry_policy,
    evaluate_retry_attempts,
    project_atom_chain_requirements,
    replay_record,
    stable_semantic_id,
)


def _chain():
    req = {
        "semantic_identity": True,
        "concrete_identity": True,
        "engine": "sync",
        "transport_delivery": "ordered",
        "framing": "json",
        "idempotency": "declared",
        "retry": "runtime-owned",
        "replay": "recorded-input",
        "session_isolation": "session",
        "engine_session_isolation": "attempt",
    }
    return (
        {"atom_id": "wire.decode", "hook_id": "ingress", "requirements": req},
        {"atom_id": "handler.invoke", "hook_id": "invoke", "requirements": req},
    )


def test_same_input_engine_state_and_plan_produce_same_normalized_result() -> None:
    first = normalized_transport_result({"value": {"id": 1}, "headers": {"date": "now"}})
    second = normalized_transport_result({"value": {"id": 1}, "headers": {"date": "later"}})

    assert first == second


def test_runtime_plan_compilation_is_deterministic_for_equivalent_specs() -> None:
    binding = {"kind": "http.rest", "path": "/items", "methods": ("GET",)}

    assert compile_binding_protocol_plan("Item.read", binding) == compile_binding_protocol_plan(
        "Item.read", binding
    )


def test_selector_and_binding_lowering_are_order_stable() -> None:
    class Table:
        pass

    profile = TableProfileSpec(kind="rest", ops=(OpSpec(alias="read", target="read"),))
    ops = profile.ops

    assert lower_binding_tokens_for_ops(Table, profile, ops) == lower_binding_tokens_for_ops(
        Table, profile, ops
    )


def test_atom_chain_requirement_projection_is_order_stable() -> None:
    assert project_atom_chain_requirements(_chain()) == project_atom_chain_requirements(_chain())


def test_hook_and_atom_execution_order_is_deterministic() -> None:
    projection = project_atom_chain_requirements(_chain())

    assert projection["atom_order"] == ("wire.decode", "handler.invoke")
    assert projection["hook_order"] == ("ingress", "invoke")


def test_error_and_diagnostic_payloads_are_deterministic() -> None:
    assert normalized_transport_result(
        {"error": {"code": "bad"}, "diagnostics": {"classification": "client", "trace_id": "a"}}
    ) == normalized_transport_result(
        {"error": {"code": "bad"}, "diagnostics": {"classification": "client", "trace_id": "b"}}
    )


def test_persistence_effects_are_deterministic_under_declared_ordering() -> None:
    assert equivalent_transport_results(
        {"effects": ("insert:1", "commit"), "effect_fence": "committed"},
        {"transport": "http", "effects": ("insert:1", "commit"), "effect_fence": "committed"},
    )


def test_idempotent_duplicate_attempts_have_deterministic_results() -> None:
    policy = compile_retry_policy(max_attempts=2, retryable_errors=("timeout",), backoff_ms=(5,))

    first = evaluate_retry_attempts(policy=policy, failures=("timeout",), idempotency_key="k1")
    second = evaluate_retry_attempts(policy=policy, failures=("timeout",), idempotency_key="k1")

    assert first == second


def test_cross_transport_equivalent_operations_have_deterministic_semantics() -> None:
    manifest = compile_equivalence_manifest(
        "Item.read",
        (
            {"kind": "http.rest", "path": "/items/{id}", "methods": ("GET",)},
            {"kind": "http.jsonrpc", "rpc_method": "Item.read"},
        ),
    )

    assert manifest == compile_equivalence_manifest(
        "Item.read",
        (
            {"kind": "http.rest", "path": "/items/{id}", "methods": ("GET",)},
            {"kind": "http.jsonrpc", "rpc_method": "Item.read"},
        ),
    )


def test_trace_qlog_replay_and_rollup_records_are_deterministic() -> None:
    assert replay_record(replay_id="r1", original_attempt_id="a1") == replay_record(
        replay_id="r1", original_attempt_id="a1"
    )
    assert attempt_record(
        app_id="app",
        router_id="router",
        table_id="Item",
        op_id="Item.read",
        attempt_id="a1",
    ) == attempt_record(
        app_id="app",
        router_id="router",
        table_id="Item",
        op_id="Item.read",
        attempt_id="a1",
    )


def test_nondeterministic_inputs_are_rejected_or_declared() -> None:
    with pytest.raises(ValueError, match="semantic id parts"):
        stable_semantic_id("Item", "")


def test_determinism_contract_excludes_wall_clock_random_and_external_effects() -> None:
    left = {"value": 1, "diagnostics": {"classification": "ok", "trace_id": "wall-clock"}}
    right = {"value": 1, "diagnostics": {"classification": "ok", "trace_id": "random"}}

    assert normalized_transport_result(left) == normalized_transport_result(right)
