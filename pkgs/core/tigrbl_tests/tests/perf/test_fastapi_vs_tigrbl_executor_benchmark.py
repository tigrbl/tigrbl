from __future__ import annotations

import asyncio
import json
import logging
import random
import sqlite3
from pathlib import Path
from statistics import mean, median, pstdev
from tempfile import TemporaryDirectory
from time import perf_counter
from typing import Any, Callable

import httpx
import pytest
from sqlalchemy import String

from tests.i9n.uvicorn_utils import run_uvicorn_in_task, stop_uvicorn_server
from tests.perf.helper_fastapi_create_app import (
    create_fastapi_app,
    dispose_fastapi_app,
    fastapi_create_path,
    fetch_fastapi_names,
)
from tests.perf.helper_tigrbl_create_app import (
    create_tigrbl_app,
    dispose_tigrbl_app,
    fetch_tigrbl_names,
    initialize_tigrbl_app,
    tigrbl_create_path,
)
from tigrbl_base._base import AppBase, ColumnBase, TableBase
from tigrbl_core._spec.app_spec import AppSpec
from tigrbl_core._spec.binding_spec import HttpRestBindingSpec
from tigrbl_core._spec.engine_spec import EngineSpec
from tigrbl_core._spec.op_spec import OpSpec
from tigrbl_core._spec.storage_spec import StorageSpec
from tigrbl_runtime import Runtime, compiled_extension_available


RESULTS_PATH = Path(__file__).with_name(
    "benchmark_results_fastapi_tigrbl_executors_sequential_10_rounds.json"
)
REPO_ROOT = Path(__file__).resolve().parents[5]
BENCH_TMP_ROOT = REPO_ROOT / ".tmp" / "perf-benchmarks"
OPS_COUNT = 25
SEQUENTIAL_ROUNDS = 10
SCENARIOS = ("fastapi", "tigrbl_python_executor", "tigrbl_rust_executor")


class RustBenchmarkItem(TableBase):
    __tablename__ = "benchmark_rust_item"
    __resource__ = "items"

    id = ColumnBase(storage=StorageSpec(type_=String, primary_key=True))
    name = ColumnBase(storage=StorageSpec(type_=String))

    __tigrbl_ops__ = (
        OpSpec(
            alias="items.create",
            target="create",
            arity="collection",
            expose_rpc=False,
            expose_method=False,
            bindings=(
                HttpRestBindingSpec(
                    proto="http.rest",
                    methods=("POST",),
                    path="/items",
                ),
            ),
            tx_scope="read_write",
        ),
    )


class RustBenchmarkAppSpec(AppBase):
    TITLE = "rust_executor_benchmark"
    VERSION = "0.1.0"
    DESCRIPTION = "Tigrbl create benchmark served by the Rust executor."
    EXECUTION_BACKEND = "rust"
    TABLES = (RustBenchmarkItem,)


class TigrblRustExecutorCreateApp:
    """Small ASGI adapter that sends HTTP create requests to Runtime(..., rust)."""

    def __init__(self, db_path: Path) -> None:
        self.spec: AppSpec = AppBase.collect_spec(RustBenchmarkAppSpec)
        self.spec.engine = EngineSpec.from_any(
            {"kind": "sqlite", "path": str(db_path), "async": False}
        )
        self.runtime = Runtime(executor_backend="rust")
        self.handle = self.runtime.rust_handle(self.spec)

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        if scope["type"] == "lifespan":
            await self._lifespan(receive, send)
            return

        if scope["type"] != "http":
            await self._send_json(send, 404, {"error": "unsupported scope"})
            return

        method = str(scope.get("method") or "").upper()
        path = str(scope.get("path") or "")
        if method == "GET" and path == "/healthz":
            await self._send_json(
                send,
                200,
                {
                    "status": "ok",
                    "executor": "rust",
                    "compiled_extension_available": compiled_extension_available(),
                    "runtime": self.handle.describe(),
                },
            )
            return

        if method != "POST" or path != "/items":
            await self._send_json(send, 404, {"error": f"unknown route {path}"})
            return

        payload = await self._read_json(receive)
        response = self.handle.execute_rest(
            {
                "operation": "items.create",
                "transport": "rest",
                "path": "/items",
                "method": "POST",
                "body": payload,
            }
        )
        body = dict(response.get("body") or {})
        await self._send_json(send, int(response["status"]), body)

    @staticmethod
    async def _lifespan(receive: Any, send: Any) -> None:
        message = await receive()
        if message.get("type") == "lifespan.startup":
            await send({"type": "lifespan.startup.complete"})
        message = await receive()
        if message.get("type") == "lifespan.shutdown":
            await send({"type": "lifespan.shutdown.complete"})

    @staticmethod
    async def _read_json(receive: Any) -> dict[str, Any]:
        chunks: list[bytes] = []
        more_body = True
        while more_body:
            message = await receive()
            chunks.append(message.get("body", b""))
            more_body = bool(message.get("more_body", False))
        raw = b"".join(chunks) or b"{}"
        payload = json.loads(raw.decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("request body must be a JSON object")
        return payload

    @staticmethod
    async def _send_json(send: Any, status: int, payload: Any) -> None:
        body = json.dumps(payload, sort_keys=True).encode("utf-8")
        await send(
            {
                "type": "http.response.start",
                "status": status,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(body)).encode("ascii")),
                ],
            }
        )
        await send({"type": "http.response.body", "body": body})


def _quantile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    if len(ordered) == 1:
        return ordered[0]
    pos = (len(ordered) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(ordered) - 1)
    frac = pos - lo
    return ordered[lo] * (1.0 - frac) + ordered[hi] * frac


def _ops_summary(values: list[float]) -> dict[str, float | int]:
    q1 = _quantile(values, 0.25)
    q3 = _quantile(values, 0.75)
    iqr = q3 - q1
    low = q1 - 1.5 * iqr
    high = q3 + 1.5 * iqr
    return {
        "min": min(values),
        "max": max(values),
        "mean": mean(values),
        "stddev": pstdev(values),
        "median": median(values),
        "iqr": iqr,
        "outliers": sum(1 for value in values if value < low or value > high),
    }


def _pairwise_deltas(
    per_scenario_ops: dict[str, list[float]],
) -> dict[str, dict[str, float]]:
    means = {name: mean(values) for name, values in per_scenario_ops.items()}
    deltas: dict[str, dict[str, float]] = {}
    for left in SCENARIOS:
        for right in SCENARIOS:
            if left == right:
                continue
            key = f"{left}_minus_{right}"
            deltas[key] = {
                "delta_ops_per_second": means[left] - means[right],
                "throughput_ratio": means[left] / means[right] if means[right] else 0.0,
            }
    return deltas


def fetch_tigrbl_rust_names(_app: TigrblRustExecutorCreateApp, db_path: Path) -> list[str]:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT row_json FROM _tigrbl_rows "
            "WHERE table_name = 'items' ORDER BY rowid"
        ).fetchall()
    return [json.loads(row[0])["name"] for row in rows]


async def _benchmark_app(
    *,
    scenario: str,
    create_app: Callable[[Path], Any],
    endpoint_path: str,
    fetch_names: Callable[[Any, Path], list[str]],
    initialize: Callable[[Any], Any] | None = None,
    dispose_app: Callable[[Any], Any] | None = None,
) -> dict[str, Any]:
    BENCH_TMP_ROOT.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(
        dir=BENCH_TMP_ROOT, ignore_cleanup_errors=True
    ) as tmpdir:
        db_path = Path(tmpdir) / f"{scenario}.sqlite3"
        expected_names = [f"{scenario}-{i}" for i in range(OPS_COUNT)]

        start = perf_counter()
        app = create_app(db_path)
        if initialize is not None:
            await initialize(app)
        base_url, server, task = await run_uvicorn_in_task(app)
        first_start_time = perf_counter() - start

        op_durations: list[float] = []
        try:
            async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
                for _ in range(5):
                    ready = await client.get("/healthz")
                    if ready.status_code == 200:
                        break
                    await asyncio.sleep(0.05)

                execution_start = perf_counter()
                for item_name in expected_names:
                    op_start = perf_counter()
                    response = await client.post(endpoint_path, json={"name": item_name})
                    op_elapsed = perf_counter() - op_start

                    assert response.status_code in {200, 201}, response.text
                    body = response.json()
                    assert body["name"] == item_name
                    op_durations.append(op_elapsed)

                execution_total = perf_counter() - execution_start

            assert fetch_names(app, db_path) == expected_names
        finally:
            await stop_uvicorn_server(server, task)
            if dispose_app is not None:
                dispose_result = dispose_app(app)
                if hasattr(dispose_result, "__await__"):
                    await dispose_result

    return {
        "scenario": scenario,
        "ops": OPS_COUNT,
        "first_start_seconds": first_start_time,
        "execution_total_seconds": execution_total,
        "ops_per_second": OPS_COUNT / execution_total,
        "time_per_op_seconds": {
            "min": min(op_durations),
            "mean": mean(op_durations),
            "max": max(op_durations),
        },
    }


async def _run_sequential_consistency_benchmark() -> dict[str, Any]:
    scenario_runner = {
        "fastapi": dict(
            create_app=create_fastapi_app,
            endpoint_path=fastapi_create_path(),
            fetch_names=lambda _app, db_path: fetch_fastapi_names(db_path),
            initialize=None,
            dispose_app=dispose_fastapi_app,
        ),
        "tigrbl_python_executor": dict(
            create_app=create_tigrbl_app,
            endpoint_path=tigrbl_create_path(),
            fetch_names=lambda _app, db_path: fetch_tigrbl_names(db_path),
            initialize=initialize_tigrbl_app,
            dispose_app=dispose_tigrbl_app,
        ),
        "tigrbl_rust_executor": dict(
            create_app=lambda db_path: TigrblRustExecutorCreateApp(db_path),
            endpoint_path="/items",
            fetch_names=fetch_tigrbl_rust_names,
            initialize=None,
            dispose_app=None,
        ),
    }
    order_rng = random.Random(20260424)
    rounds: list[dict[str, Any]] = []
    steps: list[dict[str, Any]] = []

    for round_index in range(1, SEQUENTIAL_ROUNDS + 1):
        order = list(SCENARIOS)
        order_rng.shuffle(order)
        round_results: list[dict[str, Any]] = []

        for scenario in order:
            config = scenario_runner[scenario]
            result = await _benchmark_app(
                scenario=scenario,
                create_app=config["create_app"],
                endpoint_path=config["endpoint_path"],
                fetch_names=config["fetch_names"],
                initialize=config["initialize"],
                dispose_app=config["dispose_app"],
            )
            round_results.append(result)

        indexed = {result["scenario"]: result for result in round_results}
        ops_per_second = {
            scenario: indexed[scenario]["ops_per_second"] for scenario in SCENARIOS
        }
        rounds.append({"round": round_index, "order": order, "results": round_results})
        steps.append(
            {
                "step": round_index,
                "order": order,
                "ops_per_second": ops_per_second,
                "pairwise_deltas": _pairwise_deltas(
                    {name: [value] for name, value in ops_per_second.items()}
                ),
            }
        )

    per_scenario_ops: dict[str, list[float]] = {scenario: [] for scenario in SCENARIOS}
    for round_payload in rounds:
        for result in round_payload["results"]:
            per_scenario_ops[result["scenario"]].append(result["ops_per_second"])

    return {
        "rounds": rounds,
        "steps": steps,
        "summary": {
            "round_count": SEQUENTIAL_ROUNDS,
            "step_count": SEQUENTIAL_ROUNDS,
            "ops_per_second": {
                scenario: _ops_summary(values)
                for scenario, values in per_scenario_ops.items()
            },
            "pairwise_deltas": _pairwise_deltas(per_scenario_ops),
        },
    }


@pytest.mark.perf
def test_fastapi_vs_tigrbl_python_vs_tigrbl_rust_sequential_10_rounds() -> None:
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    payload = asyncio.run(_run_sequential_consistency_benchmark())
    RESULTS_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("\n[perf] randomized sequential order")
    for step in payload["steps"]:
        ops = step["ops_per_second"]
        print(
            "[perf] round={round} order={order} fastapi={fastapi:.3f} "
            "tigrbl_python={python:.3f} tigrbl_rust={rust:.3f}".format(
                round=step["step"],
                order="->".join(step["order"]),
                fastapi=ops["fastapi"],
                python=ops["tigrbl_python_executor"],
                rust=ops["tigrbl_rust_executor"],
            )
        )

    print("\n[perf] mean ops/s by scenario")
    for scenario in SCENARIOS:
        stats = payload["summary"]["ops_per_second"][scenario]
        print(
            "[perf] {scenario} min={min:.3f} max={max:.3f} mean={mean:.3f} "
            "stddev={stddev:.3f} median={median:.3f} iqr={iqr:.3f} "
            "outliers={outliers}".format(scenario=scenario, **stats)
        )

    print("[perf] mean pairwise throughput deltas")
    for key, delta in payload["summary"]["pairwise_deltas"].items():
        print(
            "[perf] {key} delta_ops/s={delta:.3f} ratio={ratio:.3f}".format(
                key=key,
                delta=delta["delta_ops_per_second"],
                ratio=delta["throughput_ratio"],
            )
        )

    assert RESULTS_PATH.exists()
    assert payload["summary"]["round_count"] == SEQUENTIAL_ROUNDS
    assert payload["summary"]["step_count"] == SEQUENTIAL_ROUNDS
    assert len(payload["steps"]) == SEQUENTIAL_ROUNDS
    for step in payload["steps"]:
        assert sorted(step["order"]) == sorted(SCENARIOS)
        for scenario in SCENARIOS:
            assert step["ops_per_second"][scenario] > 0
