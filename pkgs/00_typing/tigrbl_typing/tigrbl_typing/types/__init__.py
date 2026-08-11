# ── Standard Library ─────────────────────────────────────────────────────
from importlib.metadata import version as distribution_version
from types import MethodType, SimpleNamespace
from uuid import uuid4, UUID
import warnings

# ── Third-party Dependencies (via deps module) ───────────────────────────
from ..vendor.sqlalchemy import (
    # Core SQLAlchemy
    Boolean,
    Column as _SQLAlchemyColumn,
    _DateTime,
    Float,
    SAEnum,
    Text,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    String,
    LargeBinary,
    UniqueConstraint,
    CheckConstraint,
    create_engine,
    event,
    # PostgreSQL dialect
    ARRAY,
    PgEnum,
    JSONB,
    TSVECTOR,
    # ORM
    Mapped as _SQLAlchemyMapped,
    declarative_mixin,
    declared_attr,
    foreign,
    mapped_column as _sqlalchemy_mapped_column,
    relationship,
    remote,
    column_property,
    Session,
    sessionmaker,
    InstrumentedAttribute,
    # Extensions
    MutableDict,
    MutableList,
    hybrid_property,
    StaticPool,
    TypeDecorator,
)


from ..vendor.pydantic import (
    BaseModel,
    Field,
    ValidationError,
)

from ..status.exceptions import StatusDetailError

# ── Local Package ─────────────────────────────────────────────────────────
from .channel import OpChannel, OpChannelFamily, OpChannelKind, OpChannelSubevent
from .op import _Op, _SchemaVerb
from .uuid import PgUUID, SqliteUUID
from .authn_abc import AuthNProvider

# ── Generics / Extensions ─────────────────────────────────────────────────
DateTime = _DateTime(timezone=False)
TZDateTime = _DateTime(timezone=True)


DEPRECATED_EXPORTS_CUTOFF = (0, 7)

_DEPRECATED_EXPORTS = {
    "Column": _SQLAlchemyColumn,
    "Mapped": _SQLAlchemyMapped,
    "mapped_column": _sqlalchemy_mapped_column,
}
_DEPRECATED_EXPORTS_MESSAGE = (
    "{name} is deprecated in tigrbl_typing.types and will no longer be exported "
    "starting with tigrbl-typing 0.7. Import Column from 'tigrbl_concrete', or "
    "use 'tigrbl_concrete.factories.makeColumn', 'makeVirtualColumn', 'acol', or "
    "'vcol'. For SQLAlchemy declarative typing, import Mapped and mapped_column "
    "from 'sqlalchemy.orm'."
)


def _major_minor(value: str) -> tuple[int, int]:
    release = value.split("+", 1)[0].split(".dev", 1)[0]
    major, minor, *_ = release.split(".")
    return int(major), int(minor)


def _deprecated_export_names_for(
    current_major_minor: tuple[int, int],
) -> list[str]:
    if current_major_minor >= DEPRECATED_EXPORTS_CUTOFF:
        return []
    return list(_DEPRECATED_EXPORTS)


_CURRENT_MAJOR_MINOR = _major_minor(distribution_version("tigrbl-typing"))


# ── Public Re-exports (Backwards Compatibility) ──────────────────────────
__all__: list[str] = [
    # local
    "_Op",
    "_SchemaVerb",
    "AuthNProvider",
    "OpChannel",
    "OpChannelFamily",
    "OpChannelKind",
    "OpChannelSubevent",
    # add ons
    "SqliteUUID",
    # builtin types
    "MethodType",
    "SimpleNamespace",
    "uuid4",
    "UUID",
    # sqlalchemy core (from deps.sqlalchemy)
    "Boolean",
    "DateTime",
    "TZDateTime",
    "Float",
    "Text",
    "SAEnum",
    "ForeignKey",
    "Index",
    "Integer",
    "JSON",
    "Numeric",
    "String",
    "LargeBinary",
    "UniqueConstraint",
    "CheckConstraint",
    "create_engine",
    "event",
    # sqlalchemy.dialects.postgresql (from deps.sqlalchemy)
    "ARRAY",
    "PgEnum",
    "JSONB",
    "PgUUID",
    "TSVECTOR",
    # sqlalchemy.orm (from deps.sqlalchemy)
    "declarative_mixin",
    "declared_attr",
    "foreign",
    "column_property",
    "hybrid_property",
    "relationship",
    "remote",
    "Session",
    "sessionmaker",
    "InstrumentedAttribute",
    # sqlalchemy.ext.mutable (from deps.sqlalchemy)
    "MutableDict",
    "MutableList",
    "StaticPool",
    "TypeDecorator",
    # pydantic schema support (from deps.pydantic)
    "BaseModel",
    "Field",
    "ValidationError",
    # status
    "StatusDetailError",
]

__all__.extend(_deprecated_export_names_for(_CURRENT_MAJOR_MINOR))


def __getattr__(name: str):
    value = _DEPRECATED_EXPORTS.get(name)
    if value is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    if _CURRENT_MAJOR_MINOR >= DEPRECATED_EXPORTS_CUTOFF:
        raise AttributeError(
            f"{name} is no longer exported by tigrbl_typing.types as of "
            "tigrbl-typing 0.7. " + _DEPRECATED_EXPORTS_MESSAGE.format(name=name)
        )
    warnings.warn(
        _DEPRECATED_EXPORTS_MESSAGE.format(name=name),
        DeprecationWarning,
        stacklevel=2,
    )
    return value
