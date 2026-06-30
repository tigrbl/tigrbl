from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


def _tuple_values(segment: Mapping[str, Any], key: str) -> tuple[Any, ...]:
    value = segment.get(key, ())
    if value is None:
        return ()
    return tuple(value)


def _barrier(segment: Mapping[str, Any]) -> bool:
    return bool(segment.get("barrier")) or str(segment.get("barrier_kind", "")) in {
        "transaction",
        "transport",
        "error",
        "completion",
    }


def fuse_protocol_segments(
    segments: Iterable[Mapping[str, Any]],
    *,
    force: bool = False,
) -> list[dict[str, object]]:
    items = [dict(segment) for segment in segments]
    if force and sum(1 for segment in items if _barrier(segment)) > 1:
        raise ValueError("protocol segment fusion cannot cross transaction, transport, or error barriers")

    fused: list[dict[str, object]] = []
    bucket: list[dict[str, Any]] = []

    def flush() -> None:
        nonlocal bucket
        if not bucket:
            return
        if len(bucket) == 1:
            item = dict(bucket[0])
            if "err_target" in item:
                item["err_targets"] = (item["err_target"],)
            fused.append(item)
        else:
            merged: dict[str, object] = {
                "segment_id": "+".join(str(item["segment_id"]) for item in bucket),
                "source_segments": tuple(str(item["segment_id"]) for item in bucket),
                "anchors": tuple(anchor for item in bucket for anchor in _tuple_values(item, "anchors")),
            }
            atoms = tuple(atom for item in bucket for atom in _tuple_values(item, "atoms"))
            if atoms:
                merged["atoms"] = atoms
            err_targets = tuple(item["err_target"] for item in bucket if "err_target" in item)
            if err_targets:
                merged["err_targets"] = err_targets
            fused.append(merged)
        bucket = []

    for segment in items:
        if _barrier(segment):
            flush()
            fused.append(segment)
        else:
            bucket.append(segment)
    flush()
    return fused


def linearize_segment_anchors(segments: Iterable[Mapping[str, Any]]) -> tuple[Any, ...]:
    return tuple(anchor for segment in segments for anchor in _tuple_values(segment, "anchors"))


__all__ = ["fuse_protocol_segments", "linearize_segment_anchors"]
