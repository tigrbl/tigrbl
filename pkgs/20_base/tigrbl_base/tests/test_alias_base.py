from dataclasses import FrozenInstanceError

import pytest

from tigrbl_base._base._alias_base import AliasBase
from tigrbl_core._spec.alias_spec import AliasSpec


def test_alias_base_inheritance_and_properties() -> None:
    alias = AliasBase(
        _alias="create_user",
        _request_schema="Req",
        _response_schema="Res",
        _persist="always",
        _arity="one",
        _rest=True,
    )

    assert isinstance(alias, AliasSpec)
    assert alias.alias == "create_user"
    assert alias.request_schema == "Req"
    assert alias.response_schema == "Res"
    assert alias.persist == "always"
    assert alias.arity == "one"
    assert alias.rest is True


def test_alias_base_is_immutable_after_construction() -> None:
    alias = AliasBase(_alias="read_user")

    with pytest.raises(FrozenInstanceError):
        alias._alias = "delete_user"  # type: ignore[misc]

    assert alias.alias == "read_user"


def test_alias_base_preserves_optional_none_contract() -> None:
    alias = AliasBase(_alias="list_users")

    assert alias.request_schema is None
    assert alias.response_schema is None
    assert alias.persist is None
    assert alias.arity is None
    assert alias.rest is None
