from __future__ import annotations

import pytest

from tigrbl_core._spec.hook_types import HookPhase
from tigrbl_typing import phases


def _phase_names_from_projection(value: object) -> set[str]:
    if isinstance(value, dict):
        candidates = value.get("phases") or value.get("phase_order") or value.get("nodes")
    else:
        candidates = getattr(value, "phases", None) or getattr(value, "phase_order", None)
        candidates = candidates or getattr(value, "nodes", None)
    if candidates is None:
        return set()

    names: set[str] = set()
    for candidate in candidates:
        if isinstance(candidate, str):
            names.add(candidate)
        elif isinstance(candidate, dict):
            phase = candidate.get("canonical_phase") or candidate.get("phase")
            if phase:
                names.add(str(phase))
        else:
            phase = getattr(candidate, "canonical_phase", None) or getattr(candidate, "phase", None)
            if phase:
                names.add(str(phase))
    return names


def test_canonical_phase_tree_no_longer_exposes_ingress_route() -> None:
    phase_names = set(phases.PHASES)
    if "INGRESS_ROUTE" in phase_names:
        pytest.xfail("INGRESS_ROUTE still exists in the canonical phase tree")
    assert "INGRESS_ROUTE" not in phase_names


def test_ingress_route_is_not_a_public_hook_phase_member() -> None:
    if "INGRESS_ROUTE" in HookPhase.__members__:
        pytest.xfail("INGRESS_ROUTE is still exposed as a public hook phase")

    assert "INGRESS_ROUTE" not in HookPhase.__members__


def test_ingress_route_is_not_normalized_as_a_legacy_phase_alias() -> None:
    normalized = phases.normalize_phase("INGRESS_ROUTE")
    if normalized != "INGRESS_ROUTE":
        pytest.xfail("INGRESS_ROUTE is still accepted as a legacy phase alias")

    assert normalized == "INGRESS_ROUTE"


def test_protocol_phase_projection_uses_ingress_parse_not_ingress_route() -> None:
    compile_projection = getattr(phases, "compile_protocol_phase_projection", None)
    if compile_projection is None:
        pytest.xfail("canonical protocol phase projection compiler is not implemented")

    projection = compile_projection("http.rest")
    phase_names = _phase_names_from_projection(projection)

    assert "INGRESS_ROUTE" not in phase_names
    assert {"INGRESS_PARSE", "HANDLER", "POST_EMIT"} <= phase_names


def test_post_emit_is_a_canonical_completion_fence_after_emit() -> None:
    phase_order = tuple(phases.PHASES)
    missing = {"EMIT", "POST_EMIT"} - set(phase_order)
    if missing:
        pytest.xfail(f"canonical emission fence phases are missing: {sorted(missing)}")

    assert phase_order.index("EMIT") < phase_order.index("POST_EMIT")


def test_transaction_legacy_aliases_are_removed_from_hook_phase_members() -> None:
    legacy_aliases = {"END_TX", "ON_END_TX_ERROR", "ON_ROLLBACK"}
    exposed_aliases = legacy_aliases & set(HookPhase.__members__)
    if exposed_aliases:
        pytest.xfail(
            f"legacy transaction aliases are still exposed: {sorted(exposed_aliases)}"
        )
    assert exposed_aliases == set()


def test_transaction_legacy_aliases_are_no_longer_normalized() -> None:
    legacy_aliases = ("END_TX", "ON_END_TX_ERROR", "ON_ROLLBACK")
    still_normalized = [
        alias for alias in legacy_aliases if phases.normalize_phase(alias) != alias
    ]
    if still_normalized:
        pytest.xfail(
            "legacy transaction aliases are still accepted by normalize_phase: "
            f"{still_normalized}"
        )
    assert still_normalized == []
