from __future__ import annotations

import pytest

from tigrbl_kernel.runtime_contracts import (
    attempt_record,
    atom_execution_record,
    concrete_id,
    ensure_unique_concrete_ids,
    replay_record,
    stable_semantic_id,
)


def test_semantic_id_stability_across_transports() -> None:
    assert stable_semantic_id("app", "router", "Widget", "read") == stable_semantic_id(
        "app", "router", "Widget", "read"
    )


def test_concrete_id_uniqueness_within_parent_scope() -> None:
    ids = (
        concrete_id("stream", "session-1", "stream-1"),
        concrete_id("datagram", "session-1", "datagram-1"),
    )

    assert ensure_unique_concrete_ids(ids) == ids
    with pytest.raises(ValueError, match="unique"):
        ensure_unique_concrete_ids((ids[0], ids[0]))


def test_attempt_id_links_to_op_table_router_app() -> None:
    record = attempt_record(
        app_id="app",
        router_id="router",
        table_id="Widget",
        op_id="Widget.read",
        attempt_id="attempt-1",
    )

    assert record["op_id"] == "Widget.read"
    assert record["table_id"] == "Widget"
    assert record["router_id"] == "router"
    assert record["app_id"] == "app"


def test_atom_execution_links_to_atom_id_and_runtime_plan() -> None:
    record = atom_execution_record(
        atom_id="handler.invoke",
        attempt_id="attempt-1",
        runtime_plan_id="plan-1",
    )

    assert record == {
        "atom_id": "handler.invoke",
        "attempt_id": "attempt-1",
        "runtime_plan_id": "plan-1",
    }


def test_replay_id_preserves_original_attempt_id() -> None:
    assert replay_record(replay_id="replay-1", original_attempt_id="attempt-1") == {
        "replay_id": "replay-1",
        "original_attempt_id": "attempt-1",
    }
