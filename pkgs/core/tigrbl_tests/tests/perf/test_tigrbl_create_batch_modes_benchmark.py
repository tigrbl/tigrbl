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
    "benchmark_results_tigrbl_create_modes_15_rounds_250_ops.json"
)
PERF_TEMP_ROOT = Path(__file__).resolve().parents[5] / ".tmp" / "pytest-perf"
ROUND_COUNT = 15
OPS_COUNT = 250
CONCURRENCY = 10
BATCH_MAX_SIZE = 25
BATCH_MAX_DELAY_MS = 1
PRE_MEASUREMENT_WAIT_SECONDS = 0.5


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
) -> dict[str, Any]:
    PERF_TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=PERF_TEMP_ROOT, ignore_cleanup_errors=True) as tmpdir:
        db_path = Path(tmpdir) / f"{mode}-{round_index}.sqlite3"
        measured_names = [f"{mode}-{round_index}-{idx}" for idx in range(OPS_COUNT)]

        start = perf_counter()
        app = create_app(db_path)
        await initialize_tigrbl_app(app)
        base_url, server, task = await run_uvicorn_in_task(app)
        first_start_seconds = perf_counter() - start
        op_durations: list[float] = []
        try:
            async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
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
        "mode": mode,
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


async def _run_modes_benchmark() -> dict[str, Any]:
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    modes: dict[str, dict[str, Any]] = {
        "scalar_sequential_create": {
            "create_app": create_tigrbl_app,
            "concurrent": False,
        },
        "scalar_concurrent_create": {
            "create_app": create_tigrbl_app,
            "concurrent": True,
        },
        "batch_concurrent_create": {
            "create_app": lambda db_path: create_tigrbl_batch_app(
                db_path,
                max_size=BATCH_MAX_SIZE,
                max_delay_ms=BATCH_MAX_DELAY_MS,
            ),
            "concurrent": True,
        },
    }
    order_rng = random.Random(20260507)
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
                "ratio_batch_concurrent_over_scalar_concurrent": (
                    indexed["batch_concurrent_create"]["ops_per_second"]
                    / indexed["scalar_concurrent_create"]["ops_per_second"]
                ),
            }
        )

    return {
        "rounds": rounds,
        "steps": steps,
        "summary": {
            "ops": OPS_COUNT,
            "round_count": ROUND_COUNT,
            "concurrency": CONCURRENCY,
            "batch_policy": {
                "enabled": True,
                "max_size": BATCH_MAX_SIZE,
                "max_delay_ms": BATCH_MAX_DELAY_MS,
            },
            "ops_per_second": {
                mode: _ops_summary(values) for mode, values in per_mode_ops.items()
            },
            "mean_ratios": {
                "scalar_concurrent_over_scalar_sequential": (
                    mean(per_mode_ops["scalar_concurrent_create"])
                    / mean(per_mode_ops["scalar_sequential_create"])
                ),
                "batch_concurrent_over_scalar_concurrent": (
                    mean(per_mode_ops["batch_concurrent_create"])
                    / mean(per_mode_ops["scalar_concurrent_create"])
                ),
            },
            "current_batch_runtime_note": (
                "batch_concurrent_create enables the packed batch policy on the "
                "create op and measures current real HTTP runtime behavior."
            ),
        },
    }


@pytest.mark.perf
def test_tigrbl_create_modes_15_rounds_250_ops() -> None:
    payload = asyncio.run(_run_modes_benchmark())
    RESULTS_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    summary = payload["summary"]
    print(
        "\n[perf] tigrbl create modes "
        f"rounds={summary['round_count']} ops={summary['ops']} "
        f"concurrency={summary['concurrency']}"
    )
    for step in payload["steps"]:
        ops = step["ops_per_second"]
        print(
            "[perf] round={round} order={order} scalar_seq={seq:.3f} "
            "scalar_conc={conc:.3f} batch_conc={batch:.3f} "
            "conc/seq={conc_ratio:.3f} batch/conc={batch_ratio:.3f}".format(
                round=step["step"],
                order="->".join(step["order"]),
                seq=ops["scalar_sequential_create"],
                conc=ops["scalar_concurrent_create"],
                batch=ops["batch_concurrent_create"],
                conc_ratio=step["ratio_scalar_concurrent_over_scalar_sequential"],
                batch_ratio=step["ratio_batch_concurrent_over_scalar_concurrent"],
            )
        )
    for mode, mode_summary in summary["ops_per_second"].items():
        print(
            "[perf] {mode} ops/s min={min:.3f} max={max:.3f} "
            "mean={mean:.3f} stddev={stddev:.3f} median={median:.3f}".format(
                mode=mode,
                **mode_summary,
            )
        )
    print(
        "[perf] mean ratio scalar_concurrent/scalar_sequential={:.3f}".format(
            summary["mean_ratios"]["scalar_concurrent_over_scalar_sequential"]
        )
    )
    print(
        "[perf] mean ratio batch_concurrent/scalar_concurrent={:.3f}".format(
            summary["mean_ratios"]["batch_concurrent_over_scalar_concurrent"]
        )
    )

    assert RESULTS_PATH.exists()
    assert summary["round_count"] == ROUND_COUNT
    assert summary["ops"] == OPS_COUNT
    assert len(payload["steps"]) == ROUND_COUNT
    for mode_summary in summary["ops_per_second"].values():
        assert mode_summary["mean"] > 0
