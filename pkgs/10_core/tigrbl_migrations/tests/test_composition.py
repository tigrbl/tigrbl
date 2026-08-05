from __future__ import annotations

import pytest

from tigrbl_migrations import (
    DatabaseObject,
    ManifestError,
    Migration,
    SchemaRequirement,
    StorageComposition,
    StorageManifest,
)


def up(_connection) -> None:
    return None


def component(name: str, head: str, *, objects=(), requires=()) -> StorageManifest:
    return StorageManifest(
        manifest_version="1.0.0",
        component_id=f"tigrbl.test.storage.{name}",
        distribution=f"tigrbl-test-{name}",
        import_root=f"tigrbl_test_{name}",
        schema_contract="1.0.0",
        migration_head=head,
        migrations_package=f"tigrbl_test_{name}.migrations.versions",
        objects=tuple(objects),
        requires=tuple(requires),
    )


def test_cross_component_minimum_revision_orders_roots() -> None:
    base = component("base", "base-2")
    child = component(
        "child",
        "child-1",
        requires=(
            SchemaRequirement(
                component=base.component_id,
                contract=">=1.0.0,<2.0.0",
                minimum_revision="base-1",
            ),
        ),
    )
    migrations = (
        Migration("base-1", base.component_id, upgrade=up),
        Migration("base-2", base.component_id, parents=("base-1",), upgrade=up),
        Migration("child-1", child.component_id, upgrade=up),
    )
    graph = StorageComposition.from_manifests(child, base).graph(migrations)
    assert graph.topological_order() == ("base-1", "base-2", "child-1")


def test_duplicate_physical_ownership_is_rejected() -> None:
    first = component(
        "one",
        "one-1",
        objects=(DatabaseObject("tigrbl.test.one.table.x", "table", "test.records"),),
    )
    second = component(
        "two",
        "two-1",
        objects=(DatabaseObject("tigrbl.test.two.table.x", "table", "test.records"),),
    )
    with pytest.raises(ManifestError, match="claimed"):
        StorageComposition.from_manifests(first, second)
