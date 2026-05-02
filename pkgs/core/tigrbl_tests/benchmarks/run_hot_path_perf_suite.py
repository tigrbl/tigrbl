from __future__ import annotations

import argparse
import asyncio
import gzip
import json
import shutil
import sqlite3
import struct
import subprocess
import sys
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

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


class MissingSurfaceError(RuntimeError):
    pass


@dataclass(frozen=True)
class CommandTask:
    name: str
    argv: tuple[str, ...]
    artifact_paths: tuple[Path, ...]
    description: str


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
    app = TigrblApp(engine=sqlitef(str(db_path), async_=False))
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
            ),
            description="Run the 250-op unary parity benchmark.",
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
    ]


def _ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _run_task(task: CommandTask) -> dict[str, Any]:
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
        "streaming_parity_benchmark": PERF_DIR / "benchmark_results_streaming_uvicorn.json",
        "streaming_call_graph": PERF_DIR / "tigrbl_streaming_call_graph_250_ops.json",
        "streaming_tgpkhot1_bin": PERF_DIR / "tgpkhot1-benchmark-streaming.bin",
        "streaming_tgpkhot1_benchmark": PERF_DIR / "tgpkhot1-benchmark-streaming.benchmark.json",
        "websocket_parity_benchmark": PERF_DIR / "benchmark_results_websocket_uvicorn.json",
        "websocket_call_graph": PERF_DIR / "tigrbl_websocket_call_graph_250_ops.json",
        "websocket_tgpkhot1_bin": PERF_DIR / "tgpkhot1-benchmark-websocket.bin",
        "websocket_tgpkhot1_benchmark": PERF_DIR / "tgpkhot1-benchmark-websocket.benchmark.json",
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


def _render_suite_report(manifest: dict[str, Any]) -> str:
    lines = [
        "# Hot-Path Perf Suite",
        "",
        "## Tasks",
    ]
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
    task_results = [_run_task(task) for task in _default_tasks()]
    copied_artifacts = _copy_kernel_benchmark_artifacts()
    hot_block_artifacts = _export_unary_hot_block(HOT_BLOCK_PREFIX)
    artifacts = [
        *(str(path) for path in copied_artifacts),
        *(artifact for task in task_results for artifact in task["artifacts"]),
        *(str(path) for path in hot_block_artifacts),
    ]
    seen: set[str] = set()
    unique_artifacts = [path for path in artifacts if not (path in seen or seen.add(path))]
    missing_surfaces = _required_missing_surfaces()
    manifest = {
        "suite": "hot_path_perf_suite",
        "cwd": str(ROOT),
        "python": sys.executable,
        "tasks": task_results,
        "artifacts": unique_artifacts,
        "missing_surfaces": missing_surfaces,
    }
    SUITE_MANIFEST_JSON.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    SUITE_REPORT_MD.write_text(_render_suite_report(manifest), encoding="utf-8")
    if missing_surfaces and not allow_missing_surfaces:
        names = ", ".join(item["surface"] for item in missing_surfaces)
        raise MissingSurfaceError(
            f"required perf surfaces are still missing: {names}"
        )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run the hot-path unary perf rails, export TGPKHOT1 artifacts, and "
            "fail closed if required stream/websocket or FastAPI call-graph surfaces "
            "are still missing."
        )
    )
    parser.add_argument(
        "--allow-missing-surfaces",
        action="store_true",
        help="complete the currently implemented unary suite even if stream/websocket or FastAPI call-graph rails are still missing",
    )
    args = parser.parse_args()
    run_suite(allow_missing_surfaces=bool(args.allow_missing_surfaces))


if __name__ == "__main__":
    main()
