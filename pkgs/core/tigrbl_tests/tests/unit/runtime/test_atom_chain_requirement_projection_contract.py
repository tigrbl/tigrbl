from __future__ import annotations

import pytest

from tigrbl_kernel.runtime_contracts import project_atom_chain_requirements


def _chain():
    return (
        {
            "atom_id": "transport.receive",
            "hook_id": "ingress",
            "source": "binding:http.stream",
            "requirements": {
                "semantic_identity": True,
                "concrete_identity": True,
                "engine": "async",
                "transport_delivery": "ordered",
                "framing": "stream",
                "idempotency": "declared",
                "retry": "runtime-owned",
                "replay": "recorded-input",
                "session_isolation": "session",
                "engine_session_isolation": "attempt",
            },
        },
        {
            "atom_id": "handler.invoke",
            "hook_id": "invoke",
            "source": "kernel:plan",
            "requirements": {
                "semantic_identity": True,
                "concrete_identity": True,
                "engine": "async",
                "transport_delivery": "ordered",
                "framing": "stream",
                "idempotency": "declared",
                "retry": "runtime-owned",
                "replay": "recorded-input",
                "session_isolation": "session",
                "engine_session_isolation": "attempt",
            },
        },
    )


def test_compiled_atom_chain_projects_minimal_runtime_requirements() -> None:
    projection = project_atom_chain_requirements(_chain())

    assert projection["rollup"] == {"atom_count": 2, "capability_count": 10}


def test_projection_includes_required_semantic_and_concrete_identity() -> None:
    requirements = project_atom_chain_requirements(_chain())["requirements"]

    assert requirements["semantic_identity"] is True
    assert requirements["concrete_identity"] is True


def test_projection_declares_engine_requirements_without_engine_downgrade() -> None:
    assert project_atom_chain_requirements(_chain())["requirements"]["engine"] == "async"


def test_projection_declares_transport_delivery_and_framing_requirements() -> None:
    requirements = project_atom_chain_requirements(_chain())["requirements"]

    assert requirements["transport_delivery"] == "ordered"
    assert requirements["framing"] == "stream"


def test_projection_declares_idempotency_retry_and_replay_requirements() -> None:
    requirements = project_atom_chain_requirements(_chain())["requirements"]

    assert requirements["idempotency"] == "declared"
    assert requirements["retry"] == "runtime-owned"
    assert requirements["replay"] == "recorded-input"


def test_projection_declares_session_and_engine_session_isolation_requirements() -> None:
    requirements = project_atom_chain_requirements(_chain())["requirements"]

    assert requirements["session_isolation"] == "session"
    assert requirements["engine_session_isolation"] == "attempt"


def test_projection_preserves_atom_hook_order_without_reordering_hot_path() -> None:
    projection = project_atom_chain_requirements(_chain())

    assert projection["atom_order"] == ("transport.receive", "handler.invoke")
    assert projection["hook_order"] == ("ingress", "invoke")


def test_projection_rejects_missing_required_atom_requirement_metadata() -> None:
    bad = ({**_chain()[0], "requirements": {"semantic_identity": True}},)

    with pytest.raises(ValueError, match="missing atom requirement metadata"):
        project_atom_chain_requirements(bad)


def test_projection_diagnostics_include_atom_id_hook_id_and_requirement_source() -> None:
    diagnostic = project_atom_chain_requirements(_chain())["diagnostics"][0]

    assert diagnostic == {
        "atom_id": "transport.receive",
        "hook_id": "ingress",
        "requirement_source": "binding:http.stream",
    }


def test_projection_is_deterministic_for_same_compiled_chain() -> None:
    assert project_atom_chain_requirements(_chain()) == project_atom_chain_requirements(_chain())


def test_projection_supports_runtime_rollup_and_compaction_summaries() -> None:
    projection = project_atom_chain_requirements(_chain())

    assert projection["rollup"]["atom_count"] == 2
    assert projection["compaction"]["atom_order_hash"]


def test_projection_does_not_create_redundant_capability_vector() -> None:
    projection = project_atom_chain_requirements((_chain()[0], _chain()[0]))

    assert projection["rollup"]["capability_count"] == 10
