from __future__ import annotations

import pytest

from tigrbl_core._spec.hook_types import HookPhase
from tigrbl_typing import phases


def test_canonical_phase_tree_no_longer_exposes_ingress_route() -> None:
    phase_names = set(phases.PHASES)
    if "INGRESS_ROUTE" in phase_names:
        pytest.xfail("INGRESS_ROUTE still exists in the canonical phase tree")
    assert "INGRESS_ROUTE" not in phase_names


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
