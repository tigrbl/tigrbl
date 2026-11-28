"""Reusable primary keys for ORM tables."""

from __future__ import annotations

import re
from secrets import randbits
from time import time_ns

from sqlalchemy import String, TypeDecorator
from sqlalchemy.orm import validates

from tigrbl.specs import ColumnSpec, F, IO, S, acol
from tigrbl.types import PgUUID, UUID, declarative_mixin, uuid4, Mapped
from tigrbl_core._spec.datatypes import DataTypeSpec
from tigrbl_core.schema.materialize import validated_type

from .utils import RO_IO, uuid_example


_ULID_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
_ULID_PATTERN = rf"^[0-7][{_ULID_ALPHABET}]{{25}}$"
_FINGERPRINT_PATTERN = r"^(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$"
_Fingerprint = validated_type(
    str,
    str.lower,
    strict=True,
    min_length=17,
    max_length=17,
    pattern=_FINGERPRINT_PATTERN,
)


def _new_ulid() -> str:
    timestamp_ms = time_ns() // 1_000_000
    value = (timestamp_ms << 80) | randbits(80)
    return "".join(
        _ULID_ALPHABET[(value >> shift) & 31] for shift in range(125, -1, -5)
    )


def _new_uuid7() -> UUID:
    timestamp_ms = time_ns() // 1_000_000
    # RFC 9562 §5.7: 48-bit time, version, 12 random bits, variant, 62 random bits.
    return UUID(
        int=(timestamp_ms << 80)
        | (7 << 76)
        | (randbits(12) << 64)
        | (2 << 62)
        | randbits(62)
    )


def _validate_uuid7(value: UUID | str) -> UUID:
    if isinstance(value, str):
        value = UUID(value)
    if not isinstance(value, UUID) or value.version != 7:
        raise ValueError("Expected an RFC 9562 UUID version 7")
    return value


class _UUID7Type(TypeDecorator[UUID]):
    impl = PgUUID
    cache_ok = True

    @property
    def python_type(self) -> type[UUID]:
        return UUID

    def process_bind_param(self, value: UUID | str | None, dialect) -> UUID | None:
        return None if value is None else _validate_uuid7(value)


class _ULIDString(TypeDecorator[str]):
    impl = String(26)
    cache_ok = True

    @property
    def python_type(self) -> type[str]:
        return str

    def process_bind_param(self, value: str | None, dialect) -> str | None:
        if value is not None and (
            not isinstance(value, str) or re.fullmatch(_ULID_PATTERN, value) is None
        ):
            raise ValueError("Expected a canonical 26-character uppercase ULID")
        return value


def _normalize_fingerprint(value: str) -> str:
    if not isinstance(value, str) or re.fullmatch(_FINGERPRINT_PATTERN, value) is None:
        raise ValueError("Expected six colon-separated hexadecimal byte pairs")
    return value.lower()


class _FingerprintString(TypeDecorator[str]):
    impl = String(17)
    cache_ok = True

    @property
    def python_type(self) -> type[str]:
        return str

    def process_bind_param(self, value: str | None, dialect) -> str | None:
        return None if value is None else _normalize_fingerprint(value)


@declarative_mixin
class GUIDPk:
    """Universal surrogate primary key."""

    id: Mapped[UUID] = acol(
        spec=ColumnSpec(
            storage=S(
                type_=PgUUID(as_uuid=True),
                primary_key=True,
                default=uuid4,
            ),
            field=F(py_type=UUID, constraints={"examples": [uuid_example]}),
            io=RO_IO,
        )
    )


@declarative_mixin
class UUID7Pk:
    """Add a UUIDv7 primary key generated on insert."""

    id: Mapped[UUID] = acol(
        spec=ColumnSpec(
            storage=S(
                type_=_UUID7Type(),
                primary_key=True,
                nullable=False,
                default=_new_uuid7,
            ),
            field=F(
                py_type=validated_type(
                    UUID, _validate_uuid7, json_schema_extra={"format": "uuid7"}
                ),
                constraints={"examples": ["017f22e2-79b0-7cc3-98c4-dc0c0c07398f"]},
            ),
            io=RO_IO,
            datatype=DataTypeSpec(logical_name="uuid"),
        )
    )


@declarative_mixin
class ULIDPk:
    """Add a canonical ULID string primary key, generated on insert."""

    id: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(
                type_=_ULIDString(),
                primary_key=True,
                nullable=False,
                default=_new_ulid,
            ),
            field=F(
                py_type=str,
                constraints={
                    "min_length": 26,
                    "max_length": 26,
                    "pattern": _ULID_PATTERN,
                },
            ),
            io=RO_IO,
            datatype=DataTypeSpec(logical_name="ulid"),
        )
    )


@declarative_mixin
class FingerprintPk:
    """Add a caller-supplied, lowercase six-byte fingerprint primary key."""

    id: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(
                type_=_FingerprintString(),
                primary_key=True,
                nullable=False,
                autoincrement=False,
            ),
            field=F(
                py_type=_Fingerprint, constraints={"examples": ["7c:db:98:04:14:f5"]}
            ),
            io=IO(
                in_verbs=("create",),
                out_verbs=RO_IO.out_verbs,
                mutable_verbs=("create",),
            ),
        )
    )

    @validates("id")
    def _validate_fingerprint(self, _key: str, value: str) -> str:
        return _normalize_fingerprint(value)


__all__ = ["GUIDPk", "UUID7Pk", "ULIDPk", "FingerprintPk"]
