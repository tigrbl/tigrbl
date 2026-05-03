from __future__ import annotations

import json
from collections.abc import Mapping as ABCMapping
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from time import perf_counter
from typing import Any, Callable

import pytest

from tigrbl_runtime.executors.types import HotCtx, _HotTemp

RESULTS_PATH = Path(__file__).with_name("runtime_hotstate_microbench.json")
ITERATIONS = 2_000_000
SAMPLE_COUNT = 7


@dataclass(slots=True)
class _ConcreteHotFields:
    route_payload: dict[str, Any] | None = None
    path_params: dict[str, Any] | None = None
    program_id: int = -1
    selector: str = ""
    protocol: str = ""


def _concrete_hotctx_payload_name(state: _ConcreteHotFields) -> Any:
    payload = state.route_payload
    if payload is None:
        return None
    return payload.get("name")


def _prenormalized_namespace_payload_name(route: Any) -> Any:
    payload = route.get("payload")
    return payload.get("name")


def _abcmapping_temp_payload_name(temp: Any) -> Any:
    if isinstance(temp, ABCMapping):
        hot = temp.get("hot_ctx")
        if isinstance(hot, HotCtx):
            payload = hot.in_values_view
            if isinstance(payload, dict):
                return payload.get("name")
    return None


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
def test_runtime_hotstate_microbench() -> None:
    payload = {"name": "Ada", "id": 7}
    path_params = {"item_id": "7"}

    concrete = _ConcreteHotFields(
        route_payload=payload,
        path_params=path_params,
        program_id=7,
        selector="/ws/echo",
        protocol="ws",
    )

    hot = HotCtx(
        program_id=7,
        selector="/ws/echo",
        protocol="ws",
        in_values_view=payload,
        path_params=path_params,
    )
    temp = _HotTemp.from_mapping(
        {
            "hot_ctx": hot,
            "route": {
                "payload": payload,
                "path_params": path_params,
                "program_id": 7,
                "selector": "/ws/echo",
                "protocol": "ws",
            },
        }
    )
    route = temp["route"]

    results = [
        _benchmark(
            title="runtime_hotstate.concrete_hotctx_dict_none_field",
            iterations=ITERATIONS,
            samples=SAMPLE_COUNT,
            func=lambda: _concrete_hotctx_payload_name(concrete),
        ),
        _benchmark(
            title="runtime_hotstate.prenormalized_hottemp_namespace",
            iterations=ITERATIONS,
            samples=SAMPLE_COUNT,
            func=lambda: _prenormalized_namespace_payload_name(route),
        ),
        _benchmark(
            title="runtime_hotstate.abcmapping_temp_check",
            iterations=ITERATIONS,
            samples=SAMPLE_COUNT,
            func=lambda: _abcmapping_temp_payload_name(temp),
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
    assert (
        ops["runtime_hotstate.concrete_hotctx_dict_none_field"]
        > ops["runtime_hotstate.abcmapping_temp_check"]
    )
    assert (
        ops["runtime_hotstate.prenormalized_hottemp_namespace"]
        > ops["runtime_hotstate.abcmapping_temp_check"]
    )
