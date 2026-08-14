"""Portable SQL ledger for component migrations and database-object ownership."""

from __future__ import annotations

import datetime as dt
import uuid
from dataclasses import dataclass
from typing import Any, Iterable

from .errors import LedgerError, LockError, OwnershipError
from .manifests import StorageManifest
from .migration import Migration

DDL = (
    """CREATE TABLE IF NOT EXISTS tigrbl_schema_components (
        component_id VARCHAR(255) PRIMARY KEY,
        artifact_version VARCHAR(64) NOT NULL,
        manifest_version VARCHAR(64) NOT NULL,
        schema_contract VARCHAR(64) NOT NULL,
        migration_head VARCHAR(255) NOT NULL,
        manifest_digest VARCHAR(80) NOT NULL,
        updated_at VARCHAR(64) NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS tigrbl_schema_migrations (
        component_id VARCHAR(255) NOT NULL,
        revision VARCHAR(255) NOT NULL,
        migration_checksum VARCHAR(64) NOT NULL,
        migration_kind VARCHAR(32) NOT NULL,
        application_mode VARCHAR(32) NOT NULL,
        artifact_version VARCHAR(64) NOT NULL,
        execution_id VARCHAR(64) NOT NULL,
        applied_at VARCHAR(64) NOT NULL,
        PRIMARY KEY (component_id, revision)
    )""",
    """CREATE TABLE IF NOT EXISTS tigrbl_schema_ownership (
        object_id VARCHAR(255) PRIMARY KEY,
        physical_name VARCHAR(255) NOT NULL UNIQUE,
        owner_component_id VARCHAR(255) NOT NULL,
        acquired_by_revision VARCHAR(255) NOT NULL,
        ownership_state VARCHAR(32) NOT NULL,
        updated_at VARCHAR(64) NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS tigrbl_schema_execution_lock (
        lock_name VARCHAR(64) PRIMARY KEY,
        execution_id VARCHAR(64) NOT NULL,
        acquired_at VARCHAR(64) NOT NULL
    )""",
)


def _execute(connection: Any, sql: str, params: Any = None) -> Any:
    if hasattr(connection, "exec_driver_sql"):
        values = tuple(params or ())
        paramstyle = getattr(getattr(connection, "dialect", None), "paramstyle", "qmark")
        if values and paramstyle in {"format", "pyformat"}:
            sql = sql.replace("?", "%s")
        elif values and paramstyle in {"numeric", "numeric_dollar"}:
            prefix = "$" if paramstyle == "numeric_dollar" else ":"
            for index in range(1, len(values) + 1):
                sql = sql.replace("?", f"{prefix}{index}", 1)
        return connection.exec_driver_sql(sql, values)
    if params is None:
        return connection.execute(sql)
    return connection.execute(sql, params)


def _rows(result: Any) -> list[Any]:
    if hasattr(result, "fetchall"):
        return list(result.fetchall())
    return list(result)


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


@dataclass(slots=True)
class MigrationLedger:
    connection: Any

    def bootstrap(self) -> None:
        for ddl in DDL:
            _execute(self.connection, ddl)

    def applied_revisions(self) -> set[str]:
        self.bootstrap()
        result = _execute(self.connection, "SELECT revision FROM tigrbl_schema_migrations")
        return {str(row[0]) for row in _rows(result)}

    def recorded_checksum(self, *, component: str, revision: str) -> str | None:
        result = _execute(
            self.connection,
            "SELECT migration_checksum FROM tigrbl_schema_migrations "
            "WHERE component_id = ? AND revision = ?",
            (component, revision),
        )
        rows = _rows(result)
        return str(rows[0][0]) if rows else None

    def record_migration(
        self,
        migration: Migration,
        *,
        artifact_version: str,
        execution_id: str,
        application_mode: str = "executed",
    ) -> None:
        if application_mode not in {"executed", "adopted", "transferred"}:
            raise LedgerError(f"invalid migration application mode: {application_mode}")
        checksum = migration.checksum()
        prior = self.recorded_checksum(component=migration.component, revision=migration.revision)
        if prior is not None:
            if prior != checksum:
                raise LedgerError(
                    f"migration {migration.revision} checksum differs from the ledger"
                )
            return
        _execute(
            self.connection,
            "INSERT INTO tigrbl_schema_migrations "
            "(component_id, revision, migration_checksum, migration_kind, application_mode, "
            "artifact_version, execution_id, applied_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                migration.component,
                migration.revision,
                checksum,
                migration.kind.value,
                application_mode,
                artifact_version,
                execution_id,
                _now(),
            ),
        )

    def record_component(self, manifest: StorageManifest, *, artifact_version: str) -> None:
        existing = _rows(
            _execute(
                self.connection,
                "SELECT component_id FROM tigrbl_schema_components WHERE component_id = ?",
                (manifest.component_id,),
            )
        )
        params = (
            artifact_version,
            manifest.manifest_version,
            manifest.schema_contract,
            manifest.migration_head,
            manifest.digest(),
            _now(),
            manifest.component_id,
        )
        if existing:
            _execute(
                self.connection,
                "UPDATE tigrbl_schema_components SET artifact_version = ?, manifest_version = ?, "
                "schema_contract = ?, migration_head = ?, manifest_digest = ?, updated_at = ? "
                "WHERE component_id = ?",
                params,
            )
        else:
            _execute(
                self.connection,
                "INSERT INTO tigrbl_schema_components "
                "(artifact_version, manifest_version, schema_contract, migration_head, "
                "manifest_digest, updated_at, component_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                params,
            )

    def claim_objects(
        self,
        manifest: StorageManifest,
        *,
        revision: str,
        state: str = "active",
    ) -> None:
        for item in manifest.objects:
            rows = _rows(
                _execute(
                    self.connection,
                    "SELECT owner_component_id FROM tigrbl_schema_ownership WHERE object_id = ?",
                    (item.id,),
                )
            )
            if rows and str(rows[0][0]) != manifest.component_id:
                raise OwnershipError(
                    f"database object {item.id} is already owned by {rows[0][0]}"
                )
            if not rows:
                _execute(
                    self.connection,
                    "INSERT INTO tigrbl_schema_ownership "
                    "(object_id, physical_name, owner_component_id, acquired_by_revision, "
                    "ownership_state, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        item.id,
                        item.physical_name,
                        manifest.component_id,
                        revision,
                        state,
                        _now(),
                    ),
                )

    def transfer_objects(
        self,
        object_ids: Iterable[str],
        *,
        source: str,
        destination: str,
        revision: str,
    ) -> None:
        object_ids = tuple(object_ids)
        for object_id in object_ids:
            rows = _rows(
                _execute(
                    self.connection,
                    "SELECT owner_component_id FROM tigrbl_schema_ownership WHERE object_id = ?",
                    (object_id,),
                )
            )
            if not rows or str(rows[0][0]) != source:
                raise OwnershipError(f"{source} does not own database object {object_id}")
        for object_id in object_ids:
            _execute(
                self.connection,
                "UPDATE tigrbl_schema_ownership SET owner_component_id = ?, "
                "acquired_by_revision = ?, ownership_state = 'active', updated_at = ? "
                "WHERE object_id = ? AND owner_component_id = ?",
                (destination, revision, _now(), object_id, source),
            )

    def acquire_lock(self, execution_id: str | None = None) -> str:
        execution_id = execution_id or str(uuid.uuid4())
        try:
            _execute(
                self.connection,
                "INSERT INTO tigrbl_schema_execution_lock "
                "(lock_name, execution_id, acquired_at) VALUES ('migration', ?, ?)",
                (execution_id, _now()),
            )
        except Exception as exc:
            raise LockError("another migration execution owns the database lock") from exc
        return execution_id

    def release_lock(self, execution_id: str) -> None:
        _execute(
            self.connection,
            "DELETE FROM tigrbl_schema_execution_lock "
            "WHERE lock_name = 'migration' AND execution_id = ?",
            (execution_id,),
        )
