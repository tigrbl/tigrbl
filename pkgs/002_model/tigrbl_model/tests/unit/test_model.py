from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal
from uuid import UUID

import pytest

from tigrbl_model import (
    AliasChoices,
    ConfigDict,
    Field,
    Model,
    ValidationError,
    field_validator,
    model_validator,
)


class Color(str, Enum):
    RED = "red"
    BLUE = "blue"


class Address(Model):
    city: str
    postal_code: str = Field(pattern=r"^\d{5}$")


class User(Model):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: UUID
    name: str = Field(min_length=2, max_length=20)
    age: int = Field(default=0, ge=0, lt=150)
    address: Address | None = None
    tags: list[str] = Field(default_factory=list, max_length=3)
    color: Color = Color.RED
    role: Literal["user", "admin"] = "user"
    created_at: datetime | None = None


def test_validation_coerces_supported_tigrbl_types() -> None:
    user = User.model_validate(
        {
            "id": "1d4b4bb0-8dc7-4d2c-b749-8a52ec6e2938",
            "name": "Ada",
            "age": "37",
            "address": {"city": "Austin", "postal_code": "78701"},
            "tags": ("maintainer",),
            "color": "blue",
            "created_at": "2026-07-16T12:00:00",
        }
    )

    assert user.age == 37
    assert user.address == Address(city="Austin", postal_code="78701")
    assert user.tags == ["maintainer"]
    assert user.color is Color.BLUE
    assert user.created_at == datetime(2026, 7, 16, 12)


def test_strict_validation_rejects_integer_strings() -> None:
    with pytest.raises(ValidationError) as exc_info:
        User.model_validate(
            {"id": UUID(int=0), "name": "Ada", "age": "37"}, strict=True
        )

    assert exc_info.value.errors(include_url=False)[0]["loc"] == ("age",)


@pytest.mark.parametrize(
    ("payload", "location"),
    [
        ({"id": UUID(int=0)}, ("name",)),
        ({"id": UUID(int=0), "name": "A"}, ("name",)),
        ({"id": UUID(int=0), "name": "Ada", "age": -1}, ("age",)),
        (
            {
                "id": UUID(int=0),
                "name": "Ada",
                "address": {"city": "Austin", "postal_code": "invalid"},
            },
            ("address", "postal_code"),
        ),
    ],
)
def test_validation_reports_stable_nested_locations(payload, location) -> None:
    with pytest.raises(ValidationError) as exc_info:
        User.model_validate(payload)

    assert location in {tuple(item["loc"]) for item in exc_info.value.errors()}


def test_extra_forbid_and_extra_allow() -> None:
    with pytest.raises(ValidationError) as exc_info:
        User(id=UUID(int=0), name="Ada", unknown=True)
    assert exc_info.value.errors(include_url=False)[0]["type"] == "extra_forbidden"

    class Extensible(Model):
        model_config = ConfigDict(extra="allow")
        name: str

    value = Extensible(name="Ada", extension=True)
    assert value.extension is True
    assert value.model_extra == {"extension": True}
    assert value.model_dump() == {"name": "Ada", "extension": True}


def test_alias_choices_and_serialization_alias() -> None:
    class Aliased(Model):
        value: int = Field(
            validation_alias=AliasChoices("value", "legacy_value"),
            serialization_alias="wire_value",
        )

    value = Aliased.model_validate({"legacy_value": "3"})
    assert value.value == 3
    assert value.model_dump(by_alias=True) == {"wire_value": 3}


def test_field_and_model_validators() -> None:
    class Validated(Model):
        left: int
        right: int

        @field_validator("left", mode="before")
        @classmethod
        def normalize_left(cls, value):
            return int(value) + 1

        @model_validator(mode="after")
        def ordered(self):
            if self.left >= self.right:
                raise ValueError("left must be less than right")
            return self

    assert Validated(left="1", right=3).left == 2
    with pytest.raises(ValidationError, match="left must be less than right"):
        Validated(left=3, right=3)


def test_removed_pydantic_field_keywords_fail_closed() -> None:
    from tigrbl_model import ModelUserError

    with pytest.raises(ModelUserError, match="regex.*removed"):
        Field(regex="^[A-Z]+$")
    with pytest.raises(ModelUserError, match="unique_items.*removed"):
        Field(unique_items=True)


def test_model_construct_bypasses_validation_and_tracks_fields() -> None:
    user = User.model_construct(id="not-a-uuid", name=42)
    assert user.id == "not-a-uuid"
    assert user.name == 42
    assert user.model_fields_set == {"id", "name"}
    assert User.model_fields["name"].is_required()
    assert not User.model_fields["age"].is_required()


def test_model_copy_updates_without_revalidation() -> None:
    original = User(id=UUID(int=0), name="Ada")
    copied = original.model_copy(update={"age": 41})
    assert copied.age == 41
    assert original.age == 0
    assert "age" in copied.model_fields_set
