from __future__ import annotations

import sqlite3

import pytest

from tigrbl_migrations import (
    DatabaseObject,
    DeploymentLock,
    Migration,
    MigrationError,
    MigrationKind,
    MigrationLedger,
    MigrationOrchestrator,
    OwnershipError,
    StorageComposition,
    StorageManifest,
)


def storage() -> StorageManifest:
    return StorageManifest(
        manifest_version="1.0.0",
        component_id="tigrbl.test.storage.alpha",
        distribution="tigrbl-test-alpha",
        import_root="tigrbl_test_alpha",
        schema_contract="1.0.0",
        migration_head="alpha-1",
        migrations_package="tigrbl_test_alpha.migrations.versions",
        objects=(
            DatabaseObject(
                "tigrbl.test.storage.alpha.table.records", "table", "alpha_records"
            ),
        ),
    )


def create_table(connection) -> None:
    connection.execute("CREATE TABLE alpha_records (id INTEGER PRIMARY KEY)")


def drop_table(connection) -> None:
    connection.execute("DROP TABLE alpha_records")


def orchestrator(connection: sqlite3.Connection, *, reversible: bool = True):
    manifest = storage()
    migration = Migration(
        revision="alpha-1",
        component=manifest.component_id,
        kind=MigrationKind.STANDARD,
        reversible=reversible,
        upgrade=create_table,
        downgrade=drop_table if reversible else None,
    )
    return MigrationOrchestrator(
        composition=StorageComposition.from_manifests(manifest),
        migrations=(migration,),
        ledger=MigrationLedger(connection),
        artifact_versions={manifest.component_id: "1.0.0"},
    )


def test_fresh_apply_records_head_and_ownership() -> None:
    connection = sqlite3.connect(":memory:")
    runner = orchestrator(connection)
    plan = runner.apply()
    assert [item.revision for item in plan.ordered] == ["alpha-1"]
    assert connection.execute(
        "SELECT owner_component_id FROM tigrbl_schema_ownership"
    ).fetchone() == ("tigrbl.test.storage.alpha",)
    assert runner.plan().ordered == ()


def test_forward_only_requires_acknowledgement() -> None:
    connection = sqlite3.connect(":memory:")
    runner = orchestrator(connection, reversible=False)
    with pytest.raises(MigrationError, match="acknowledgement"):
        runner.apply()
    runner.apply(acknowledge_forward_only=True)


def test_deployment_lock_is_deterministic() -> None:
    manifest = storage()
    composition = StorageComposition.from_manifests(manifest)
    lock = DeploymentLock.from_composition(
        composition, artifact_versions={manifest.component_id: "1.0.0"}
    )
    expected = DeploymentLock.from_composition(
        composition, artifact_versions={manifest.component_id: "1.0.0"}
    )
    assert lock.to_toml() == expected.to_toml()
    parsed = DeploymentLock.from_text(lock.to_toml())
    assert parsed == lock
    parsed.verify(composition, artifact_versions={manifest.component_id: "1.0.0"})


def test_transfer_prevalidation_prevents_partial_ownership_change() -> None:
    connection = sqlite3.connect(":memory:")
    ledger = MigrationLedger(connection)
    ledger.bootstrap()
    ledger.claim_objects(storage(), revision="alpha-1")
    with pytest.raises(OwnershipError):
        ledger.transfer_objects(
            (
                "tigrbl.test.storage.alpha.table.records",
                "tigrbl.test.storage.alpha.table.missing",
            ),
            source="tigrbl.test.storage.alpha",
            destination="tigrbl.test.storage.beta",
            revision="transfer-1",
        )
    assert connection.execute(
        "SELECT owner_component_id FROM tigrbl_schema_ownership"
    ).fetchone() == ("tigrbl.test.storage.alpha",)
