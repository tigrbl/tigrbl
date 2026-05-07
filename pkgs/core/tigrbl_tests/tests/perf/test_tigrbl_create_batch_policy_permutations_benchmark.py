from __future__ import annotations

import asyncio
import json
import logging
import random
from pathlib import Path
from statistics import mean, median, pstdev
from tempfile import TemporaryDirectory
from time import perf_counter
from typing import Any, Callable

import httpx
import pytest

from tests.i9n.uvicorn_utils import run_uvicorn_in_task, stop_uvicorn_server
from tests.perf.helper_tigrbl_create_app import (
    create_tigrbl_app,
    create_tigrbl_batch_app,
    dispose_tigrbl_app,
    fetch_tigrbl_names,
    initialize_tigrbl_app,
    tigrbl_create_path,
)

RESULTS_PATH = Path(__file__).with_name(
    "benchmark_results_tigrbl_create_batch_policy_permutations_15_rounds_2500_ops.json"
)
PERF_TEMP_ROOT = Path(__file__).resolve().parents[5] / ".tmp" / "pytest-perf"
ROUND_COUNT = 15
OPS_COUNT = 2500
CONCURRENCY = 25
PRE_MEASUREMENT_WAIT_SECONDS = 0.5

BATCH_POLICIES: tuple[dict[str, Any], ...] = (
    {
        "policy": "batch_size_25_expected_10",
        "max_size": 25,
        "expected_batch_count": 10,
        "max_delay_ms": 1,
    },
    {
        "policy": "batch_size_100_expected_25",
        "max_size": 100,
        "expected_batch_count": 25,
        "max_delay_ms": 1,
    },
)


def _ops_summary(values: list[float]) -> dict[str, float | int]:
    return {
        "min": min(values),
        "max": max(values),
        "mean": mean(values),
        "stddev": pstdev(values),
        "median": median(values),
    }


async def _post_one(
    client: httpx.AsyncClient,
    *,
    item_name: str,
) -> float:
    start = perf_counter()
    response = await client.post(tigrbl_create_path(), json={"name": item_name})
    elapsed = perf_counter() - start
    assert response.status_code in {200, 201}, response.text
    body = response.json()
    assert body["name"] == item_name
    return elapsed


async def _run_create_mode(
    *,
    mode: str,
    round_index: int,
    create_app: Callable[[Path], Any],
    concurrent: bool,
    policy_name: str,
) -> dict[str, Any]:
    PERF_TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    scenario = f"{policy_name}-{mode}"
    with TemporaryDirectory(dir=PERF_TEMP_ROOT, ignore_cleanup_errors=True) as tmpdir:
        db_path = Path(tmpdir) / f"{scenario}-{round_index}.sqlite3"
        measured_names = [
            f"{scenario}-{round_index}-{idx}" for idx in range(OPS_COUNT)
        ]

        start = perf_counter()
        app = create_app(db_path)
        await initialize_tigrbl_app(app)
        base_url, server, task = await run_uvicorn_in_task(app)
        first_start_seconds = perf_counter() - start
        op_durations: list[float] = []
        try:
            async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as client:
                await asyncio.sleep(PRE_MEASUREMENT_WAIT_SECONDS)
                execution_start = perf_counter()
                if concurrent:
                    semaphore = asyncio.Semaphore(CONCURRENCY)

                    async def _limited(item_name: str) -> float:
                        async with semaphore:
                            return await _post_one(client, item_name=item_name)

                    op_durations = await asyncio.gather(
                        *(_limited(item_name) for item_name in measured_names)
                    )
                else:
                    for item_name in measured_names:
                        op_durations.append(
                            await _post_one(client, item_name=item_name)
                        )
                execution_total_seconds = perf_counter() - execution_start

            persisted_names = fetch_tigrbl_names(db_path)
            assert sorted(persisted_names) == sorted(measured_names)
        finally:
            await stop_uvicorn_server(server, task)
            dispose_result = dispose_tigrbl_app(app)
            if hasattr(dispose_result, "__await__"):
                await dispose_result

    return {
        "policy": policy_name,
        "mode": mode,
        "scenario": scenario,
        "round": round_index,
        "ops": OPS_COUNT,
        "concurrency": CONCURRENCY if concurrent else 1,
        "first_start_seconds": first_start_seconds,
        "execution_total_seconds": execution_total_seconds,
        "ops_per_second": OPS_COUNT / execution_total_seconds,
        "time_per_op_seconds": {
            "min": min(op_durations),
            "mean": mean(op_durations),
            "max": max(op_durations),
        },
    }


async def _run_policy_benchmark(policy: dict[str, Any]) -> dict[str, Any]:
    policy_name = str(policy["policy"])
    max_size = int(policy["max_size"])
    max_delay_ms = int(policy["max_delay_ms"])
    modes: dict[str, dict[str, Any]] = {
        "scalar_sequential_create": {
            "create_app": create_tigrbl_app,
            "concurrent": False,
        },
        "scalar_concurrent_create": {
            "create_app": create_tigrbl_app,
            "concurrent": True,
        },
        "batch_sequential_create": {
            "create_app": lambda db_path: create_tigrbl_batch_app(
                db_path,
                max_size=max_size,
                max_delay_ms=max_delay_ms,
            ),
            "concurrent": False,
        },
        "batch_concurrent_create": {
            "create_app": lambda db_path: create_tigrbl_batch_app(
                db_path,
                max_size=max_size,
                max_delay_ms=max_delay_ms,
            ),
            "concurrent": True,
        },
    }
    order_rng = random.Random(f"20260507:{policy_name}")
    rounds: list[dict[str, Any]] = []
    steps: list[dict[str, Any]] = []
    per_mode_ops: dict[str, list[float]] = {mode: [] for mode in modes}

    for round_index in range(1, ROUND_COUNT + 1):
        order = list(modes)
        order_rng.shuffle(order)
        results = []
        for mode in order:
            result = await _run_create_mode(
                mode=mode,
                round_index=round_index,
                create_app=modes[mode]["create_app"],
                concurrent=bool(modes[mode]["concurrent"]),
                policy_name=policy_name,
            )
            per_mode_ops[mode].append(float(result["ops_per_second"]))
            results.append(result)

        indexed = {result["mode"]: result for result in results}
        rounds.append({"round": round_index, "order": order, "results": results})
        steps.append(
            {
                "step": round_index,
                "order": order,
                "ops_per_second": {
                    mode: indexed[mode]["ops_per_second"] for mode in modes
                },
                "ratio_scalar_concurrent_over_scalar_sequential": (
                    indexed["scalar_concurrent_create"]["ops_per_second"]
                    / indexed["scalar_sequential_create"]["ops_per_second"]
                ),
                "ratio_batch_sequential_over_scalar_sequential": (
                    indexed["batch_sequential_create"]["ops_per_second"]
                    / indexed["scalar_sequential_create"]["ops_per_second"]
                ),
                "ratio_batch_concurrent_over_scalar_concurrent": (
                    indexed["batch_concurrent_create"]["ops_per_second"]
                    / indexed["scalar_concurrent_create"]["ops_per_second"]
                ),
                "ratio_batch_concurrent_over_batch_sequential": (
                    indexed["batch_concurrent_create"]["ops_per_second"]
                    / indexed["batch_sequential_create"]["ops_per_second"]
                ),
            }
        )

    return {
        "policy": policy,
        "rounds": rounds,
        "steps": steps,
        "summary": {
            "ops": OPS_COUNT,
            "round_count": ROUND_COUNT,
            "concurrency": CONCURRENCY,
            "batch_policy": {
                "enabled": True,
                "name": policy_name,
                "max_size": max_size,
                "expected_batch_count": int(policy["expected_batch_count"]),
                "calculated_batch_count": OPS_COUNT // max_size,
                "max_delay_ms": max_delay_ms,
            },
            "ops_per_second": {
                mode: _ops_summary(values) for mode, values in per_mode_ops.items()
            },
            "mean_ratios": {
                "scalar_concurrent_over_scalar_sequential": (
                    mean(per_mode_ops["scalar_concurrent_create"])
                    / mean(per_mode_ops["scalar_sequential_create"])
                ),
                "batch_sequential_over_scalar_sequential": (
                    mean(per_mode_ops["batch_sequential_create"])
                    / mean(per_mode_ops["scalar_sequential_create"])
                ),
                "batch_concurrent_over_scalar_concurrent": (
                    mean(per_mode_ops["batch_concurrent_create"])
                    / mean(per_mode_ops["scalar_concurrent_create"])
                ),
                "batch_concurrent_over_batch_sequential": (
                    mean(per_mode_ops["batch_concurrent_create"])
                    / mean(per_mode_ops["batch_sequential_create"])
                ),
            },
        },
    }


async def _run_modes_benchmark() -> dict[str, Any]:
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    policy_results = []
    for policy in BATCH_POLICIES:
        policy_results.append(await _run_policy_benchmark(policy))
    return {
        "summary": {
            "ops": OPS_COUNT,
            "round_count": ROUND_COUNT,
            "concurrency": CONCURRENCY,
            "policy_count": len(BATCH_POLICIES),
            "policies": [result["summary"]["batch_policy"] for result in policy_results],
        },
        "policy_results": policy_results,
    }


@pytest.mark.perf
def test_tigrbl_create_modes_15_rounds_2500_ops_two_batch_policies() -> None:
    payload = asyncio.run(_run_modes_benchmark())
    RESULTS_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(
        "\n[perf] tigrbl create batch policy permutations "
        f"rounds={ROUND_COUNT} ops={OPS_COUNT} concurrency={CONCURRENCY}"
    )
    for policy_result in payload["policy_results"]:
        summary = policy_result["summary"]
        batch_policy = summary["batch_policy"]
        print(
            "[perf] policy={name} max_size={max_size} expected_batch_count={expected} "
            "calculated_batch_count={calculated}".format(
                name=batch_policy["name"],
                max_size=batch_policy["max_size"],
                expected=batch_policy["expected_batch_count"],
                calculated=batch_policy["calculated_batch_count"],
            )
        )
        for mode, mode_summary in summary["ops_per_second"].items():
            print(
                "[perf] {policy} {mode} ops/s min={min:.3f} max={max:.3f} "
                "mean={mean:.3f} stddev={stddev:.3f} median={median:.3f}".format(
                    policy=batch_policy["name"],
                    mode=mode,
                    **mode_summary,
                )
            )
        print(
            "[perf] {policy} mean ratio batch_concurrent/scalar_concurrent={ratio:.3f}".format(
                policy=batch_policy["name"],
                ratio=summary["mean_ratios"][
                    "batch_concurrent_over_scalar_concurrent"
                ],
            )
        )

    assert RESULTS_PATH.exists()
    assert payload["summary"]["round_count"] == ROUND_COUNT
    assert payload["summary"]["ops"] == OPS_COUNT
    assert payload["summary"]["concurrency"] == CONCURRENCY
    assert len(payload["policy_results"]) == 2
    for policy_result in payload["policy_results"]:
        summary = policy_result["summary"]
        assert len(policy_result["steps"]) == ROUND_COUNT
        assert summary["batch_policy"]["max_size"] > 0
        assert summary["batch_policy"]["expected_batch_count"] > 0
        for mode_summary in summary["ops_per_second"].values():
            assert mode_summary["mean"] > 0
