from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from time import perf_counter
from typing import Any, Callable

import pytest

from tigrbl_runtime.executors.types import _HotTemp

RESULTS_PATH = Path(__file__).with_name("runtime_namespace_dictget_microbench.json")
ITERATIONS = 2_000_000
SAMPLE_COUNT = 7


@dataclass(slots=True)
class _SlotBackedHotState:
    route_protocol: str
    route_selector: str
    program_id: int
    egress_sent: bool
    _route_view: dict[str, Any] | None = None
    _dispatch_view: dict[str, Any] | None = None
    _egress_view: dict[str, Any] | None = None

    def route_view(self) -> dict[str, Any]:
        route = self._route_view
        if route is None:
            route = {
                "protocol": self.route_protocol,
                "selector": self.route_selector,
            }
            self._route_view = route
        return route

    def dispatch_view(self) -> dict[str, Any]:
        dispatch = self._dispatch_view
        if dispatch is None:
            dispatch = {"program_id": self.program_id}
            self._dispatch_view = dispatch
        return dispatch

    def egress_view(self) -> dict[str, Any]:
        egress = self._egress_view
        if egress is None:
            egress = {"sent": self.egress_sent}
            self._egress_view = egress
        return egress

    def clear_views(self) -> None:
        self._route_view = None
        self._dispatch_view = None
        self._egress_view = None


def _repeated_temp_get_namespace(temp: _HotTemp) -> tuple[Any, Any, Any, Any]:
    route = temp.get("route", {})
    dispatch = temp.get("dispatch", {})
    egress = temp.get("egress", {})
    return (
        route.get("protocol"),
        route.get("selector"),
        dispatch.get("program_id"),
        egress.get("sent"),
    )


def _slot_backed_attrs(hot: _SlotBackedHotState) -> tuple[Any, Any, Any, Any]:
    return (
        hot.route_protocol,
        hot.route_selector,
        hot.program_id,
        hot.egress_sent,
    )


def _slot_backed_cached_compat_views(hot: _SlotBackedHotState) -> tuple[Any, Any, Any, Any]:
    route = hot.route_view()
    dispatch = hot.dispatch_view()
    egress = hot.egress_view()
    return (
        route.get("protocol"),
        route.get("selector"),
        dispatch.get("program_id"),
        egress.get("sent"),
    )


def _slot_backed_cold_publish_views(hot: _SlotBackedHotState) -> tuple[Any, Any, Any, Any]:
    hot.clear_views()
    route = hot.route_view()
    dispatch = hot.dispatch_view()
    egress = hot.egress_view()
    return (
        route.get("protocol"),
        route.get("selector"),
        dispatch.get("program_id"),
        egress.get("sent"),
    )


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
def test_runtime_namespace_dictget_microbench() -> None:
    temp = _HotTemp.from_mapping(
        {
            "route": {
                "protocol": "ws",
                "selector": "/ws/echo",
            },
            "dispatch": {
                "program_id": 7,
            },
            "egress": {
                "sent": False,
            },
        }
    )
    hot = _SlotBackedHotState(
        route_protocol="ws",
        route_selector="/ws/echo",
        program_id=7,
        egress_sent=False,
    )

    hot.route_view()
    hot.dispatch_view()
    hot.egress_view()

    results = [
        _benchmark(
            title="runtime_namespace.repeated_temp_get_namespace",
            iterations=ITERATIONS,
            samples=SAMPLE_COUNT,
            func=lambda: _repeated_temp_get_namespace(temp),
        ),
        _benchmark(
            title="runtime_namespace.slot_backed_attrs",
            iterations=ITERATIONS,
            samples=SAMPLE_COUNT,
            func=lambda: _slot_backed_attrs(hot),
        ),
        _benchmark(
            title="runtime_namespace.slot_backed_cached_compat_views",
            iterations=ITERATIONS,
            samples=SAMPLE_COUNT,
            func=lambda: _slot_backed_cached_compat_views(hot),
        ),
        _benchmark(
            title="runtime_namespace.slot_backed_cold_publish_views",
            iterations=ITERATIONS,
            samples=SAMPLE_COUNT,
            func=lambda: _slot_backed_cold_publish_views(hot),
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
    assert ops["runtime_namespace.slot_backed_attrs"] > ops[
        "runtime_namespace.repeated_temp_get_namespace"
    ]
    assert ops["runtime_namespace.slot_backed_attrs"] > ops[
        "runtime_namespace.slot_backed_cached_compat_views"
    ]
