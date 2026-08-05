from __future__ import annotations

import random

from tigrbl_migrations import Migration, MigrationGraph


def up(_connection) -> None:
    return None


def test_large_random_dag_is_deterministic_and_respects_every_edge() -> None:
    randomizer = random.Random(8675309)
    migrations = []
    for index in range(2_000):
        candidates = range(max(0, index - 50), index)
        parents = tuple(
            f"r{candidate:05d}"
            for candidate in candidates
            if randomizer.random() < 0.025
        )
        migrations.append(Migration(f"r{index:05d}", "tigrbl.test.scale", parents, upgrade=up))
    graph = MigrationGraph(reversed(migrations))
    first = graph.topological_order()
    second = graph.topological_order()
    positions = {revision: index for index, revision in enumerate(first)}
    assert first == second
    assert len(first) == len(migrations)
    for migration in migrations:
        assert all(positions[parent] < positions[migration.revision] for parent in migration.parents)
