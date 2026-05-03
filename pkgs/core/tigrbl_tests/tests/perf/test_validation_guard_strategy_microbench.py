from __future__ import annotations

import json
from pathlib import Path
from statistics import mean
from time import perf_counter
from typing import Any, Callable

import pytest

RESULTS_PATH = Path(__file__).with_name("validation_guard_strategy_microbench.json")
SAMPLE_COUNT = 5
ITERATIONS = 250_000
FIELD_COUNT = 16


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


def _field_plan_loop(
    field_plans: tuple[dict[str, Any], ...], slot_present: bytearray
) -> bool:
    for plan in field_plans:
        slot_id = int(plan["slot_id"])
        if not plan["in_enabled"]:
            continue
        if plan["required"] and not slot_present[slot_id]:
            return False
    return True


def _required_index_loop(required_indices: tuple[int, ...], slot_present: bytearray) -> bool:
    for slot_id in required_indices:
        if not slot_present[slot_id]:
            return False
    return True


@pytest.mark.perf
def test_validation_guard_strategy_microbench() -> None:
    field_plans = tuple(
        {
            "slot_id": idx,
            "required": True,
            "in_enabled": True,
            "nullable": False,
            "default_factory": None,
        }
        for idx in range(FIELD_COUNT)
    )
    required_indices = tuple(range(FIELD_COUNT))
    slot_present = bytearray([1] * FIELD_COUNT)
    full_mask = bytes([1] * FIELD_COUNT)

    results = [
        _benchmark(
            title="validation_guard.field_plan_loop",
            iterations=ITERATIONS,
            samples=SAMPLE_COUNT,
            func=lambda: _field_plan_loop(field_plans, slot_present),
        ),
        _benchmark(
            title="validation_guard.required_index_loop",
            iterations=ITERATIONS,
            samples=SAMPLE_COUNT,
            func=lambda: _required_index_loop(required_indices, slot_present),
        ),
        _benchmark(
            title="validation_guard.bytes_equality",
            iterations=ITERATIONS,
            samples=SAMPLE_COUNT,
            func=lambda: bytes(slot_present) == full_mask,
        ),
    ]

    payload = {
        "field_count": FIELD_COUNT,
        "iterations": ITERATIONS,
        "samples": SAMPLE_COUNT,
        "artifact_path": str(RESULTS_PATH),
        "results": results,
    }
    RESULTS_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    ops = {result["title"]: result["ops_per_second"] for result in results}
    assert (
        ops["validation_guard.bytes_equality"]
        > ops["validation_guard.required_index_loop"]
        > ops["validation_guard.field_plan_loop"]
    )
