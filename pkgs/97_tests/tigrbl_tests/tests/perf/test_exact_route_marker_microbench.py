from __future__ import annotations

import json
import struct
from pathlib import Path
from statistics import mean
from time import perf_counter
from typing import Any, Callable

import pytest

from tigrbl_kernel.models import PackedHotSection

RESULTS_PATH = Path(__file__).with_name("exact_route_marker_microbench.json")
SAMPLE_COUNT = 5
ITERATIONS = 75_000
METHOD_COUNT = 4
ROUTES_PER_METHOD = 512
TARGET_METHOD_ID = 2
TARGET_LOCAL_INDEX = 448


def _benchmark(
    *,
    title: str,
    iterations: int,
    samples: int,
    func: Callable[[], Any],
) -> dict[str, Any]:
    sample_times: list[float] = []
    func()
    for _ in range(samples):
        start = perf_counter()
        for _ in range(iterations):
            func()
        elapsed = perf_counter() - start
        sample_times.append(elapsed)
    mean_seconds = mean(sample_times)
    return {
        "title": title,
        "iterations": iterations,
        "samples": samples,
        "mean_seconds": mean_seconds,
        "ops_per_second": iterations / mean_seconds if mean_seconds else 0.0,
        "mean_ns_per_op": (mean_seconds / iterations) * 1_000_000_000
        if iterations
        else 0.0,
        "sample_seconds": sample_times,
    }


def _bucket_scan(bucket: tuple[tuple[int, int], ...], target_hash: int) -> int:
    for index, (candidate_hash, _) in enumerate(bucket):
        if candidate_hash == target_hash:
            return index
    return -1


@pytest.mark.perf
def test_exact_route_marker_microbench() -> None:
    bucket: list[tuple[int, int]] = []
    hashes: list[int] = []
    for method_id in range(METHOD_COUNT):
        for local_index in range(ROUTES_PER_METHOD):
            route_hash = (method_id << 40) | (local_index << 8) | method_id
            hashes.append(route_hash)
            if method_id == TARGET_METHOD_ID:
                bucket.append((route_hash, local_index))
    target_hash = bucket[TARGET_LOCAL_INDEX][0]

    hash_payload = b"".join(
        struct.pack("<Q", value) for value in hashes
    )
    section = PackedHotSection(
        name="exact_path_hashes",
        section_id=0,
        width_bits=64,
        count=len(hashes),
        offset=0,
        byte_length=len(hash_payload),
        buffer=hash_payload,
        signed=False,
    )
    start_index = TARGET_METHOD_ID * ROUTES_PER_METHOD

    results = [
        _benchmark(
            title="exact_route.marker_search.raw_lane",
            iterations=ITERATIONS,
            samples=SAMPLE_COUNT,
            func=lambda: section.find_aligned_u64(
                target_hash,
                start_index=start_index,
                count=ROUTES_PER_METHOD,
            ),
        ),
        _benchmark(
            title="exact_route.marker_search.python_bucket_scan",
            iterations=ITERATIONS,
            samples=SAMPLE_COUNT,
            func=lambda: _bucket_scan(tuple(bucket), target_hash),
        ),
    ]

    payload = {
        "iterations": ITERATIONS,
        "samples": SAMPLE_COUNT,
        "method_count": METHOD_COUNT,
        "routes_per_method": ROUTES_PER_METHOD,
        "target_method_id": TARGET_METHOD_ID,
        "target_local_index": TARGET_LOCAL_INDEX,
        "artifact_path": str(RESULTS_PATH),
        "results": results,
    }
    RESULTS_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    raw_index = section.find_aligned_u64(
        target_hash,
        start_index=start_index,
        count=ROUTES_PER_METHOD,
    )
    bucket_index = _bucket_scan(tuple(bucket), target_hash)
    assert raw_index == start_index + TARGET_LOCAL_INDEX
    assert bucket_index == TARGET_LOCAL_INDEX

    ops = {result["title"]: result["ops_per_second"] for result in results}
    assert (
        ops["exact_route.marker_search.raw_lane"]
        > ops["exact_route.marker_search.python_bucket_scan"]
    )
