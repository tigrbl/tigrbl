from __future__ import annotations

import argparse
import asyncio
import inspect
import json
import sqlite3
from pathlib import Path
from tempfile import mkdtemp
from time import perf_counter
from typing import Any

import httpx

from tigrbl import TableBase, TigrblApp
from tigrbl._spec import HttpJsonRpcBindingSpec, HttpRestBindingSpec, OpSpec
from tigrbl.factories.engine import sqlitef
from tigrbl.types import Column, Integer, String
from tigrbl_kernel import build_kernel_plan, measure_packed_kernel

from tests.i9n.uvicorn_utils import run_uvicorn_in_task, stop_uvicorn_server
from tests.perf.helper_fastapi_create_app import (
    create_fastapi_app,
    dispose_fastapi_app,
)

ROOT = Path(__file__).resolve().parents[4]
LOCAL_TMP = ROOT / ".tmp"
PRE_MEASUREMENT_WAIT_SECONDS = 0.5


class TigrblParityBenchmarkItem(TableBase):
    __tablename__ = "benchmark_item"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    __tigrbl_ops__ = (
        OpSpec(
            alias="BenchmarkItem.create",
            target="create",
            bindings=(
                HttpRestBindingSpec(
                    proto="http.rest",
                    methods=("POST",),
                    path="/items",
                ),
                HttpJsonRpcBindingSpec(
                    proto="http.jsonrpc",
                    rpc_method="BenchmarkItem.create",
                ),
            ),
        ),
    )


def create_tigrbl_parity_app(db_path: Path) -> TigrblApp:
    app = TigrblApp(engine=sqlitef(str(db_path), async_=False))
    app.include_table(TigrblParityBenchmarkItem)
    return app


async def initialize_tigrbl_parity_app(app: TigrblApp) -> None:
    init_result = app.initialize()
    if inspect.isawaitable(init_result):
        await init_result
    app.mount_jsonrpc(prefix="/rpc")


async def dispose_tigrbl_parity_app(app: TigrblApp) -> None:
    engine = getattr(app, "engine", None)
    provider = getattr(engine, "provider", None)
    raw_engine = getattr(provider, "_engine", None)
    dispose = getattr(raw_engine, "dispose", None)
    if not callable(dispose):
        return
    result: Any = dispose()
    if inspect.isawaitable(result):
        await result


def fetch_names(db_path: Path) -> list[str]:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT name FROM benchmark_item ORDER BY id"
        ).fetchall()
    return [row[0] for row in rows]


def _serialize_measurement(app: Any) -> dict[str, Any]:
    plan = build_kernel_plan(app)
    packed = getattr(plan, "packed", None)
    if packed is None:
        return {}
    measurement = getattr(packed, "measurement", None) or measure_packed_kernel(packed)
    return {
        "raw_bytes": int(measurement.raw_bytes),
        "compressed_bytes": int(measurement.compressed_bytes),
        "segment_count": int(measurement.segment_count),
        "step_count": int(measurement.step_count),
        "phase_tree_node_count": int(measurement.phase_tree_node_count),
        "proto_count": int(measurement.proto_count),
        "selector_count": int(measurement.selector_count),
        "op_count": int(measurement.op_count),
        "route_row_count": int(measurement.route_row_count),
        "route_col_count": int(measurement.route_col_count),
        "route_slot_count": int(measurement.route_slot_count),
        "exact_route_count": int(measurement.exact_route_count),
        "fusible_sync_segment_count": int(measurement.fusible_sync_segment_count),
        "hot_op_count": int(measurement.hot_op_count),
    }


async def _await_if_needed(value: Any) -> Any:
    if inspect.isawaitable(value):
        return await value
    return value


async def _ready_client(_client: httpx.AsyncClient) -> None:
    await asyncio.sleep(PRE_MEASUREMENT_WAIT_SECONDS)


async def _run_rest_benchmark(
    client: httpx.AsyncClient,
    *,
    endpoint: str,
    ops: int,
    warmup_ops: int,
    label: str,
) -> dict[str, Any]:
    for idx in range(warmup_ops):
        response = await client.post(endpoint, json={"name": f"warmup-{label}-{idx}"})
        assert response.status_code in {200, 201}, response.text

    start = perf_counter()
    for idx in range(ops):
        response = await client.post(endpoint, json={"name": f"bench-{label}-{idx}"})
        assert response.status_code in {200, 201}, response.text
    elapsed = perf_counter() - start
    return {
        "ops": ops,
        "warmup_ops": warmup_ops,
        "total_execution_time_seconds": elapsed,
        "ops_per_second": ops / elapsed,
        "endpoint": endpoint,
    }


async def _run_jsonrpc_benchmark(
    client: httpx.AsyncClient, *, ops: int, warmup_ops: int
) -> dict[str, Any]:
    method = "BenchmarkItem.create"
    for idx in range(warmup_ops):
        response = await client.post(
            "/rpc",
            json={
                "jsonrpc": "2.0",
                "id": idx,
                "method": method,
                "params": {"name": f"warmup-rpc-{idx}"},
            },
        )
        assert response.status_code == 200, response.text

    start = perf_counter()
    for idx in range(ops):
        response = await client.post(
            "/rpc",
            json={
                "jsonrpc": "2.0",
                "id": idx + warmup_ops,
                "method": method,
                "params": {"name": f"bench-rpc-{idx}"},
            },
        )
        assert response.status_code == 200, response.text
    elapsed = perf_counter() - start
    return {
        "ops": ops,
        "warmup_ops": warmup_ops,
        "total_execution_time_seconds": elapsed,
        "ops_per_second": ops / elapsed,
        "endpoint": "/rpc",
        "method": method,
    }


async def _benchmark_fastapi_rest(*, ops: int, warmup_ops: int) -> dict[str, Any]:
    tmpdir = Path(mkdtemp(dir=LOCAL_TMP))
    db_path = tmpdir / "fastapi_parity.sqlite3"
    app = create_fastapi_app(db_path)
    base_url, server, task = await run_uvicorn_in_task(app)
    try:
        async with httpx.AsyncClient(base_url=base_url, timeout=20.0) as client:
            await _ready_client(client)
            rest = await _run_rest_benchmark(
                client,
                endpoint="/items",
                ops=ops,
                warmup_ops=warmup_ops,
                label="fastapi",
            )
        persisted = fetch_names(db_path)
    finally:
        await stop_uvicorn_server(server, task)
        await dispose_fastapi_app(app)

    return {
        "rest_unary": rest,
        "persisted_row_count": len(persisted),
    }


async def _benchmark_tigrbl(*, ops: int, warmup_ops: int) -> dict[str, Any]:
    tmpdir = Path(mkdtemp(dir=LOCAL_TMP))
    db_path = tmpdir / "tigrbl_parity.sqlite3"
    app = create_tigrbl_parity_app(db_path)
    await initialize_tigrbl_parity_app(app)
    measurement = _serialize_measurement(app)
    base_url, server, task = await run_uvicorn_in_task(app)
    try:
        async with httpx.AsyncClient(base_url=base_url, timeout=20.0) as client:
            await _ready_client(client)
            rest = await _run_rest_benchmark(
                client,
                endpoint="/items",
                ops=ops,
                warmup_ops=warmup_ops,
                label="tigrbl-rest",
            )
            jsonrpc = await _run_jsonrpc_benchmark(
                client,
                ops=ops,
                warmup_ops=warmup_ops,
            )
        persisted = fetch_names(db_path)
    finally:
        await stop_uvicorn_server(server, task)
        await dispose_tigrbl_parity_app(app)

    return {
        "kernel_plan_measurement": measurement,
        "rest_unary": rest,
        "jsonrpc_unary": jsonrpc,
        "persisted_row_count": len(persisted),
    }


async def _run_suite(*, ops: int, warmup_ops: int) -> dict[str, Any]:
    LOCAL_TMP.mkdir(parents=True, exist_ok=True)
    fastapi = await _benchmark_fastapi_rest(ops=ops, warmup_ops=warmup_ops)
    tigrbl = await _benchmark_tigrbl(ops=ops, warmup_ops=warmup_ops)
    return {
        "fairness": {
            "apples_to_apples_primary_comparison": "fastapi.rest_unary vs tigrbl.rest_unary",
            "shared_transport": "HTTP REST unary",
            "shared_method": "POST",
            "shared_path": "/items",
            "shared_payload_shape": {"name": "string"},
            "shared_table_name": "benchmark_item",
            "shared_server_runner": "uvicorn via run_uvicorn_in_task",
            "shared_database_family": "SQLite",
            "notes": [
                "FastAPI has no kernel-plan packing, so KC metrics apply only to Tigrbl.",
                "Tigrbl JSON-RPC is reported as a supplemental non-FastAPI parity scenario.",
            ],
        },
        "candidate": {
            "fastapi": fastapi,
            "tigrbl": tigrbl,
            "comparisons": {
                "rest_unary": {
                    "fastapi_ops_per_second": float(
                        fastapi["rest_unary"]["ops_per_second"]
                    ),
                    "tigrbl_ops_per_second": float(
                        tigrbl["rest_unary"]["ops_per_second"]
                    ),
                    "delta_ops_per_second": float(
                        tigrbl["rest_unary"]["ops_per_second"]
                    )
                    - float(fastapi["rest_unary"]["ops_per_second"]),
                    "throughput_ratio_tigrbl_over_fastapi": (
                        float(tigrbl["rest_unary"]["ops_per_second"])
                        / float(fastapi["rest_unary"]["ops_per_second"])
                    ),
                    "compressed_bytes_per_tigrbl_op": (
                        float(tigrbl["kernel_plan_measurement"]["compressed_bytes"])
                        / float(tigrbl["rest_unary"]["ops"])
                    ),
                }
            },
        },
    }


def _build_delta(baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    base_comp = baseline.get("candidate", {}).get("comparisons", {}).get(
        "rest_unary", {}
    )
    cand_comp = candidate.get("candidate", {}).get("comparisons", {}).get(
        "rest_unary", {}
    )
    base_kc = baseline.get("candidate", {}).get("tigrbl", {}).get(
        "kernel_plan_measurement", {}
    )
    cand_kc = candidate.get("candidate", {}).get("tigrbl", {}).get(
        "kernel_plan_measurement", {}
    )
    out: dict[str, Any] = {"rest_unary": {}, "kernel_plan_measurement": {}}
    if base_comp and cand_comp:
        base_ops = float(base_comp["throughput_ratio_tigrbl_over_fastapi"])
        cand_ops = float(cand_comp["throughput_ratio_tigrbl_over_fastapi"])
        out["rest_unary"] = {
            "throughput_ratio_delta": cand_ops - base_ops,
            "throughput_ratio_improvement_percent": (
                ((cand_ops - base_ops) / base_ops) * 100 if base_ops else 0.0
            ),
            "delta_ops_per_second_delta": float(cand_comp["delta_ops_per_second"])
            - float(base_comp["delta_ops_per_second"]),
        }
    if base_kc and cand_kc:
        base_compressed = float(base_kc["compressed_bytes"])
        cand_compressed = float(cand_kc["compressed_bytes"])
        out["kernel_plan_measurement"] = {
            "compressed_bytes_delta": cand_compressed - base_compressed,
            "compressed_bytes_regression_percent": (
                ((cand_compressed - base_compressed) / base_compressed) * 100
                if base_compressed
                else 0.0
            ),
            "raw_bytes_delta": float(cand_kc["raw_bytes"]) - float(base_kc["raw_bytes"]),
        }
    return out


def _render_report(payload: dict[str, Any]) -> str:
    fairness = payload.get("fairness", {})
    candidate = payload.get("candidate", {})
    fastapi = candidate.get("fastapi", {})
    tigrbl = candidate.get("tigrbl", {})
    comparison = candidate.get("comparisons", {}).get("rest_unary", {})
    measurement = tigrbl.get("kernel_plan_measurement", {})

    lines = [
        "# Kernel Packing KC and FastAPI Parity Report",
        "",
        "## Fairness",
        f"- primary comparison: {fairness.get('apples_to_apples_primary_comparison', 'n/a')}",
        f"- transport: {fairness.get('shared_transport', 'n/a')}",
        f"- request: {fairness.get('shared_method', 'n/a')} {fairness.get('shared_path', 'n/a')}",
        f"- payload: {json.dumps(fairness.get('shared_payload_shape', {}), sort_keys=True)}",
        f"- table: {fairness.get('shared_table_name', 'n/a')}",
        f"- server runner: {fairness.get('shared_server_runner', 'n/a')}",
        f"- database: {fairness.get('shared_database_family', 'n/a')}",
        "",
        "## Throughput",
        f"- FastAPI REST unary: {fastapi.get('rest_unary', {}).get('ops_per_second', 0):.2f} ops/s",
        f"- Tigrbl REST unary: {tigrbl.get('rest_unary', {}).get('ops_per_second', 0):.2f} ops/s",
        f"- Tigrbl JSON-RPC unary: {tigrbl.get('jsonrpc_unary', {}).get('ops_per_second', 0):.2f} ops/s",
        f"- Tigrbl/FastAPI REST ratio: {comparison.get('throughput_ratio_tigrbl_over_fastapi', 0):.3f}",
        "",
        "## Tigrbl Kernel Packing KC Proxy",
        f"- raw bytes: {measurement.get('raw_bytes', 'n/a')}",
        f"- compressed bytes: {measurement.get('compressed_bytes', 'n/a')}",
        f"- segments: {measurement.get('segment_count', 'n/a')}",
        f"- steps: {measurement.get('step_count', 'n/a')}",
        f"- phase tree nodes: {measurement.get('phase_tree_node_count', 'n/a')}",
        f"- compressed bytes per REST op in this run: {comparison.get('compressed_bytes_per_tigrbl_op', 0):.2f}",
    ]

    delta = payload.get("delta", {})
    if delta:
        lines.extend(
            [
                "",
                "## Delta vs Baseline",
                f"- throughput ratio improvement: {delta.get('rest_unary', {}).get('throughput_ratio_improvement_percent', 0):.2f}%",
                f"- compressed bytes delta: {delta.get('kernel_plan_measurement', {}).get('compressed_bytes_delta', 0):.0f}",
                f"- compressed bytes regression: {delta.get('kernel_plan_measurement', {}).get('compressed_bytes_regression_percent', 0):.2f}%",
            ]
        )

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Benchmark Tigrbl kernel-plan KC proxy and compare Tigrbl REST throughput "
            "against a FastAPI app on the same POST /items workload."
        )
    )
    parser.add_argument("--ops", type=int, default=150)
    parser.add_argument("--warmup-ops", type=int, default=20)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--report-output", type=Path, default=None)
    parser.add_argument("--baseline", type=Path, default=None)
    parser.add_argument("--min-ratio-improvement-percent", type=float, default=0.0)
    parser.add_argument(
        "--max-compressed-byte-regression-percent", type=float, default=10.0
    )
    args = parser.parse_args()

    payload = asyncio.run(_run_suite(ops=args.ops, warmup_ops=args.warmup_ops))
    if args.baseline is not None:
        baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
        payload["delta"] = _build_delta(baseline, payload)
        ratio_improvement = float(
            payload["delta"].get("rest_unary", {}).get(
                "throughput_ratio_improvement_percent", 0.0
            )
        )
        if ratio_improvement < args.min_ratio_improvement_percent:
            raise SystemExit(
                "Benchmark ratio gate failed: "
                f"{ratio_improvement:.2f}% < {args.min_ratio_improvement_percent:.2f}%"
            )
        compressed_regression = float(
            payload["delta"].get("kernel_plan_measurement", {}).get(
                "compressed_bytes_regression_percent", 0.0
            )
        )
        if compressed_regression > args.max_compressed_byte_regression_percent:
            raise SystemExit(
                "Kernel-plan compressed-byte gate failed: "
                f"{compressed_regression:.2f}% > "
                f"{args.max_compressed_byte_regression_percent:.2f}%"
            )

    serialized = json.dumps(payload, indent=2)
    if args.output is not None:
        args.output.write_text(serialized, encoding="utf-8")
    if args.report_output is not None:
        args.report_output.write_text(_render_report(payload), encoding="utf-8")
    print(serialized)


if __name__ == "__main__":
    main()
