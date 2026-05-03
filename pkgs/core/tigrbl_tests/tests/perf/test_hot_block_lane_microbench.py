from __future__ import annotations

import json
from pathlib import Path
from statistics import mean
from time import perf_counter
from typing import Any, Callable

import pytest

RESULTS_PATH = Path(__file__).with_name("hot_block_lane_microbench.json")
SAMPLE_COUNT = 5
COUNT_ITERATIONS = 50_000
FIND_ITERATIONS = 30_000
TRANSLATE_ITERATIONS = 20_000
LANE_SIZE = 4096
PUT = 0x02
DELETE = 0x04


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


def _count_tuple_scan(values: tuple[int, ...], marker: int) -> int:
    total = 0
    for value in values:
        total += value == marker
    return total


def _find_tuple_scan(values: tuple[int, ...], marker: int) -> int:
    for index, value in enumerate(values):
        if value == marker:
            return index
    return -1


def _translate_tuple_scan(values: tuple[int, ...], table: bytes) -> int:
    total = 0
    for value in values:
        total += table[value] == 1
    return total


@pytest.mark.perf
def test_hot_block_lane_microbench() -> None:
    lane = bytes(
        PUT if idx % 7 == 0 else DELETE if idx % 13 == 0 else 0
        for idx in range(LANE_SIZE)
    )
    tuple_values = tuple(lane)
    first_delete = lane.find(bytes([DELETE]))
    assert first_delete >= 0

    live_table = bytes(
        1 if value in {PUT, DELETE} else 0 for value in range(256)
    )

    results = [
        _benchmark(
            title="u8.count.byte_lane",
            iterations=COUNT_ITERATIONS,
            samples=SAMPLE_COUNT,
            func=lambda: lane.count(PUT),
        ),
        _benchmark(
            title="u8.count.tuple_scan",
            iterations=COUNT_ITERATIONS,
            samples=SAMPLE_COUNT,
            func=lambda: _count_tuple_scan(tuple_values, PUT),
        ),
        _benchmark(
            title="u8.find.byte_lane",
            iterations=FIND_ITERATIONS,
            samples=SAMPLE_COUNT,
            func=lambda: lane.find(bytes([DELETE])),
        ),
        _benchmark(
            title="u8.find.tuple_scan",
            iterations=FIND_ITERATIONS,
            samples=SAMPLE_COUNT,
            func=lambda: _find_tuple_scan(tuple_values, DELETE),
        ),
        _benchmark(
            title="u8.translate_count.byte_lane",
            iterations=TRANSLATE_ITERATIONS,
            samples=SAMPLE_COUNT,
            func=lambda: lane.translate(live_table).count(1),
        ),
        _benchmark(
            title="u8.translate_count.tuple_scan",
            iterations=TRANSLATE_ITERATIONS,
            samples=SAMPLE_COUNT,
            func=lambda: _translate_tuple_scan(tuple_values, live_table),
        ),
    ]

    payload = {
        "lane_size": LANE_SIZE,
        "count_iterations": COUNT_ITERATIONS,
        "find_iterations": FIND_ITERATIONS,
        "translate_iterations": TRANSLATE_ITERATIONS,
        "samples": SAMPLE_COUNT,
        "first_delete_index": first_delete,
        "results": results,
        "artifact_path": str(RESULTS_PATH),
    }
    RESULTS_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    ops = {result["title"]: result["ops_per_second"] for result in results}
    assert ops["u8.count.byte_lane"] > ops["u8.count.tuple_scan"]
    assert ops["u8.find.byte_lane"] > ops["u8.find.tuple_scan"]
    assert (
        ops["u8.translate_count.byte_lane"]
        > ops["u8.translate_count.tuple_scan"]
    )
