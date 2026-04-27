from __future__ import annotations

from tigrbl_core._spec.monotone import (
    highest_precedence,
    merge_mro_mapping_attr,
    merge_mro_sequence_attr,
    stable_keyed_overlay,
)


def test_highest_precedence_preserves_lower_value_when_override_is_unset() -> None:
    merged = highest_precedence("base", None)
    merged = highest_precedence(merged, "leaf")

    assert merged == "leaf"
    assert highest_precedence(highest_precedence("base", None), None) == "base"


def test_highest_precedence_supports_empty_sequence_as_unset() -> None:
    merged = highest_precedence(("base",), (), is_set=bool)
    merged = highest_precedence(merged, ("leaf",), is_set=bool)

    assert highest_precedence(("base",), (), is_set=bool) == ("base",)
    assert merged == ("leaf",)


def test_stable_keyed_overlay_keeps_original_position_with_latest_value() -> None:
    merged = stable_keyed_overlay(
        [
            {"name": "auth", "phase": "base"},
            {"name": "audit", "phase": "base"},
            {"name": "auth", "phase": "leaf"},
        ],
        key=lambda item: item["name"],
    )

    assert merged == (
        {"name": "auth", "phase": "leaf"},
        {"name": "audit", "phase": "base"},
    )


def test_mro_mapping_rollup_uses_leaf_precedence_without_dropping_base_keys() -> None:
    class Base:
        settings = {"engine": "sqlite", "timeout": 30, "trace": False}

    class Middle(Base):
        settings = {"timeout": 10}

    class Leaf(Middle):
        settings = {"engine": "postgres"}

    assert merge_mro_mapping_attr(Leaf, "settings") == {
        "engine": "postgres",
        "timeout": 10,
        "trace": False,
    }


def test_mro_sequence_rollup_is_stable_for_diamond_inheritance() -> None:
    class Base:
        hooks = ("base",)

    class Left(Base):
        hooks = ("left", "shared")

    class Right(Base):
        hooks = ("right", "shared")

    class Leaf(Left, Right):
        hooks = ("leaf", "shared")

    assert merge_mro_sequence_attr(Leaf, "hooks") == (
        "leaf",
        "shared",
        "left",
        "right",
        "base",
    )
    assert merge_mro_sequence_attr(Leaf, "hooks", reverse=True) == (
        "base",
        "right",
        "shared",
        "left",
        "leaf",
    )
