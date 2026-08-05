from __future__ import annotations

from dataclasses import replace

import pytest

from tigrbl_migrations import DatabaseObject, ManifestError, SchemaRequirement, StorageManifest


def manifest(component: str = "tigrbl.test.storage.alpha") -> StorageManifest:
    return StorageManifest(
        manifest_version="1.0.0",
        component_id=component,
        distribution="tigrbl-test-alpha",
        import_root="tigrbl_test_alpha",
        schema_contract="1.2.0",
        migration_head="alpha-1",
        migrations_package="tigrbl_test_alpha.migrations.versions",
        objects=(
            DatabaseObject(
                id=f"{component}.table.records",
                kind="table",
                physical_name="test.alpha_records",
                model="tigrbl_test_alpha.tables:Record",
            ),
        ),
    )


def test_manifest_toml_round_trip_preserves_digest() -> None:
    source = """
manifest_version = "1.0.0"
[component]
id = "tigrbl.test.storage.alpha"
distribution = "tigrbl-test-alpha"
import_root = "tigrbl_test_alpha"
[schema]
contract = "1.2.0"
migration_head = "alpha-1"
migrations_package = "tigrbl_test_alpha.migrations.versions"
[[schema.objects]]
id = "tigrbl.test.storage.alpha.table.records"
kind = "table"
physical_name = "test.alpha_records"
model = "tigrbl_test_alpha.tables:Record"
"""
    parsed = StorageManifest.from_text(source)
    assert parsed == manifest()
    assert parsed.digest() == manifest().digest()
    assert StorageManifest.from_text(parsed.to_toml()) == parsed
    assert StorageManifest.from_text(parsed.to_toml()).digest() == parsed.digest()


@pytest.mark.parametrize("value", ["1", "1.0", "v1.0.0", "1.0.0.dev1"])
def test_schema_contract_requires_semver(value: str) -> None:
    with pytest.raises(ManifestError):
        replace(manifest(), schema_contract=value)


def test_requirement_uses_contract_range() -> None:
    requirement = SchemaRequirement(
        component="tigrbl.test.storage.base",
        contract=">=1.1.0,<2.0.0",
        minimum_revision="base-1",
    )
    assert requirement.accepts("1.9.0")
    assert not requirement.accepts("2.0.0")
