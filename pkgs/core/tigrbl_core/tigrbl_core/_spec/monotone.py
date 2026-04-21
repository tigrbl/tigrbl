from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import Any, TypeVar

K = TypeVar("K")
T = TypeVar("T")
V = TypeVar("V")


def as_tuple(value: Any) -> tuple[Any, ...]:
    """Normalize sequence-like inputs while treating scalars as one item."""

    if value is None:
        return ()
    if isinstance(value, tuple):
        return value
    if isinstance(value, (str, bytes, bytearray)):
        return (value,)
    if isinstance(value, Mapping):
        return (value,)
    if isinstance(value, Iterable):
        return tuple(value)
    return (value,)


def highest_precedence(
    inherited: T,
    override: T,
    *,
    is_set: Callable[[T], bool] | None = None,
) -> T:
    """Return the override value when it is set, otherwise keep inherited."""

    predicate = is_set or (lambda value: value is not None)
    return override if predicate(override) else inherited


def stable_unique(
    values: Iterable[T],
    *,
    key: Callable[[T], K] | None = None,
) -> tuple[T, ...]:
    """Return values in first-seen order with stable de-duplication."""

    out: list[T] = []
    seen_hashable: set[Any] = set()
    for item in values:
        identity = key(item) if key is not None else item
        try:
            if identity in seen_hashable:
                continue
            seen_hashable.add(identity)
        except TypeError:
            if any(
                (key(existing) if key is not None else existing) == identity
                for existing in out
            ):
                continue
        out.append(item)
    return tuple(out)


def sequence_union(
    *sequences: Iterable[T] | T | None,
    key: Callable[[T], K] | None = None,
    dedupe: bool = True,
) -> tuple[T, ...]:
    """Concatenate sequence-like values and optionally de-duplicate stably."""

    values: list[T] = []
    for sequence in sequences:
        values.extend(as_tuple(sequence))
    if not dedupe:
        return tuple(values)
    return stable_unique(values, key=key)


def mapping_overlay(
    *mappings: Mapping[K, V] | None,
) -> dict[K, V]:
    """Shallow-merge mappings by key; later mappings have higher precedence."""

    merged: dict[K, V] = {}
    for mapping in mappings:
        if mapping:
            merged.update(mapping)
    return merged


def keyed_overlay(
    *items: Iterable[T],
    key: Callable[[T], K],
) -> dict[K, T]:
    """Build a keyed map where later items replace earlier items for a key."""

    merged: dict[K, T] = {}
    for group in items:
        for item in group:
            merged[key(item)] = item
    return merged


def stable_keyed_overlay(
    values: Iterable[T],
    *,
    key: Callable[[T], K],
) -> tuple[T, ...]:
    """De-duplicate by key while preserving first key position and latest value."""

    by_key: dict[K, T] = {}
    order: list[K] = []
    for item in values:
        identity = key(item)
        if identity not in by_key:
            order.append(identity)
        by_key[identity] = item
    return tuple(by_key[identity] for identity in order)


def merge_mro_sequence_attr(
    owner: type,
    attr: str,
    *,
    include_inherited: bool = False,
    reverse: bool = False,
    dedupe: bool = True,
    key: Callable[[Any], Any] | None = None,
) -> tuple[Any, ...]:
    """Roll up a sequence-like class attribute over an MRO."""

    mro = reversed(owner.__mro__) if reverse else owner.__mro__
    values: list[Any] = []
    for base in mro:
        if include_inherited:
            if not hasattr(base, attr):
                continue
            seq = getattr(base, attr) or ()
        else:
            seq = base.__dict__.get(attr, ()) or ()
        values.extend(as_tuple(seq))
    if not dedupe:
        return tuple(values)
    return stable_unique(values, key=key)


def merge_mro_mapping_attr(owner: type, attr: str) -> dict[Any, Any]:
    """Roll up mapping-like class attributes over an MRO with subclass precedence."""

    merged: dict[Any, Any] = {}
    for base in reversed(owner.__mro__):
        value = getattr(base, attr, None)
        if isinstance(value, Mapping):
            merged.update(value)
    return merged
