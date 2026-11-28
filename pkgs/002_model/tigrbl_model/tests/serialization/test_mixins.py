from __future__ import annotations

import json
from dataclasses import dataclass

import pytest
import yaml

from tigrbl_model import (
    Field,
    JsonMixin,
    Model,
    SerdeMixin,
    TomlMixin,
    ValidationError,
    YamlMixin,
)


class Credentials(Model):
    username: str
    api_key: str | None = None


class Settings(Model):
    name: str
    credentials: Credentials
    labels: list[str] = Field(default_factory=list)
    note: str | None = None


def test_json_round_trip_supports_string_bytes_and_bytearray() -> None:
    value = Settings(name="demo", credentials={"username": "ada"})
    encoded = value.model_dump_json(exclude_none=True)

    assert json.loads(encoded)["credentials"] == {"username": "ada"}
    assert Settings.model_validate_json(encoded) == value
    assert Settings.model_validate_json(encoded.encode()) == value
    assert Settings.model_validate_json(bytearray(encoded, "utf-8")) == value


def test_invalid_json_is_a_structured_validation_error() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Settings.model_validate_json("{")
    assert exc_info.value.errors(include_url=False)[0]["type"] == "json_invalid"


def test_yaml_round_trip_uses_safe_mapping_documents() -> None:
    value = Settings(name="demo", credentials={"username": "ada"})
    encoded = value.model_dump_yaml(exclude_none=True)

    assert yaml.safe_load(encoded)["name"] == "demo"
    assert Settings.model_validate_yaml(encoded) == value
    with pytest.raises(ValidationError):
        Settings.model_validate_yaml("- not\n- a\n- mapping")


def test_toml_round_trip_omits_unrepresentable_nulls() -> None:
    value = Settings(name="demo", credentials={"username": "ada"}, note=None)
    encoded = value.model_dump_toml()

    assert "note" not in encoded
    assert Settings.model_validate_toml(encoded) == value


def test_dump_filtering_matches_model_contract() -> None:
    value = Settings(
        name="demo",
        credentials={"username": "ada", "api_key": "secret"},
        labels=["one"],
    )

    assert value.model_dump(include={"name"}) == {"name": "demo"}
    assert value.model_dump(exclude={"credentials": {"api_key"}}) == {
        "name": "demo",
        "credentials": {"username": "ada"},
        "labels": ["one"],
        "note": None,
    }
    assert value.model_dump(exclude_none=True)["credentials"] == {
        "username": "ada",
        "api_key": "secret",
    }
    assert value.model_dump(exclude_unset=True) == {
        "name": "demo",
        "credentials": {"username": "ada", "api_key": "secret"},
        "labels": ["one"],
    }


@dataclass
class DataclassDocument(SerdeMixin):
    name: str
    count: int = 0


def test_serde_mixin_supports_plain_dataclasses() -> None:
    value = DataclassDocument("demo", 2)
    assert value.to_dict() == {"name": "demo", "count": 2}
    assert DataclassDocument.from_json(value.to_json()) == value
    assert DataclassDocument.from_yaml(value.to_yaml()) == value
    assert DataclassDocument.from_toml(value.to_toml()) == value


def test_serde_mixin_aggregates_the_three_format_mixins() -> None:
    assert issubclass(SerdeMixin, JsonMixin)
    assert issubclass(SerdeMixin, YamlMixin)
    assert issubclass(SerdeMixin, TomlMixin)
