from __future__ import annotations

import json
from pathlib import Path
from statistics import mean
from time import perf_counter
from typing import Any, Callable

import pytest

from tigrbl_atoms.atoms.egress.asgi_send import _coerce_body_bytes

RESULTS_PATH = Path(__file__).with_name("egress_body_coercion_microbench.json")
SAMPLE_COUNT = 5
ITERATIONS = 500_000
PAYLOAD = b"abcdef0123456789" * 4


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
def test_egress_body_coercion_microbench() -> None:
    payload_bytes = PAYLOAD
    payload_bytearray = bytearray(PAYLOAD)
    payload_memoryview = memoryview(PAYLOAD)

    results = [
        _benchmark(
            title="egress_body.direct_bytes_passthrough",
            iterations=ITERATIONS,
            samples=SAMPLE_COUNT,
            func=lambda: payload_bytes,
        ),
        _benchmark(
            title="egress_body.coerce_bytes",
            iterations=ITERATIONS,
            samples=SAMPLE_COUNT,
            func=lambda: _coerce_body_bytes(payload_bytes),
        ),
        _benchmark(
            title="egress_body.coerce_bytearray",
            iterations=ITERATIONS,
            samples=SAMPLE_COUNT,
            func=lambda: _coerce_body_bytes(payload_bytearray),
        ),
        _benchmark(
            title="egress_body.coerce_memoryview",
            iterations=ITERATIONS,
            samples=SAMPLE_COUNT,
            func=lambda: _coerce_body_bytes(payload_memoryview),
        ),
    ]

    payload = {
        "payload_size": len(PAYLOAD),
        "iterations": ITERATIONS,
        "samples": SAMPLE_COUNT,
        "artifact_path": str(RESULTS_PATH),
        "results": results,
    }
    RESULTS_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    ops = {result["title"]: result["ops_per_second"] for result in results}
    assert (
        ops["egress_body.direct_bytes_passthrough"]
        > ops["egress_body.coerce_bytes"]
        > ops["egress_body.coerce_bytearray"]
    )
    assert (
        ops["egress_body.direct_bytes_passthrough"]
        > ops["egress_body.coerce_memoryview"]
    )
