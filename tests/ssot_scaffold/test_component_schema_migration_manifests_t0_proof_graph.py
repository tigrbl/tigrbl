from tigrbl_migrations import DatabaseObject, StorageManifest


def test_manifest_protocol_round_trip_and_stable_object_identity():
    manifest = StorageManifest(
        manifest_version="1.0.0",
        component_id="tigrbl.test.storage.records",
        distribution="tigrbl-test-storage-records",
        import_root="tigrbl_test_storage_records",
        schema_contract="1.0.0",
        migration_head="record-1",
        migrations_package="tigrbl_test_storage_records.migrations.versions",
        objects=(
            DatabaseObject(
                "tigrbl.test.storage.records:table:records",
                "table",
                "test.records",
            ),
        ),
    )
    assert StorageManifest.from_text(manifest.to_toml()) == manifest
    assert StorageManifest.from_text(manifest.to_toml()).digest() == manifest.digest()
