from __future__ import annotations

import pytest

from tigrbl_base._base import AttrDict


def test_attrdict_attribute_and_item_access_stay_equivalent() -> None:
    data = AttrDict({"name": "alice"})

    assert data.name == data["name"]
    data.status = "active"
    assert data["status"] == "active"
    data["role"] = "admin"
    assert data.role == "admin"


def test_attrdict_missing_attribute_and_delete_fail_like_attributes() -> None:
    data = AttrDict({"name": "alice"})

    with pytest.raises(AttributeError):
        _ = data.missing

    del data.name
    assert "name" not in data
    with pytest.raises(AttributeError):
        del data.name


def test_attrdict_preserves_dict_method_names_and_mapping_semantics() -> None:
    data = AttrDict({"items": "value", "copy": "shadow"})

    assert callable(data.items)
    assert data["items"] == "value"

    copied = data.copy()
    assert isinstance(copied, dict)
    assert copied == {"items": "value", "copy": "shadow"}

    data.update({"extra": 1})
    assert data.extra == 1
