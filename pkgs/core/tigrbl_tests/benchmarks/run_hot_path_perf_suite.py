from __future__ import annotations

import argparse
import asyncio
import gzip
import json
import shutil
import struct
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from tigrbl import TableBase, TigrblApp
from tigrbl._spec import HttpJsonRpcBindingSpec, HttpRestBindingSpec, OpSpec
from tigrbl.factories.engine import sqlitef
from tigrbl.types import Column, Integer, String
from tigrbl_kernel import build_kernel_plan, load_packed_kernel_hot_block, measure_packed_kernel
from tigrbl_kernel.measure import _HOT_BLOCK_SECTION_NAMES

ROOT = Path(__file__).resolve().parents[4]
PERF_DIR = ROOT / "pkgs" / "core" / "tigrbl_tests" / "tests" / "perf"
TMP_DIR = ROOT / ".tmp"
KERNEL_BENCHMARK_JSON = PERF_DIR / "kernel-plan-benchmark.json"
KERNEL_BENCHMARK_MD = PERF_DIR / "kernel-plan-benchmark.md"
SUITE_MANIFEST_JSON = PERF_DIR / "hot_path_perf_suite_manifest.json"
SUITE_REPORT_MD = PERF_DIR / "hot_path_perf_suite_report.md"
HOT_BLOCK_PREFIX = PERF_DIR / "tgpkhot1-benchmark-items"
FASTAPI_CALL_GRAPH_JSON = PERF_DIR / "fastapi_create_call_graph_250_ops.json"
STREAMING_RESULTS_JSON = PERF_DIR / "benchmark_results_streaming_uvicorn.json"
STREAMING_KERNEL_JSON = PERF_DIR / "kernel-plan-benchmark-streaming.json"
STREAMING_KERNEL_MD = PERF_DIR / "kernel-plan-benchmark-streaming.md"
STREAMING_TIGRBL_CALL_GRAPH_JSON = PERF_DIR / "tigrbl_streaming_call_graph_250_ops.json"
STREAMING_FASTAPI_CALL_GRAPH_JSON = PERF_DIR / "fastapi_streaming_call_graph_250_ops.json"
STREAMING_HOT_BLOCK_PREFIX = PERF_DIR / "tgpkhot1-benchmark-streaming"
WEBSOCKET_RESULTS_JSON = PERF_DIR / "benchmark_results_websocket_uvicorn.json"
WEBSOCKET_KERNEL_JSON = PERF_DIR / "kernel-plan-benchmark-websocket.json"
WEBSOCKET_KERNEL_MD = PERF_DIR / "kernel-plan-benchmark-websocket.md"
WEBSOCKET_TIGRBL_CALL_GRAPH_JSON = PERF_DIR / "tigrbl_websocket_call_graph_250_ops.json"
WEBSOCKET_FASTAPI_CALL_GRAPH_JSON = PERF_DIR / "fastapi_websocket_call_graph_250_ops.json"
WEBSOCKET_TIGRBL_TRANSPORT_CALL_GRAPH_JSON = (
    PERF_DIR / "tigrbl_websocket_transport_call_graph_250_ops.json"
)
WEBSOCKET_FASTAPI_TRANSPORT_CALL_GRAPH_JSON = (
    PERF_DIR / "fastapi_websocket_transport_call_graph_250_ops.json"
)
WEBSOCKET_HOT_BLOCK_PREFIX = PERF_DIR / "tgpkhot1-benchmark-websocket"
SSE_RESULTS_JSON = PERF_DIR / "benchmark_results_sse_uvicorn.json"
SSE_KERNEL_JSON = PERF_DIR / "kernel-plan-benchmark-sse.json"
SSE_KERNEL_MD = PERF_DIR / "kernel-plan-benchmark-sse.md"
SSE_TIGRBL_CALL_GRAPH_JSON = PERF_DIR / "tigrbl_sse_call_graph_250_ops.json"
SSE_FASTAPI_CALL_GRAPH_JSON = PERF_DIR / "fastapi_sse_call_graph_250_ops.json"
SSE_TIGRBL_TRANSPORT_CALL_GRAPH_JSON = PERF_DIR / "tigrbl_sse_transport_call_graph_250_ops.json"
SSE_FASTAPI_TRANSPORT_CALL_GRAPH_JSON = PERF_DIR / "fastapi_sse_transport_call_graph_250_ops.json"
SSE_HOT_BLOCK_PREFIX = PERF_DIR / "tgpkhot1-benchmark-sse"
WEBTRANSPORT_RESULTS_JSON = PERF_DIR / "benchmark_results_webtransport_uvicorn.json"
WEBTRANSPORT_KERNEL_JSON = PERF_DIR / "kernel-plan-benchmark-webtransport.json"
WEBTRANSPORT_KERNEL_MD = PERF_DIR / "kernel-plan-benchmark-webtransport.md"
WEBTRANSPORT_TIGRBL_CALL_GRAPH_JSON = PERF_DIR / "tigrbl_webtransport_call_graph_250_ops.json"
WEBTRANSPORT_TIGRBL_TRANSPORT_CALL_GRAPH_JSON = (
    PERF_DIR / "tigrbl_webtransport_transport_call_graph_250_ops.json"
)
WEBTRANSPORT_HOT_BLOCK_PREFIX = PERF_DIR / "tgpkhot1-benchmark-webtransport"

LOCKED_EXISTING_BASELINES: dict[str, dict[str, float | int]] = {
    "unary": {
        "rest_ops_per_second": 718.12,
        "jsonrpc_ops_per_second": 618.46,
        "raw_bytes_ceiling": 1627,
    },
    "streaming": {
        "transport_only_ops_per_second": 1020.00,
        "db_backed_ops_per_second": 666.88,
        "raw_bytes_ceiling": 858,
    },
    "websocket": {
        "transport_only_ops_per_second": 14237.96,
        "db_backed_ops_per_second": 156.41,
        "raw_bytes_ceiling": 848,
    },
}


class MissingSurfaceError(RuntimeError):
    pass


@dataclass(frozen=True)
class CommandTask:
    name: str
    argv: tuple[str, ...]
    artifact_paths: tuple[Path, ...]
    description: str


BENCHMARK_RERUN_TASKS: dict[str, tuple[str, ...]] = {
    "unary": ("kernel_plan_benchmark",),
    "streaming": ("streaming_perf_suite",),
    "websocket": ("websocket_perf_suite",),
    "sse": ("sse_perf_suite",),
    "webtransport": ("webtransport_perf_suite",),
}
MAX_BENCHMARK_RETRIES = 4


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


def _build_tigrbl_parity_app(db_path: Path) -> TigrblApp:
    app = TigrblApp(engine=sqlitef(str(db_path), async_=False), mount_system=False)
    app.include_table(TigrblParityBenchmarkItem)
    return app


async def _initialize_tigrbl_parity_app(app: TigrblApp) -> None:
    init_result = app.initialize()
    if hasattr(init_result, "__await__"):
        await init_result
    app.mount_jsonrpc(prefix="/rpc")


async def _dispose_tigrbl_parity_app(app: TigrblApp) -> None:
    engine = getattr(app, "engine", None)
    provider = getattr(engine, "provider", None)
    raw_engine = getattr(provider, "_engine", None)
    dispose = getattr(raw_engine, "dispose", None)
    if not callable(dispose):
        return
    dispose_result = dispose()
    if hasattr(dispose_result, "__await__"):
        await dispose_result


def _python_command(*args: str) -> tuple[str, ...]:
    return (sys.executable, *args)


def _default_tasks() -> list[CommandTask]:
    return [
        CommandTask(
            name="kernel_plan_benchmark",
            argv=_python_command(
                "pkgs/core/tigrbl_tests/benchmarks/tigrbl_kernel_plan_benchmark.py",
                "--output",
                str(TMP_DIR / "kernel-plan-benchmark.json"),
                "--report-output",
                str(TMP_DIR / "kernel-plan-benchmark.md"),
            ),
            artifact_paths=(TMP_DIR / "kernel-plan-benchmark.json", TMP_DIR / "kernel-plan-benchmark.md"),
            description="Generate the kernel packing KC and FastAPI parity report.",
        ),
        CommandTask(
            name="rest_unary_seq_25",
            argv=_python_command(
                "-m",
                "pytest",
                "pkgs/core/tigrbl_tests/tests/perf/test_tigrbl_vs_fastapi_create_benchmark.py::test_tigrbl_vs_fastapi_sequential_10_rounds_randomized_comparison",
                "-q",
            ),
            artifact_paths=(
                PERF_DIR / "benchmark_results_create_uvicorn.json",
                PERF_DIR / "benchmark_results_create_uvicorn_sequential_10_rounds.json",
            ),
            description="Run the 25-op unary parity benchmark.",
        ),
        CommandTask(
            name="rest_unary_seq_250",
            argv=_python_command(
                "-m",
                "pytest",
                "pkgs/core/tigrbl_tests/tests/perf/test_tigrbl_vs_fastapi_create_benchmark.py::test_tigrbl_vs_fastapi_sequential_10_rounds_randomized_comparison_250_ops",
                "-q",
            ),
            artifact_paths=(
                PERF_DIR / "benchmark_results_create_uvicorn.json",
                PERF_DIR / "benchmark_results_create_uvicorn_sequential_10_rounds_250_ops.json",
                PERF_DIR / "benchmark_results_create_httpxtransport_sequential_10_rounds_250_ops.json",
            ),
            description="Run the legacy 250-op unary parity benchmark over HTTPX real transport.",
        ),
        CommandTask(
            name="rest_unary_asgitransport_seq_250",
            argv=_python_command(
                "-m",
                "pytest",
                "pkgs/core/tigrbl_tests/tests/perf/test_tigrbl_vs_fastapi_create_benchmark.py::test_tigrbl_vs_fastapi_asgitransport_sequential_10_rounds_randomized_comparison_250_ops",
                "-q",
            ),
            artifact_paths=(
                PERF_DIR / "benchmark_results_create_asgitransport_sequential_10_rounds_250_ops.json",
            ),
            description="Run the 250-op unary parity benchmark over httpx.ASGITransport.",
        ),
        CommandTask(
            name="rest_unary_httpxtransport_seq_250",
            argv=_python_command(
                "-m",
                "pytest",
                "pkgs/core/tigrbl_tests/tests/perf/test_tigrbl_vs_fastapi_create_benchmark.py::test_tigrbl_vs_fastapi_httpxtransport_sequential_10_rounds_randomized_comparison_250_ops",
                "-q",
            ),
            artifact_paths=(
                PERF_DIR / "benchmark_results_create_httpxtransport_sequential_10_rounds_250_ops.json",
            ),
            description="Run the 250-op unary parity benchmark over HTTPX real transport.",
        ),
        CommandTask(
            name="tigrbl_call_graph_250",
            argv=_python_command(
                "-m",
                "pytest",
                "pkgs/core/tigrbl_tests/tests/perf/test_tigrbl_create_call_graph.py",
                "-q",
            ),
            artifact_paths=(PERF_DIR / "tigrbl_create_call_graph_250_ops.json",),
            description="Generate the Tigrbl unary call graph.",
        ),
        CommandTask(
            name="fastapi_call_graph_250",
            argv=_python_command(
                "-m",
                "pytest",
                "pkgs/core/tigrbl_tests/tests/perf/test_fastapi_create_call_graph.py",
                "-q",
            ),
            artifact_paths=(FASTAPI_CALL_GRAPH_JSON,),
            description="Generate the FastAPI unary call graph.",
        ),
        CommandTask(
            name="streaming_perf_suite",
            argv=_python_command(
                "pkgs/core/tigrbl_tests/benchmarks/tigrbl_streaming_perf_suite.py",
            ),
            artifact_paths=(
                STREAMING_RESULTS_JSON,
                STREAMING_KERNEL_JSON,
                STREAMING_KERNEL_MD,
                STREAMING_TIGRBL_CALL_GRAPH_JSON,
                STREAMING_FASTAPI_CALL_GRAPH_JSON,
                STREAMING_HOT_BLOCK_PREFIX.with_suffix(".bin"),
                STREAMING_HOT_BLOCK_PREFIX.with_suffix(".summary.json"),
                STREAMING_HOT_BLOCK_PREFIX.with_suffix(".hexdump.txt"),
                STREAMING_HOT_BLOCK_PREFIX.with_suffix(".benchmark.json"),
                STREAMING_HOT_BLOCK_PREFIX.with_suffix(".benchmark.md"),
            ),
            description="Run the full streaming parity suite and TGPKHOT1 export.",
        ),
        CommandTask(
            name="websocket_perf_suite",
            argv=_python_command(
                "pkgs/core/tigrbl_tests/benchmarks/tigrbl_websocket_perf_suite.py",
            ),
            artifact_paths=(
                WEBSOCKET_RESULTS_JSON,
                WEBSOCKET_KERNEL_JSON,
                WEBSOCKET_KERNEL_MD,
                WEBSOCKET_TIGRBL_TRANSPORT_CALL_GRAPH_JSON,
                WEBSOCKET_FASTAPI_TRANSPORT_CALL_GRAPH_JSON,
                WEBSOCKET_TIGRBL_CALL_GRAPH_JSON,
                WEBSOCKET_FASTAPI_CALL_GRAPH_JSON,
                WEBSOCKET_HOT_BLOCK_PREFIX.with_suffix(".bin"),
                WEBSOCKET_HOT_BLOCK_PREFIX.with_suffix(".summary.json"),
                WEBSOCKET_HOT_BLOCK_PREFIX.with_suffix(".hexdump.txt"),
                WEBSOCKET_HOT_BLOCK_PREFIX.with_suffix(".benchmark.json"),
                WEBSOCKET_HOT_BLOCK_PREFIX.with_suffix(".benchmark.md"),
            ),
            description="Run the full websocket parity suite and TGPKHOT1 export.",
        ),
        CommandTask(
            name="sse_perf_suite",
            argv=_python_command(
                "pkgs/core/tigrbl_tests/benchmarks/tigrbl_sse_perf_suite.py",
            ),
            artifact_paths=(
                SSE_RESULTS_JSON,
                SSE_KERNEL_JSON,
                SSE_KERNEL_MD,
                SSE_TIGRBL_TRANSPORT_CALL_GRAPH_JSON,
                SSE_FASTAPI_TRANSPORT_CALL_GRAPH_JSON,
                SSE_TIGRBL_CALL_GRAPH_JSON,
                SSE_FASTAPI_CALL_GRAPH_JSON,
                SSE_HOT_BLOCK_PREFIX.with_suffix(".bin"),
                SSE_HOT_BLOCK_PREFIX.with_suffix(".summary.json"),
                SSE_HOT_BLOCK_PREFIX.with_suffix(".hexdump.txt"),
                SSE_HOT_BLOCK_PREFIX.with_suffix(".benchmark.json"),
                SSE_HOT_BLOCK_PREFIX.with_suffix(".benchmark.md"),
            ),
            description="Run the full SSE parity suite and TGPKHOT1 export.",
        ),
        CommandTask(
            name="webtransport_perf_suite",
            argv=_python_command(
                "pkgs/core/tigrbl_tests/benchmarks/tigrbl_webtransport_perf_suite.py",
            ),
            artifact_paths=(
                WEBTRANSPORT_RESULTS_JSON,
                WEBTRANSPORT_KERNEL_JSON,
                WEBTRANSPORT_KERNEL_MD,
                WEBTRANSPORT_TIGRBL_TRANSPORT_CALL_GRAPH_JSON,
                WEBTRANSPORT_TIGRBL_CALL_GRAPH_JSON,
                WEBTRANSPORT_HOT_BLOCK_PREFIX.with_suffix(".bin"),
                WEBTRANSPORT_HOT_BLOCK_PREFIX.with_suffix(".summary.json"),
                WEBTRANSPORT_HOT_BLOCK_PREFIX.with_suffix(".hexdump.txt"),
                WEBTRANSPORT_HOT_BLOCK_PREFIX.with_suffix(".benchmark.json"),
                WEBTRANSPORT_HOT_BLOCK_PREFIX.with_suffix(".benchmark.md"),
            ),
            description="Run the full webtransport Tigrbl suite and TGPKHOT1 export.",
        ),
    ]


def _ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _run_task(task: CommandTask, *, attempt: int = 1) -> dict[str, Any]:
    result = subprocess.run(
        task.argv,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    payload = {
        "name": task.name,
        "description": task.description,
        "argv": list(task.argv),
        "attempt": int(attempt),
        "returncode": int(result.returncode),
        "stdout": result.stdout,
        "stderr": result.stderr,
        "artifacts": [str(path) for path in task.artifact_paths],
    }
    if result.returncode != 0:
        raise RuntimeError(
            f"task {task.name!r} failed with exit code {result.returncode}\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return payload


def _copy_kernel_benchmark_artifacts() -> list[Path]:
    copied: list[Path] = []
    for src, dest in (
        (TMP_DIR / "kernel-plan-benchmark.json", KERNEL_BENCHMARK_JSON),
        (TMP_DIR / "kernel-plan-benchmark.md", KERNEL_BENCHMARK_MD),
    ):
        _ensure_dir(dest)
        shutil.copyfile(src, dest)
        copied.append(dest)
    return copied


def _hexdump(payload: bytes, *, width: int = 16) -> str:
    lines: list[str] = []
    for offset in range(0, len(payload), width):
        chunk = payload[offset : offset + width]
        left = " ".join(f"{value:02x}" for value in chunk[:8])
        right = " ".join(f"{value:02x}" for value in chunk[8:])
        hex_part = f"{left:<23}  {right:<23}".rstrip()
        text = "".join(chr(value) if 32 <= value < 127 else "." for value in chunk)
        lines.append(f"{offset:08x}  {hex_part:<48}  {text}")
    return "\n".join(lines) + ("\n" if lines else "")


def _summarize_hot_block(payload: bytes) -> dict[str, Any]:
    header_size = struct.calcsize("<8sHHIHHHHHHH")
    entry_size = struct.calcsize("<HBBII")
    (
        magic,
        version,
        max_width_bits,
        total_bytes,
        section_count,
        directory_offset,
        atom_count,
        segment_count,
        program_count,
        error_profile_count,
        route_entry_count,
    ) = struct.unpack("<8sHHIHHHHHHH", payload[:header_size])
    sections: list[dict[str, Any]] = []
    for index in range(section_count):
        start = directory_offset + (index * entry_size)
        end = start + entry_size
        section_id, width_bits, flags, count, offset = struct.unpack(
            "<HBBII", payload[start:end]
        )
        next_offset = (
            struct.unpack("<HBBII", payload[end : end + entry_size])[4]
            if index + 1 < section_count
            else len(payload)
        )
        sections.append(
            {
                "index": int(index),
                "section_id": int(section_id),
                "name": _HOT_BLOCK_SECTION_NAMES.get(int(section_id), f"unknown:{section_id}"),
                "width_bits": int(width_bits),
                "flags": int(flags),
                "count": int(count),
                "offset": int(offset),
                "byte_length": int(next_offset - offset),
            }
        )
    return {
        "header": {
            "magic": magic.decode("ascii"),
            "version": int(version),
            "max_width_bits": int(max_width_bits),
            "total_bytes": int(total_bytes),
            "section_count": int(section_count),
            "directory_offset": int(directory_offset),
            "atom_count": int(atom_count),
            "segment_count": int(segment_count),
            "program_count": int(program_count),
            "error_profile_count": int(error_profile_count),
            "route_entry_count": int(route_entry_count),
        },
        "sections": sections,
    }


def _hot_block_benchmark_payload(hot_block_bytes: bytes, packed: Any) -> dict[str, Any]:
    measurement = getattr(packed, "measurement", None) or measure_packed_kernel(packed)
    summary = _summarize_hot_block(hot_block_bytes)
    return {
        "artifact": {
            "magic": "TGPKHOT1",
            "raw_bytes": len(hot_block_bytes),
            "compressed_bytes": len(gzip.compress(hot_block_bytes, compresslevel=9, mtime=0)),
        },
        "header": summary["header"],
        "measurement": {
            "raw_bytes": int(measurement.raw_bytes),
            "compressed_bytes": int(measurement.compressed_bytes),
            "segment_count": int(measurement.segment_count),
            "step_count": int(measurement.step_count),
            "phase_tree_node_count": int(measurement.phase_tree_node_count),
            "proto_count": int(measurement.proto_count),
            "selector_count": int(measurement.selector_count),
            "op_count": int(measurement.op_count),
            "exact_route_count": int(measurement.exact_route_count),
            "hot_op_count": int(measurement.hot_op_count),
            "compact_step_count": int(measurement.compact_step_count),
            "compact_segment_count": int(measurement.compact_segment_count),
            "compact_program_segment_ref_count": int(
                measurement.compact_program_segment_ref_count
            ),
            "compact_route_entry_count": int(measurement.compact_route_entry_count),
            "shared_error_profile_count": int(measurement.shared_error_profile_count),
            "externalized_prelude_step_count": int(
                measurement.externalized_prelude_step_count
            ),
            "max_index_width_bits": int(measurement.max_index_width_bits),
        },
    }


def _render_hot_block_benchmark_md(surface: str, payload: dict[str, Any]) -> str:
    header = payload["header"]
    measurement = payload["measurement"]
    artifact = payload["artifact"]
    return (
        f"# TGPKHOT1 Benchmark ({surface})\n\n"
        f"- raw bytes: {artifact['raw_bytes']}\n"
        f"- compressed bytes: {artifact['compressed_bytes']}\n"
        f"- section count: {header['section_count']}\n"
        f"- max width bits: {header['max_width_bits']}\n"
        f"- atom count: {header['atom_count']}\n"
        f"- segment count: {header['segment_count']}\n"
        f"- program count: {header['program_count']}\n"
        f"- route entry count: {header['route_entry_count']}\n"
        f"- compact steps: {measurement['compact_step_count']}\n"
        f"- compact segments: {measurement['compact_segment_count']}\n"
        f"- compact program segment refs: {measurement['compact_program_segment_ref_count']}\n"
        f"- compact route entries: {measurement['compact_route_entry_count']}\n"
        f"- externalized prelude steps: {measurement['externalized_prelude_step_count']}\n"
        f"- max index width bits: {measurement['max_index_width_bits']}\n"
    )


def _export_unary_hot_block(prefix: Path) -> list[Path]:
    async def _build() -> tuple[bytes, Any]:
        db_path = TMP_DIR / f"hot-path-perf-suite-tgpkhot1-{uuid.uuid4().hex}.sqlite3"
        app = _build_tigrbl_parity_app(db_path)
        try:
            await _initialize_tigrbl_parity_app(app)
            plan = build_kernel_plan(app)
            packed = getattr(plan, "packed", None)
            if packed is None:
                raise RuntimeError("kernel plan build did not yield a packed kernel")
            hot_block_bytes = getattr(packed, "hot_block_bytes", b"")
            if not hot_block_bytes:
                raise RuntimeError("packed kernel did not carry TGPKHOT1 bytes")
            return hot_block_bytes, packed
        finally:
            await _dispose_tigrbl_parity_app(app)
            if db_path.exists():
                try:
                    db_path.unlink()
                except OSError:
                    pass

    hot_block_bytes, packed = asyncio.run(_build())
    hot_block_view = load_packed_kernel_hot_block(hot_block_bytes)
    summary = _summarize_hot_block(hot_block_bytes)
    summary_payload = {
        "artifact": {
            "path": str(prefix.with_suffix(".bin")),
            "bytes": len(hot_block_bytes),
        },
        "header": summary["header"],
        "sections": summary["sections"],
        "loaded_view_counts": {
            "atom_count": len(tuple(hot_block_view.get("atom_opcode_ids", ()) or ())),
            "segment_count": len(tuple(hot_block_view.get("segment_step_offsets", ()) or ())),
            "program_count": len(tuple(hot_block_view.get("program_hot_runner_ids", ()) or ())),
            "route_entry_count": int(hot_block_view.get("route_entry_count", 0)),
        },
    }
    benchmark_payload = _hot_block_benchmark_payload(hot_block_bytes, packed)

    bin_path = prefix.with_suffix(".bin")
    summary_path = prefix.with_suffix(".summary.json")
    hexdump_path = prefix.with_suffix(".hexdump.txt")
    benchmark_json_path = prefix.with_suffix(".benchmark.json")
    benchmark_md_path = prefix.with_suffix(".benchmark.md")
    for path in (bin_path, summary_path, hexdump_path, benchmark_json_path, benchmark_md_path):
        _ensure_dir(path)
    bin_path.write_bytes(hot_block_bytes)
    summary_path.write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")
    hexdump_path.write_text(_hexdump(hot_block_bytes), encoding="utf-8")
    benchmark_json_path.write_text(
        json.dumps(benchmark_payload, indent=2), encoding="utf-8"
    )
    benchmark_md_path.write_text(
        _render_hot_block_benchmark_md("rest_unary", benchmark_payload),
        encoding="utf-8",
    )
    return [bin_path, summary_path, hexdump_path, benchmark_json_path, benchmark_md_path]


def _required_missing_surfaces() -> list[dict[str, str]]:
    expected_files = {
        "fastapi_rest_unary_call_graph": FASTAPI_CALL_GRAPH_JSON,
        "streaming_parity_benchmark": STREAMING_RESULTS_JSON,
        "streaming_kernel_benchmark": STREAMING_KERNEL_JSON,
        "streaming_tigrbl_call_graph": STREAMING_TIGRBL_CALL_GRAPH_JSON,
        "streaming_fastapi_call_graph": STREAMING_FASTAPI_CALL_GRAPH_JSON,
        "streaming_tgpkhot1_bin": STREAMING_HOT_BLOCK_PREFIX.with_suffix(".bin"),
        "streaming_tgpkhot1_benchmark": STREAMING_HOT_BLOCK_PREFIX.with_suffix(".benchmark.json"),
        "websocket_parity_benchmark": WEBSOCKET_RESULTS_JSON,
        "websocket_kernel_benchmark": WEBSOCKET_KERNEL_JSON,
        "websocket_transport_tigrbl_call_graph": WEBSOCKET_TIGRBL_TRANSPORT_CALL_GRAPH_JSON,
        "websocket_transport_fastapi_call_graph": WEBSOCKET_FASTAPI_TRANSPORT_CALL_GRAPH_JSON,
        "websocket_tigrbl_call_graph": WEBSOCKET_TIGRBL_CALL_GRAPH_JSON,
        "websocket_fastapi_call_graph": WEBSOCKET_FASTAPI_CALL_GRAPH_JSON,
        "websocket_tgpkhot1_bin": WEBSOCKET_HOT_BLOCK_PREFIX.with_suffix(".bin"),
        "websocket_tgpkhot1_benchmark": WEBSOCKET_HOT_BLOCK_PREFIX.with_suffix(".benchmark.json"),
        "sse_parity_benchmark": SSE_RESULTS_JSON,
        "sse_kernel_benchmark": SSE_KERNEL_JSON,
        "sse_transport_tigrbl_call_graph": SSE_TIGRBL_TRANSPORT_CALL_GRAPH_JSON,
        "sse_transport_fastapi_call_graph": SSE_FASTAPI_TRANSPORT_CALL_GRAPH_JSON,
        "sse_tigrbl_call_graph": SSE_TIGRBL_CALL_GRAPH_JSON,
        "sse_fastapi_call_graph": SSE_FASTAPI_CALL_GRAPH_JSON,
        "sse_tgpkhot1_bin": SSE_HOT_BLOCK_PREFIX.with_suffix(".bin"),
        "sse_tgpkhot1_benchmark": SSE_HOT_BLOCK_PREFIX.with_suffix(".benchmark.json"),
        "webtransport_benchmark": WEBTRANSPORT_RESULTS_JSON,
        "webtransport_kernel_benchmark": WEBTRANSPORT_KERNEL_JSON,
        "webtransport_transport_tigrbl_call_graph": WEBTRANSPORT_TIGRBL_TRANSPORT_CALL_GRAPH_JSON,
        "webtransport_tigrbl_call_graph": WEBTRANSPORT_TIGRBL_CALL_GRAPH_JSON,
        "webtransport_tgpkhot1_bin": WEBTRANSPORT_HOT_BLOCK_PREFIX.with_suffix(".bin"),
        "webtransport_tgpkhot1_benchmark": WEBTRANSPORT_HOT_BLOCK_PREFIX.with_suffix(".benchmark.json"),
    }
    missing: list[dict[str, str]] = []
    for surface, artifact_path in expected_files.items():
        if not artifact_path.exists():
            missing.append(
                {
                    "surface": surface,
                    "reason": "required benchmark or artifact producer is not implemented yet",
                    "expected_artifact": str(artifact_path),
                }
            )
    return missing


def _read_json(path: Path) -> dict[str, Any] | list[Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _as_float(value: Any) -> float:
    return float(value) if isinstance(value, (int, float)) else 0.0


def _as_int(value: Any) -> int | None:
    return int(value) if isinstance(value, (int, float)) else None


def _surface_ops_250(
    path: Path,
    *,
    tigrbl_only: bool = False,
) -> dict[str, Any]:
    payload = _read_json(path)
    if not isinstance(payload, dict):
        return {}
    out: dict[str, Any] = {}
    for scenario in ("transport_only", "db_backed"):
        scenario_payload = payload.get(scenario, {})
        if not isinstance(scenario_payload, dict):
            continue
        ops_250 = scenario_payload.get("250", {})
        if not isinstance(ops_250, dict):
            continue
        row = {
            "tigrbl_ops_per_second": _as_float(
                ((ops_250.get("tigrbl", {}) or {}).get("ops_per_second"))
            )
        }
        if not tigrbl_only:
            row["fastapi_ops_per_second"] = _as_float(
                ((ops_250.get("fastapi", {}) or {}).get("ops_per_second"))
            )
        out[scenario] = row
    return out


def _hot_block_summary(path: Path) -> dict[str, int] | None:
    payload = _read_json(path)
    if not isinstance(payload, dict):
        return None
    artifact = payload.get("artifact", {})
    if not isinstance(artifact, dict):
        return None
    raw_bytes = _as_int(artifact.get("raw_bytes"))
    compressed_bytes = _as_int(artifact.get("compressed_bytes"))
    if raw_bytes is None or compressed_bytes is None:
        return None
    return {
        "raw_bytes": raw_bytes,
        "compressed_bytes": compressed_bytes,
    }


def _load_previous_locked_baselines() -> dict[str, dict[str, Any]]:
    payload = _read_json(SUITE_MANIFEST_JSON)
    if not isinstance(payload, dict):
        return {}
    baselines = payload.get("locked_baselines", {})
    return baselines if isinstance(baselines, dict) else {}


def _dynamic_baseline_from_surface_summary(
    surface_name: str, summary: Mapping[str, Any]
) -> dict[str, Any] | None:
    transport = summary.get("transport_only", {})
    db_backed = summary.get("db_backed", {})
    tgpkhot1 = summary.get("tgpkhot1", {})
    if not (
        isinstance(transport, dict)
        and isinstance(db_backed, dict)
        and isinstance(tgpkhot1, dict)
    ):
        return None
    transport_ops = _as_float(transport.get("tigrbl_ops_per_second"))
    db_ops = _as_float(db_backed.get("tigrbl_ops_per_second"))
    raw_bytes = _as_int(tgpkhot1.get("raw_bytes"))
    if raw_bytes is None:
        return None
    return {
        "transport_only_ops_per_second": transport_ops,
        "db_backed_ops_per_second": db_ops,
        "raw_bytes_ceiling": raw_bytes,
        "baseline_source": f"{surface_name}_current_run_lock",
    }


def _resolve_locked_baselines(summary: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    locked: dict[str, dict[str, Any]] = {
        key: {**value, "baseline_source": "locked_may_2_2026"}
        for key, value in LOCKED_EXISTING_BASELINES.items()
    }
    previous = _load_previous_locked_baselines()
    for surface_name in ("sse", "webtransport"):
        previous_surface = previous.get(surface_name)
        if isinstance(previous_surface, dict):
            locked[surface_name] = dict(previous_surface)
            continue
        surface_summary = summary.get(surface_name, {})
        if isinstance(surface_summary, dict):
            current = _dynamic_baseline_from_surface_summary(
                surface_name, surface_summary
            )
            if current is not None:
                locked[surface_name] = current
    return locked


def _unary_gate_status(summary: Mapping[str, Any], baseline: Mapping[str, Any]) -> dict[str, Any]:
    unary = summary.get("unary", {})
    if not isinstance(unary, dict):
        return {"available": False}
    tgpkhot1 = unary.get("tgpkhot1", {})
    raw_bytes_value = (
        _as_int(tgpkhot1.get("raw_bytes")) if isinstance(tgpkhot1, dict) else None
    )
    raw_ceiling = _as_int(baseline.get("raw_bytes_ceiling"))
    rest_floor = _as_float(baseline.get("rest_ops_per_second"))
    jsonrpc_floor = _as_float(baseline.get("jsonrpc_ops_per_second"))
    rest_ops = _as_float(unary.get("tigrbl_rest_ops_per_second"))
    jsonrpc_ops = _as_float(unary.get("tigrbl_jsonrpc_ops_per_second"))
    return {
        "available": True,
        "rest_ops_per_second": rest_ops,
        "jsonrpc_ops_per_second": jsonrpc_ops,
        "raw_bytes": raw_bytes_value,
        "raw_bytes_ceiling": raw_ceiling,
        "rest_floor": rest_floor,
        "jsonrpc_floor": jsonrpc_floor,
        "baseline_source": str(baseline.get("baseline_source", "locked")),
        "rest_pass": rest_ops >= rest_floor,
        "jsonrpc_pass": jsonrpc_ops >= jsonrpc_floor,
        "raw_bytes_pass": (
            raw_bytes_value is not None
            and raw_ceiling is not None
            and raw_bytes_value <= raw_ceiling
        ),
    }


def _two_scenario_gate_status(
    surface_name: str,
    summary: Mapping[str, Any],
    baseline: Mapping[str, Any],
) -> dict[str, Any]:
    surface = summary.get(surface_name, {})
    if not isinstance(surface, dict):
        return {"available": False}
    transport = surface.get("transport_only", {})
    db_backed = surface.get("db_backed", {})
    tgpkhot1 = surface.get("tgpkhot1", {})
    if not (
        isinstance(transport, dict)
        and isinstance(db_backed, dict)
        and isinstance(tgpkhot1, dict)
    ):
        return {"available": False}
    transport_floor = _as_float(baseline.get("transport_only_ops_per_second"))
    db_floor = _as_float(baseline.get("db_backed_ops_per_second"))
    raw_ceiling = _as_int(baseline.get("raw_bytes_ceiling"))
    transport_ops = _as_float(transport.get("tigrbl_ops_per_second"))
    db_ops = _as_float(db_backed.get("tigrbl_ops_per_second"))
    raw_bytes = _as_int(tgpkhot1.get("raw_bytes"))
    return {
        "available": True,
        "transport_only_ops_per_second": transport_ops,
        "db_backed_ops_per_second": db_ops,
        "transport_only_floor": transport_floor,
        "db_backed_floor": db_floor,
        "raw_bytes": raw_bytes,
        "raw_bytes_ceiling": raw_ceiling,
        "baseline_source": str(baseline.get("baseline_source", "locked")),
        "transport_only_pass": transport_ops >= transport_floor,
        "db_backed_pass": db_ops >= db_floor,
        "raw_bytes_pass": (
            raw_bytes is not None and raw_ceiling is not None and raw_bytes <= raw_ceiling
        ),
    }


def _surface_summary() -> dict[str, Any]:
    summary: dict[str, Any] = {}
    unary = _read_json(KERNEL_BENCHMARK_JSON)
    if isinstance(unary, dict):
        candidate = unary.get("candidate", {})
        if isinstance(candidate, dict):
            tigrbl = candidate.get("tigrbl", {})
            fastapi = candidate.get("fastapi", {})
            summary["unary"] = {
                "tigrbl_rest_ops_per_second": float(
                    ((tigrbl or {}).get("rest_unary", {}) or {}).get("ops_per_second", 0.0)
                ),
                "tigrbl_jsonrpc_ops_per_second": float(
                    ((tigrbl or {}).get("jsonrpc_unary", {}) or {}).get("ops_per_second", 0.0)
                ),
                "fastapi_rest_ops_per_second": float(
                    ((fastapi or {}).get("rest_unary", {}) or {}).get("ops_per_second", 0.0)
                ),
            }
    for surface_name, path, tigrbl_only in (
        ("streaming", STREAMING_RESULTS_JSON, False),
        ("websocket", WEBSOCKET_RESULTS_JSON, False),
        ("sse", SSE_RESULTS_JSON, False),
        ("webtransport", WEBTRANSPORT_RESULTS_JSON, True),
    ):
        surface_ops = _surface_ops_250(path, tigrbl_only=tigrbl_only)
        if surface_ops:
            summary[surface_name] = dict(surface_ops)
    for surface_name, path in {
        "unary": HOT_BLOCK_PREFIX.with_suffix(".benchmark.json"),
        "streaming": STREAMING_HOT_BLOCK_PREFIX.with_suffix(".benchmark.json"),
        "websocket": WEBSOCKET_HOT_BLOCK_PREFIX.with_suffix(".benchmark.json"),
        "sse": SSE_HOT_BLOCK_PREFIX.with_suffix(".benchmark.json"),
        "webtransport": WEBTRANSPORT_HOT_BLOCK_PREFIX.with_suffix(".benchmark.json"),
    }.items():
        artifact = _hot_block_summary(path)
        if artifact is None:
            continue
        summary.setdefault(surface_name, {})
        summary[surface_name]["tgpkhot1"] = dict(artifact)
    return summary


def _render_suite_report(manifest: dict[str, Any]) -> str:
    gates = manifest.get("gates", {})
    summary = manifest.get("summary", {})
    lines = [
        "# Hot-Path Perf Suite",
        "",
        "## Gates",
    ]
    unary = gates.get("unary", {}) if isinstance(gates, dict) else {}
    if unary.get("available"):
        lines.extend(
            [
                f"- `REST unary >= {unary.get('rest_floor', 0.0):.2f} ops/s`: {'PASS' if unary.get('rest_pass') else 'FAIL'} ({unary.get('rest_ops_per_second', 0.0):.2f})",
                f"- `JSON-RPC unary >= {unary.get('jsonrpc_floor', 0.0):.2f} ops/s`: {'PASS' if unary.get('jsonrpc_pass') else 'FAIL'} ({unary.get('jsonrpc_ops_per_second', 0.0):.2f})",
                f"- `Unary TGPKHOT1 raw_bytes <= {unary.get('raw_bytes_ceiling')}`: {'PASS' if unary.get('raw_bytes_pass') else 'FAIL'} ({unary.get('raw_bytes')})",
            ]
        )
    else:
        lines.append("- unary gates: unavailable")
    for surface_name in ("streaming", "websocket", "sse", "webtransport"):
        gate = gates.get(surface_name, {}) if isinstance(gates, dict) else {}
        if not isinstance(gate, dict) or not gate.get("available"):
            lines.append(f"- {surface_name} gates: unavailable")
            continue
        lines.extend(
            [
                f"- `{surface_name} transport-only >= {gate.get('transport_only_floor', 0.0):.2f} ops/s`: {'PASS' if gate.get('transport_only_pass') else 'FAIL'} ({gate.get('transport_only_ops_per_second', 0.0):.2f})",
                f"- `{surface_name} db-backed >= {gate.get('db_backed_floor', 0.0):.2f} ops/s`: {'PASS' if gate.get('db_backed_pass') else 'FAIL'} ({gate.get('db_backed_ops_per_second', 0.0):.2f})",
                f"- `{surface_name} TGPKHOT1 raw_bytes <= {gate.get('raw_bytes_ceiling')}`: {'PASS' if gate.get('raw_bytes_pass') else 'FAIL'} ({gate.get('raw_bytes')})",
            ]
        )
    lines.extend(["", "## Throughput Summary"])
    unary_summary = summary.get("unary", {}) if isinstance(summary, dict) else {}
    if unary_summary:
        lines.append(
            f"- unary: tigrbl REST={unary_summary.get('tigrbl_rest_ops_per_second', 0.0):.2f}, "
            f"tigrbl JSON-RPC={unary_summary.get('tigrbl_jsonrpc_ops_per_second', 0.0):.2f}, "
            f"fastapi REST={unary_summary.get('fastapi_rest_ops_per_second', 0.0):.2f}"
        )
    for surface_name in ("streaming", "websocket", "sse", "webtransport"):
        surface = summary.get(surface_name, {}) if isinstance(summary, dict) else {}
        if not isinstance(surface, dict):
            continue
        transport = surface.get("transport_only", {})
        db_backed = surface.get("db_backed", {})
        tgpkhot1 = surface.get("tgpkhot1", {})
        if transport:
            line = (
                f"- {surface_name} transport-only 250: "
                f"tigrbl={transport.get('tigrbl_ops_per_second', 0.0):.2f}"
            )
            if "fastapi_ops_per_second" in transport:
                line += f", fastapi={transport.get('fastapi_ops_per_second', 0.0):.2f}"
            lines.append(line)
        if db_backed:
            line = (
                f"- {surface_name} db-backed 250: "
                f"tigrbl={db_backed.get('tigrbl_ops_per_second', 0.0):.2f}"
            )
            if "fastapi_ops_per_second" in db_backed:
                line += f", fastapi={db_backed.get('fastapi_ops_per_second', 0.0):.2f}"
            lines.append(line)
        if tgpkhot1:
            lines.append(
                f"- {surface_name} TGPKHOT1: raw={tgpkhot1.get('raw_bytes')}, compressed={tgpkhot1.get('compressed_bytes')}"
            )
    locked_baselines = manifest.get("locked_baselines", {})
    if isinstance(locked_baselines, dict):
        lines.extend(["", "## Locked Baselines"])
        for surface_name, baseline in locked_baselines.items():
            if not isinstance(baseline, dict):
                continue
            lines.append(
                f"- {surface_name}: source={baseline.get('baseline_source', 'locked')}, "
                f"transport={baseline.get('transport_only_ops_per_second', baseline.get('rest_ops_per_second', 0.0))}, "
                f"db/jsonrpc={baseline.get('db_backed_ops_per_second', baseline.get('jsonrpc_ops_per_second', 0.0))}, "
                f"raw_bytes={baseline.get('raw_bytes_ceiling')}"
            )
    lines.extend(["", "## Tasks"])
    for task in manifest["tasks"]:
        lines.append(f"- `{task['name']}`: exit `{task['returncode']}`")
    lines.extend(["", "## Artifacts"])
    for artifact in manifest["artifacts"]:
        lines.append(f"- `{artifact}`")
    missing = manifest.get("missing_surfaces", [])
    if missing:
        lines.extend(["", "## Missing Surfaces"])
        for item in missing:
            lines.append(
                f"- `{item['surface']}`: {item['reason']} ({item['expected_artifact']})"
            )
    return "\n".join(lines) + "\n"


def run_suite(*, allow_missing_surfaces: bool) -> dict[str, Any]:
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    PERF_DIR.mkdir(parents=True, exist_ok=True)
    tasks = _default_tasks()
    task_by_name = {task.name: task for task in tasks}
    task_attempts: dict[str, int] = {}
    task_results_by_name: dict[str, dict[str, Any]] = {}

    def _evaluate_current_state() -> tuple[dict[str, Any], list[str], list[dict[str, Any]]]:
        copied_artifacts = _copy_kernel_benchmark_artifacts()
        hot_block_artifacts = _export_unary_hot_block(HOT_BLOCK_PREFIX)
        task_results = [task_results_by_name[task.name] for task in tasks]
        artifacts = [
            *(str(path) for path in copied_artifacts),
            *(artifact for task_result in task_results for artifact in task_result["artifacts"]),
            *(str(path) for path in hot_block_artifacts),
        ]
        seen: set[str] = set()
        unique_artifacts = [
            path for path in artifacts if not (path in seen or seen.add(path))
        ]
        missing_surfaces = _required_missing_surfaces()
        summary = _surface_summary()
        locked_baselines = _resolve_locked_baselines(summary)
        gates = {
            "unary": _unary_gate_status(
                summary,
                locked_baselines.get("unary", LOCKED_EXISTING_BASELINES["unary"]),
            ),
            "streaming": _two_scenario_gate_status(
                "streaming",
                summary,
                locked_baselines.get("streaming", LOCKED_EXISTING_BASELINES["streaming"]),
            ),
            "websocket": _two_scenario_gate_status(
                "websocket",
                summary,
                locked_baselines.get("websocket", LOCKED_EXISTING_BASELINES["websocket"]),
            ),
            "sse": _two_scenario_gate_status(
                "sse",
                summary,
                locked_baselines.get("sse", {}),
            ),
            "webtransport": _two_scenario_gate_status(
                "webtransport",
                summary,
                locked_baselines.get("webtransport", {}),
            ),
        }
        manifest = {
            "suite": "hot_path_perf_suite",
            "cwd": str(ROOT),
            "python": sys.executable,
            "tasks": task_results,
            "artifacts": unique_artifacts,
            "missing_surfaces": missing_surfaces,
            "locked_baselines": locked_baselines,
            "gates": gates,
            "summary": summary,
        }
        failures: list[str] = []
        unary = gates.get("unary", {})
        if isinstance(unary, dict) and unary.get("available") and not (
            unary.get("rest_pass")
            and unary.get("jsonrpc_pass")
            and unary.get("raw_bytes_pass")
        ):
            failures.append(
                "unary "
                f"rest={unary.get('rest_ops_per_second', 0.0):.2f}/{unary.get('rest_floor', 0.0):.2f} "
                f"jsonrpc={unary.get('jsonrpc_ops_per_second', 0.0):.2f}/{unary.get('jsonrpc_floor', 0.0):.2f} "
                f"raw={unary.get('raw_bytes')}/{unary.get('raw_bytes_ceiling')}"
            )
        for surface_name in ("streaming", "websocket", "sse", "webtransport"):
            gate = gates.get(surface_name, {})
            if not isinstance(gate, dict) or not gate.get("available"):
                continue
            if not (
                gate.get("transport_only_pass")
                and gate.get("db_backed_pass")
                and gate.get("raw_bytes_pass")
            ):
                failures.append(
                    f"{surface_name} "
                    f"transport={gate.get('transport_only_ops_per_second', 0.0):.2f}/{gate.get('transport_only_floor', 0.0):.2f} "
                    f"db={gate.get('db_backed_ops_per_second', 0.0):.2f}/{gate.get('db_backed_floor', 0.0):.2f} "
                    f"raw={gate.get('raw_bytes')}/{gate.get('raw_bytes_ceiling')}"
                )
        return manifest, failures, missing_surfaces

    for task in tasks:
        task_attempts[task.name] = 1
        task_results_by_name[task.name] = _run_task(task, attempt=1)

    manifest, failures, missing_surfaces = _evaluate_current_state()

    retry_round = 0
    while failures and retry_round < MAX_BENCHMARK_RETRIES:
        rerun_names: list[str] = []
        gates = manifest.get("gates", {})
        unary = gates.get("unary", {}) if isinstance(gates, dict) else {}
        if isinstance(unary, dict) and unary.get("available") and not (
            unary.get("rest_pass")
            and unary.get("jsonrpc_pass")
            and unary.get("raw_bytes_pass")
        ):
            rerun_names.extend(BENCHMARK_RERUN_TASKS["unary"])
        for surface_name in ("streaming", "websocket", "sse", "webtransport"):
            gate = gates.get(surface_name, {}) if isinstance(gates, dict) else {}
            if not isinstance(gate, dict) or not gate.get("available"):
                continue
            if not (
                gate.get("transport_only_pass")
                and gate.get("db_backed_pass")
                and gate.get("raw_bytes_pass")
            ):
                rerun_names.extend(BENCHMARK_RERUN_TASKS[surface_name])
        rerun_names = list(dict.fromkeys(rerun_names))
        if not rerun_names:
            break
        retry_round += 1
        time.sleep(1.0)
        for task_name in rerun_names:
            task = task_by_name.get(task_name)
            if task is None:
                continue
            attempt = int(task_attempts.get(task_name, 1)) + 1
            task_attempts[task_name] = attempt
            task_results_by_name[task_name] = _run_task(task, attempt=attempt)
        manifest, failures, missing_surfaces = _evaluate_current_state()

    SUITE_MANIFEST_JSON.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    SUITE_REPORT_MD.write_text(_render_suite_report(manifest), encoding="utf-8")
    if missing_surfaces and not allow_missing_surfaces:
        names = ", ".join(item["surface"] for item in missing_surfaces)
        raise MissingSurfaceError(
            f"required perf surfaces are still missing: {names}"
        )
    if failures:
        raise RuntimeError("perf gates failed: " + "; ".join(failures))
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run the hot-path unary, streaming, websocket, SSE, and webtransport "
            "perf rails, export TGPKHOT1 artifacts, and fail closed if required "
            "artifact surfaces or locked throughput/raw-byte gates regress."
        )
    )
    parser.add_argument(
        "--allow-missing-surfaces",
        action="store_true",
        help="continue writing the manifest/report even if one of the required perf surfaces is still missing",
    )
    args = parser.parse_args()
    run_suite(allow_missing_surfaces=bool(args.allow_missing_surfaces))


if __name__ == "__main__":
    main()
