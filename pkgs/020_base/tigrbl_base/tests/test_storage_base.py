from dataclasses import FrozenInstanceError

import pytest

from tigrbl_base._base._storage import ForeignKeyBase, StorageTransformBase
from tigrbl_core._spec.storage_spec import ForeignKeySpec, StorageTransformSpec


def test_foreign_key_base_inheritance_and_fields() -> None:
    fk = ForeignKeyBase(target="users(id)", on_delete="CASCADE")

    assert isinstance(fk, ForeignKeySpec)
    assert fk.target == "users(id)"
    assert fk.on_delete == "CASCADE"


def test_foreign_key_base_is_immutable() -> None:
    fk = ForeignKeyBase(target="users(id)")

    with pytest.raises(FrozenInstanceError):
        fk.target = "groups(id)"  # type: ignore[misc]


def test_storage_transform_base_preserves_transform_callables() -> None:
    def to_stored(value: str, ctx: dict) -> str:
        return value.lower()

    def from_stored(value: str, ctx: dict) -> str:
        return value.upper()

    transform = StorageTransformBase(to_stored=to_stored, from_stored=from_stored)

    assert isinstance(transform, StorageTransformSpec)
    assert transform.to_stored is to_stored
    assert transform.from_stored is from_stored
