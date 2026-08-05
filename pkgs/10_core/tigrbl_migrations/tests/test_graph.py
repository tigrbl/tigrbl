from __future__ import annotations

import pytest

from tigrbl_migrations import GraphError, Migration, MigrationGraph, MigrationKind


def up(_connection) -> None:
    return None


def down(_connection) -> None:
    return None


def migration(revision: str, *parents: str) -> Migration:
    return Migration(
        revision=revision,
        component="tigrbl.test.storage.alpha",
        parents=parents,
        kind=MigrationKind.STANDARD,
        reversible=True,
        upgrade=up,
        downgrade=down,
    )


def test_parallel_dag_has_deterministic_merge_order() -> None:
    graph = MigrationGraph(
        [migration("root"), migration("b", "root"), migration("a", "root"), migration("merge", "a", "b")]
    )
    assert graph.topological_order() == ("root", "a", "b", "merge")
    assert graph.component_heads("tigrbl.test.storage.alpha") == ("merge",)
    assert graph.closure("merge") == {"root", "a", "b", "merge"}


def test_cycle_fails_closed() -> None:
    graph = MigrationGraph([migration("a", "b"), migration("b", "a")])
    with pytest.raises(GraphError, match="cycle"):
        graph.topological_order()


def test_missing_parent_fails_closed() -> None:
    graph = MigrationGraph([migration("a", "missing")])
    with pytest.raises(GraphError, match="missing"):
        graph.topological_order()


def test_multiple_release_heads_are_rejected() -> None:
    graph = MigrationGraph([migration("root"), migration("a", "root"), migration("b", "root")])
    with pytest.raises(GraphError, match="graph heads"):
        graph.validate_release_head(
            component="tigrbl.test.storage.alpha", declared_head="a"
        )
