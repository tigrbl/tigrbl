from __future__ import annotations

import copy
from typing import Any

from tigrbl_spec.schema import CURRENT_SCHEMA_VERSION, UnsupportedSchemaVersionError, schema_versions

SUPPORTED_SCHEMA_VERSIONS = schema_versions()


class SchemaMigrationError(ValueError):
    """Raised when no valid schema catalog migration path exists."""


def migration_path(
    from_version: str,
    to_version: str = CURRENT_SCHEMA_VERSION,
) -> tuple[str, ...]:
    if from_version not in SUPPORTED_SCHEMA_VERSIONS:
        raise UnsupportedSchemaVersionError(f"Unsupported source schema version {from_version!r}")
    if to_version not in SUPPORTED_SCHEMA_VERSIONS:
        raise UnsupportedSchemaVersionError(f"Unsupported target schema version {to_version!r}")
    if from_version == to_version:
        return (from_version,)
    versions = list(SUPPORTED_SCHEMA_VERSIONS)
    start = versions.index(from_version)
    end = versions.index(to_version)
    if end < start:
        raise SchemaMigrationError(
            f"Downgrade migrations are not supported: {from_version!r} -> {to_version!r}"
        )
    path = tuple(versions[start : end + 1])
    if len(path) < 2:
        raise SchemaMigrationError(f"No migration path from {from_version!r} to {to_version!r}")
    return path


def migrate_payload(
    spec_kind: str,
    payload: dict[str, Any],
    from_version: str,
    to_version: str = CURRENT_SCHEMA_VERSION,
) -> dict[str, Any]:
    path = migration_path(from_version, to_version)
    migrated = copy.deepcopy(payload)
    if len(path) == 1:
        return migrated
    raise SchemaMigrationError(
        f"No adjacent migration implementation registered for {spec_kind!r}: "
        f"{from_version!r} -> {to_version!r}"
    )
