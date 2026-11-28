"""ORM mixins for principal references."""

from __future__ import annotations

from tigrbl.specs import ColumnSpec, F, S, acol
from tigrbl._spec.storage_spec import ForeignKeySpec
from tigrbl.types import PgUUID, UUID, declarative_mixin, declared_attr, Mapped

# Keep the historical import paths for the key mixins.
from .primary_keys import GUIDPk, UUID7Pk, ULIDPk, FingerprintPk
from .utils import _infer_schema, uuid_example, CRUD_IO


@declarative_mixin
class TenantColumn:
    """Adds ``tenant_id`` with a schema-qualified FK to ``<schema>.tenants.id``."""

    @declared_attr
    def tenant_id(cls) -> Mapped[UUID]:
        schema = getattr(cls, "__tenant_table_schema__", None) or _infer_schema(cls)
        spec = ColumnSpec(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(target=f"{schema}.tenants.id"),
                nullable=False,
                index=True,
            ),
            field=F(py_type=UUID, constraints={"examples": [uuid_example]}),
            io=CRUD_IO,
        )
        return acol(spec=spec)


@declarative_mixin
class UserColumn:
    """Adds ``user_id`` with a schema-qualified FK to ``<schema>.users.id``."""

    @declared_attr
    def user_id(cls) -> Mapped[UUID]:
        schema = getattr(cls, "__user_table_schema__", None) or _infer_schema(cls)
        spec = ColumnSpec(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(target=f"{schema}.users.id"),
                nullable=False,
                index=True,
            ),
            field=F(py_type=UUID, constraints={"examples": [uuid_example]}),
            io=CRUD_IO,
        )
        return acol(spec=spec)


@declarative_mixin
class OrgColumn:
    """Adds ``org_id`` with a schema-qualified FK to ``<schema>.orgs.id``."""

    @declared_attr
    def org_id(cls) -> Mapped[UUID]:
        schema = getattr(cls, "__org_table_schema__", None) or _infer_schema(cls)
        spec = ColumnSpec(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(target=f"{schema}.orgs.id"),
                nullable=False,
                index=True,
            ),
            field=F(py_type=UUID, constraints={"examples": [uuid_example]}),
            io=CRUD_IO,
        )
        return acol(spec=spec)


@declarative_mixin
class Principal:
    __abstract__ = True


__all__ = [
    "GUIDPk",
    "UUID7Pk",
    "ULIDPk",
    "FingerprintPk",
    "TenantColumn",
    "UserColumn",
    "OrgColumn",
    "Principal",
]
