from __future__ import annotations

import json
from collections.abc import Mapping as ABCMapping
from pathlib import Path
from statistics import mean
from time import perf_counter
from typing import Any, Callable, Mapping

import pytest

RESULTS_PATH = Path(__file__).with_name("runtime_typecheck_microbench.json")
ITERATIONS = 2_000_000
SAMPLE_COUNT = 7


def _dict_check_get(payload: dict[str, Any]) -> Any:
    if isinstance(payload, dict):
        return payload.get("program_id")
    return None


def _abc_mapping_check_get(payload: dict[str, Any]) -> Any:
    if isinstance(payload, ABCMapping):
        return payload.get("program_id")
    return None


def _typing_mapping_check_get(payload: dict[str, Any]) -> Any:
    if isinstance(payload, Mapping):
        return payload.get("program_id")
    return None


def _no_check_get(payload: dict[str, Any]) -> Any:
    return payload.get("program_id")


def _attr_no_check(obj: Any) -> Any:
    return obj.program_id


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


@pytest.mark.perf
def test_runtime_typecheck_microbench() -> None:
    payload = {
        "program_id": 7,
        "selector": "POST /items",
        "binding_protocol": "http.rest",
    }

    class _Payload:
        __slots__ = ("program_id",)

        def __init__(self, program_id: int) -> None:
            self.program_id = program_id

    payload_obj = _Payload(7)

    results = [
        _benchmark(
            title="runtime_check.dict_get",
            iterations=ITERATIONS,
            samples=SAMPLE_COUNT,
            func=lambda: _dict_check_get(payload),
        ),
        _benchmark(
            title="runtime_check.abc_mapping_get",
            iterations=ITERATIONS,
            samples=SAMPLE_COUNT,
            func=lambda: _abc_mapping_check_get(payload),
        ),
        _benchmark(
            title="runtime_check.typing_mapping_get",
            iterations=ITERATIONS,
            samples=SAMPLE_COUNT,
            func=lambda: _typing_mapping_check_get(payload),
        ),
        _benchmark(
            title="runtime_check.no_check_dict_get",
            iterations=ITERATIONS,
            samples=SAMPLE_COUNT,
            func=lambda: _no_check_get(payload),
        ),
        _benchmark(
            title="runtime_check.no_check_attr",
            iterations=ITERATIONS,
            samples=SAMPLE_COUNT,
            func=lambda: _attr_no_check(payload_obj),
        ),
    ]

    artifact = {
        "iterations": ITERATIONS,
        "samples": SAMPLE_COUNT,
        "results": results,
        "artifact_path": str(RESULTS_PATH),
    }
    RESULTS_PATH.write_text(json.dumps(artifact, indent=2), encoding="utf-8")

    assert RESULTS_PATH.exists()
    ops = {result["title"]: result["ops_per_second"] for result in results}
    assert all(value > 0 for value in ops.values())
    assert ops["runtime_check.no_check_dict_get"] > ops["runtime_check.typing_mapping_get"]
    assert ops["runtime_check.dict_get"] > ops["runtime_check.typing_mapping_get"]
    assert ops["runtime_check.no_check_attr"] > ops["runtime_check.typing_mapping_get"]
