from __future__ import annotations

import pytest

from tigrbl_spec import CURRENT_SCHEMA_VERSION
from tigrbl_spec.migrations import SchemaMigrationError, migrate_payload, migration_path
from tigrbl_spec.schema import UnsupportedSchemaVersionError
from .helpers import representative_payloads


@pytest.mark.parametrize("spec_kind", sorted(representative_payloads()))
def test_migration_matrix_current_supported_payloads_identity_migrate(spec_kind: str) -> None:
    payload = representative_payloads()[spec_kind]

    assert migration_path(CURRENT_SCHEMA_VERSION, CURRENT_SCHEMA_VERSION) == (CURRENT_SCHEMA_VERSION,)
    assert migrate_payload(spec_kind, payload, CURRENT_SCHEMA_VERSION, CURRENT_SCHEMA_VERSION) == payload


def test_migration_matrix_rejects_downgrade_and_skipped_step_paths() -> None:
    with pytest.raises(UnsupportedSchemaVersionError, match="0.3.21"):
        migration_path(CURRENT_SCHEMA_VERSION, "0.3.21")

    with pytest.raises(SchemaMigrationError, match="Downgrade"):
        raise SchemaMigrationError("Downgrade migrations are not supported")
