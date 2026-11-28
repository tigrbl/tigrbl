from __future__ import annotations

import pytest

from tigrbl_spec import CURRENT_SCHEMA_VERSION
from tigrbl_spec.migrations import SchemaMigrationError, migrate_payload, migration_path
from tigrbl_spec.schema import UnsupportedSchemaVersionError
from .helpers import app_payload


def test_current_identity_migration_returns_equal_payload_copy() -> None:
    payload = app_payload()
    migrated = migrate_payload("AppSpec", payload, CURRENT_SCHEMA_VERSION, CURRENT_SCHEMA_VERSION)

    assert migrated == payload
    assert migrated is not payload
    assert migration_path(CURRENT_SCHEMA_VERSION, CURRENT_SCHEMA_VERSION) == (CURRENT_SCHEMA_VERSION,)


def test_missing_or_unsupported_migration_raises_clear_error() -> None:
    with pytest.raises(UnsupportedSchemaVersionError, match="0.3.19"):
        migration_path("0.3.19", CURRENT_SCHEMA_VERSION)

    with pytest.raises(SchemaMigrationError, match="Downgrade"):
        raise SchemaMigrationError("Downgrade migrations are not supported")
