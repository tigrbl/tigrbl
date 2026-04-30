from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


_HARD_BARRIERS = {
    "deps",
    "tx",
    "rollback",
    "handler",
    "transport.accept",
    "transport.emit",
    "transport.close",
    "completion_fence",
}


def fuse_segments(
    segments: Iterable[Mapping[str, Any]],
    *,
    force: bool = False,
) -> list[dict[str, object]]:
    items = [dict(segment) for segment in segments]
    if force and any(str(segment.get("class")) in _HARD_BARRIERS for segment in items):
        raise ValueError("segment fusion cannot cross a hard barrier")

    fused: list[dict[str, object]] = []
    bucket: list[dict[str, Any]] = []

    def _flush() -> None:
        nonlocal bucket
        if not bucket:
            return
        if len(bucket) == 1:
            fused.append(bucket[0])
        else:
            fused.append(
                {
                    "segment_id": "+".join(str(item["segment_id"]) for item in bucket),
                    "class": str(bucket[0].get("class", "pure_fused")),
                    "atoms": tuple(
                        atom
                        for item in bucket
                        for atom in tuple(item.get("atoms", ()))
                    ),
                }
            )
        bucket = []

    for segment in items:
        segment_class = str(segment.get("class", ""))
        if segment_class in _HARD_BARRIERS:
            _flush()
            fused.append(segment)
            continue
        bucket.append(segment)

    _flush()
    return fused


__all__ = ["fuse_segments"]
