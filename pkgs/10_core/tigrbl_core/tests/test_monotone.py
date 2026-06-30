from __future__ import annotations

from tigrbl_core._spec.monotone import (
    as_tuple,
    highest_precedence,
    keyed_overlay,
    mapping_overlay,
    merge_mro_mapping_attr,
    merge_mro_sequence_attr,
    sequence_union,
    stable_keyed_overlay,
    stable_unique,
)


def test_as_tuple_treats_scalars_and_mappings_as_single_items() -> None:
    payload = {"k": "v"}

    assert as_tuple(None) == ()
    assert as_tuple("tag") == ("tag",)
    assert as_tuple(payload) == (payload,)
    assert as_tuple(["a", "b"]) == ("a", "b")


def test_highest_precedence_uses_non_none_by_default() -> None:
    assert highest_precedence("base", None) == "base"
    assert highest_precedence("base", "override") == "override"


def test_highest_precedence_accepts_custom_set_predicate() -> None:
    assert highest_precedence(("base",), (), is_set=bool) == ("base",)
    assert highest_precedence(("base",), ("override",), is_set=bool) == (
        "override",
    )


def test_stable_unique_dedupes_hashable_and_unhashable_values() -> None:
    assert stable_unique(["a", "b", "a"]) == ("a", "b")
    assert stable_unique([{"k": "v"}, {"k": "v"}, {"k": "w"}]) == (
        {"k": "v"},
        {"k": "w"},
    )


def test_sequence_union_concatenates_and_dedupes_by_key() -> None:
    assert sequence_union(["a", "b"], ["b", "c"]) == ("a", "b", "c")
    assert sequence_union(
        [{"id": 1, "v": "a"}],
        [{"id": 1, "v": "b"}, {"id": 2, "v": "c"}],
        key=lambda item: item["id"],
    ) == ({"id": 1, "v": "a"}, {"id": 2, "v": "c"})


def test_mapping_overlay_and_keyed_overlay_use_later_precedence() -> None:
    assert mapping_overlay({"a": 1, "b": 1}, {"b": 2, "c": 2}) == {
        "a": 1,
        "b": 2,
        "c": 2,
    }
    assert keyed_overlay(
        [{"name": "a", "v": 1}],
        [{"name": "a", "v": 2}, {"name": "b", "v": 3}],
        key=lambda item: item["name"],
    ) == {
        "a": {"name": "a", "v": 2},
        "b": {"name": "b", "v": 3},
    }


def test_stable_keyed_overlay_keeps_first_position_and_latest_value() -> None:
    assert stable_keyed_overlay(
        [{"name": "a", "v": 1}, {"name": "b", "v": 2}, {"name": "a", "v": 3}],
        key=lambda item: item["name"],
    ) == ({"name": "a", "v": 3}, {"name": "b", "v": 2})


def test_mro_sequence_and_mapping_rollups_are_domain_agnostic() -> None:
    class Base:
        values = ("base", "shared")
        settings = {"engine": "base", "shared": "base"}

    class Leaf(Base):
        values = ("leaf", "shared")
        settings = {"engine": "leaf"}

    assert merge_mro_sequence_attr(Leaf, "values") == ("leaf", "shared", "base")
    assert merge_mro_sequence_attr(Leaf, "values", reverse=True) == (
        "base",
        "shared",
        "leaf",
    )
    assert merge_mro_mapping_attr(Leaf, "settings") == {
        "engine": "leaf",
        "shared": "base",
    }

