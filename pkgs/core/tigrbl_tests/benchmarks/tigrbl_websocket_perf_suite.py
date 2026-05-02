from __future__ import annotations

import asyncio
import cProfile
import gzip
import json
import pstats
import struct
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter
from typing import Any, Awaitable, Callable

from tigrbl_kernel import build_kernel_plan, load_packed_kernel_hot_block, measure_packed_kernel
from tigrbl_kernel.measure import _HOT_BLOCK_SECTION_NAMES

from tests.perf.helper_websocket_apps import (
    create_fastapi_websocket_db_app,
    create_fastapi_websocket_transport_app,
    create_tigrbl_websocket_db_app,
    create_tigrbl_websocket_transport_app,
    dispose_tigrbl_websocket_app,
    fetch_websocket_names,
    initialize_tigrbl_websocket_app,
)

ROOT = Path(__file__).resolve().parents[4]
PERF_DIR = ROOT / "pkgs" / "core" / "tigrbl_tests" / "tests" / "perf"
TMP_DIR = ROOT / ".tmp"
RESULTS_PATH = PERF_DIR / "benchmark_results_websocket_uvicorn.json"
KERNEL_JSON_PATH = PERF_DIR / "kernel-plan-benchmark-websocket.json"
KERNEL_MD_PATH = PERF_DIR / "kernel-plan-benchmark-websocket.md"
TIGRBL_CALL_GRAPH_PATH = PERF_DIR / "tigrbl_websocket_call_graph_250_ops.json"
FASTAPI_CALL_GRAPH_PATH = PERF_DIR / "fastapi_websocket_call_graph_250_ops.json"
HOT_BLOCK_PREFIX = PERF_DIR / "tgpkhot1-benchmark-websocket"
OPS_COUNTS = (25, 250)
WARMUP_OPS = 5
TOP_FUNCTION_LIMIT = 75
TOP_EDGE_LIMIT = 150


def _func_label(func_key: tuple[str, int, str]) -> str:
    file_name, line_no, func_name = func_key
    return f"{func_name} ({file_name}:{line_no})"


def _build_top_functions(stats: pstats.Stats) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for func_key, values in stats.stats.items():
        primitive_calls, total_calls, total_time, cumulative_time, _ = values
        rows.append(
            {
                "function": _func_label(func_key),
                "primitive_calls": int(primitive_calls),
                "total_calls": int(total_calls),
                "total_time_seconds": float(total_time),
                "cumulative_time_seconds": float(cumulative_time),
            }
        )
    rows.sort(key=lambda row: row["cumulative_time_seconds"], reverse=True)
    return rows[:TOP_FUNCTION_LIMIT]


def _build_call_edges(stats: pstats.Stats) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    for callee_key, values in stats.stats.items():
        for caller_key, caller_metrics in values[4].items():
            edges.append(
                {
                    "caller": _func_label(caller_key),
                    "callee": _func_label(callee_key),
                    "call_count": int(caller_metrics[0]),
                    "total_time_seconds": float(caller_metrics[2]),
                    "cumulative_time_seconds": float(caller_metrics[3]),
                }
            )
    edges.sort(
        key=lambda edge: (
            edge["cumulative_time_seconds"],
            edge["total_time_seconds"],
            edge["call_count"],
        ),
        reverse=True,
    )
    return edges[:TOP_EDGE_LIMIT]


async def _run_websocket_session(
    app: Any,
    *,
    path: str,
    text: str,
) -> list[dict[str, Any]]:
    sent: list[dict[str, Any]] = []
    pending = [
        {"type": "websocket.connect"},
        {"type": "websocket.receive", "text": text},
    ]

    async def receive() -> dict[str, Any]:
        return pending.pop(0) if pending else {"type": "websocket.disconnect", "code": 1000}

    async def send(message: dict[str, Any]) -> None:
        sent.append(message)

    await app(
        {
            "type": "websocket",
            "scheme": "ws",
            "path": path,
            "query_string": b"",
            "headers": [],
            "subprotocols": [],
        },
        receive,
        send,
    )
    return sent


def _extract_text_payload(sent: list[dict[str, Any]]) -> str:
    for message in sent:
        if message.get("type") != "websocket.send":
            continue
        text = message.get("text")
        if isinstance(text, str):
            return text
        raw = message.get("bytes")
        if isinstance(raw, (bytes, bytearray)):
            return bytes(raw).decode("utf-8")
    raise AssertionError(f"no websocket.send payload found in {sent!r}")


async def _initialize_if_needed(app: Any) -> None:
    if hasattr(app, "engine"):
        try:
            await initialize_tigrbl_websocket_app(app)
        except ValueError as exc:
            if "Engine provider is not configured" not in str(exc):
                raise


async def _dispose_if_needed(app: Any) -> None:
    if hasattr(app, "engine"):
        try:
            await dispose_tigrbl_websocket_app(app)
        except ValueError as exc:
            if "Engine provider is not configured" not in str(exc):
                raise


async def _benchmark_ws_app(
    *,
    create_app: Callable[[Path], Any],
    scenario: str,
    endpoint: str,
    ops: int,
    db_backed: bool,
) -> dict[str, Any]:
    with TemporaryDirectory(dir=TMP_DIR, ignore_cleanup_errors=True) as tmp_dir:
        db_path = Path(tmp_dir) / f"{scenario}.sqlite3"
        app = create_app(db_path)
        await _initialize_if_needed(app)
        persisted_names: list[str] = []
        try:
            if db_backed:
                for idx in range(WARMUP_OPS):
                    name = f"warmup-ws-item-{idx}"
                    sent = await _run_websocket_session(
                        app,
                        path=endpoint,
                        text=json.dumps({"name": name}, separators=(",", ":")),
                    )
                    parsed = json.loads(_extract_text_payload(sent))
                    assert parsed["name"] == name
                start = perf_counter()
                for idx in range(ops):
                    name = f"bench-ws-item-{idx}"
                    sent = await _run_websocket_session(
                        app,
                        path=endpoint,
                        text=json.dumps({"name": name}, separators=(",", ":")),
                    )
                    parsed = json.loads(_extract_text_payload(sent))
                    assert parsed["name"] == name
                    persisted_names.append(name)
                elapsed = perf_counter() - start
                names = fetch_websocket_names(db_path)
                assert names[-ops:] == persisted_names
            else:
                for idx in range(WARMUP_OPS):
                    text = f"warmup-ws-echo-{idx}"
                    sent = await _run_websocket_session(app, path=endpoint, text=text)
                    assert _extract_text_payload(sent) == text
                start = perf_counter()
                for idx in range(ops):
                    text = f"bench-ws-echo-{idx}"
                    sent = await _run_websocket_session(app, path=endpoint, text=text)
                    assert _extract_text_payload(sent) == text
                elapsed = perf_counter() - start
        finally:
            await _dispose_if_needed(app)
        return {
            "scenario": scenario,
            "endpoint": endpoint,
            "ops": ops,
            "warmup_ops": WARMUP_OPS,
            "ops_per_second": ops / elapsed,
            "total_execution_time_seconds": elapsed,
            "persisted_row_count": len(persisted_names),
            "shared_runner": "direct ASGI websocket session",
        }


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
        "exact_route_count": int(measurement.exact_route_count),
        "hot_op_count": int(measurement.hot_op_count),
        "compact_step_count": int(measurement.compact_step_count),
        "compact_segment_count": int(measurement.compact_segment_count),
        "compact_program_segment_ref_count": int(measurement.compact_program_segment_ref_count),
        "compact_route_entry_count": int(measurement.compact_route_entry_count),
        "shared_error_profile_count": int(measurement.shared_error_profile_count),
        "externalized_prelude_step_count": int(measurement.externalized_prelude_step_count),
        "max_index_width_bits": int(measurement.max_index_width_bits),
    }


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


def _serialize_measurement_from_measurement(measurement: Any) -> dict[str, Any]:
    return {
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
        "compact_program_segment_ref_count": int(measurement.compact_program_segment_ref_count),
        "compact_route_entry_count": int(measurement.compact_route_entry_count),
        "shared_error_profile_count": int(measurement.shared_error_profile_count),
        "externalized_prelude_step_count": int(measurement.externalized_prelude_step_count),
        "max_index_width_bits": int(measurement.max_index_width_bits),
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
        "measurement": _serialize_measurement_from_measurement(measurement),
    }


async def _export_hot_block() -> list[str]:
    with TemporaryDirectory(dir=TMP_DIR, ignore_cleanup_errors=True) as tmp_dir:
        db_path = Path(tmp_dir) / "websocket-hot-block.sqlite3"
        app = create_tigrbl_websocket_db_app(db_path)
        await _initialize_if_needed(app)
        try:
            plan = build_kernel_plan(app)
            packed = getattr(plan, "packed", None)
            if packed is None:
                raise RuntimeError("websocket benchmark app did not build a packed kernel")
            hot_block_bytes = getattr(packed, "hot_block_bytes", b"")
            if not hot_block_bytes:
                raise RuntimeError("websocket benchmark app did not carry TGPKHOT1 bytes")
            hot_block_view = load_packed_kernel_hot_block(hot_block_bytes)
            summary = _summarize_hot_block(hot_block_bytes)
            summary_payload = {
                "artifact": {
                    "path": str(HOT_BLOCK_PREFIX.with_suffix(".bin")),
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
            outputs = {
                HOT_BLOCK_PREFIX.with_suffix(".bin"): hot_block_bytes,
                HOT_BLOCK_PREFIX.with_suffix(".summary.json"): json.dumps(summary_payload, indent=2).encode("utf-8"),
                HOT_BLOCK_PREFIX.with_suffix(".hexdump.txt"): _hexdump(hot_block_bytes).encode("utf-8"),
                HOT_BLOCK_PREFIX.with_suffix(".benchmark.json"): json.dumps(benchmark_payload, indent=2).encode("utf-8"),
                HOT_BLOCK_PREFIX.with_suffix(".benchmark.md"): _render_hot_block_benchmark_md("websocket", benchmark_payload).encode("utf-8"),
            }
            for path, payload in outputs.items():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)
            return [str(path) for path in outputs]
        finally:
            await _dispose_if_needed(app)


async def _profile_websocket_call_graph(
    *,
    create_app: Callable[[Path], Any],
    endpoint: str,
    db_backed: bool,
    results_path: Path,
) -> dict[str, Any]:
    with TemporaryDirectory(dir=TMP_DIR, ignore_cleanup_errors=True) as tmp_dir:
        db_path = Path(tmp_dir) / f"{results_path.stem}.sqlite3"
        app = create_app(db_path)
        await _initialize_if_needed(app)
        profiler = cProfile.Profile()
        start = perf_counter()
        try:
            profiler.enable()
            if db_backed:
                for idx in range(250):
                    name = f"profiled-ws-item-{idx}"
                    sent = await _run_websocket_session(
                        app,
                        path=endpoint,
                        text=json.dumps({"name": name}, separators=(",", ":")),
                    )
                    parsed = json.loads(_extract_text_payload(sent))
                    assert parsed["name"] == name
            else:
                for idx in range(250):
                    text = f"profiled-ws-echo-{idx}"
                    sent = await _run_websocket_session(app, path=endpoint, text=text)
                    assert _extract_text_payload(sent) == text
            profiler.disable()
        finally:
            await _dispose_if_needed(app)
        elapsed = perf_counter() - start
        stats = pstats.Stats(profiler).strip_dirs()
        payload = {
            "ops": 250,
            "endpoint": endpoint,
            "elapsed_seconds": elapsed,
            "call_graph": {
                "top_functions": _build_top_functions(stats),
                "edges": _build_call_edges(stats),
            },
            "artifact_path": str(results_path),
            "scenario": "db_backed" if db_backed else "transport_only",
            "shared_runner": "direct ASGI websocket session",
        }
        payload["call_graph"]["node_count"] = len(
            {edge["caller"] for edge in payload["call_graph"]["edges"]}
            | {edge["callee"] for edge in payload["call_graph"]["edges"]}
        )
        payload["call_graph"]["edge_count"] = len(payload["call_graph"]["edges"])
        results_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload


async def main() -> None:
    PERF_DIR.mkdir(parents=True, exist_ok=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)

    results: dict[str, Any] = {"transport_only": {}, "db_backed": {}}
    for ops in OPS_COUNTS:
        results["transport_only"][str(ops)] = {
            "tigrbl": await _benchmark_ws_app(
                create_app=create_tigrbl_websocket_transport_app,
                scenario=f"tigrbl-ws-transport-{ops}",
                endpoint="/ws/echo",
                ops=ops,
                db_backed=False,
            ),
            "fastapi": await _benchmark_ws_app(
                create_app=create_fastapi_websocket_transport_app,
                scenario=f"fastapi-ws-transport-{ops}",
                endpoint="/ws/echo",
                ops=ops,
                db_backed=False,
            ),
        }
        results["db_backed"][str(ops)] = {
            "tigrbl": await _benchmark_ws_app(
                create_app=create_tigrbl_websocket_db_app,
                scenario=f"tigrbl-ws-db-{ops}",
                endpoint="/ws/items",
                ops=ops,
                db_backed=True,
            ),
            "fastapi": await _benchmark_ws_app(
                create_app=create_fastapi_websocket_db_app,
                scenario=f"fastapi-ws-db-{ops}",
                endpoint="/ws/items",
                ops=ops,
                db_backed=True,
            ),
        }

    with TemporaryDirectory(dir=TMP_DIR, ignore_cleanup_errors=True) as tmp_dir:
        db_path = Path(tmp_dir) / "websocket-kernel.sqlite3"
        app = create_tigrbl_websocket_db_app(db_path)
        await _initialize_if_needed(app)
        try:
            measurement = _serialize_measurement(app)
        finally:
            await _dispose_if_needed(app)
    kernel_payload = {
        "fairness": {
            "surface": "websocket",
            "shared_server_runner": "direct ASGI websocket session",
            "shared_database_family": "SQLite",
            "transport_only_endpoint": "/ws/echo",
            "db_backed_endpoint": "/ws/items",
        },
        "candidate": {
            "tigrbl": {"kernel_plan_measurement": measurement},
            "benchmarks": results,
        },
    }
    KERNEL_JSON_PATH.write_text(json.dumps(kernel_payload, indent=2), encoding="utf-8")
    KERNEL_MD_PATH.write_text(
        "# WebSocket Kernel Packing KC and FastAPI Parity Report\n\n"
        f"- shared runner: direct ASGI websocket session\n"
        f"- raw bytes: {measurement['raw_bytes']}\n"
        f"- compressed bytes: {measurement['compressed_bytes']}\n"
        f"- transport-only 250 ops/s: tigrbl={results['transport_only']['250']['tigrbl']['ops_per_second']:.2f}, fastapi={results['transport_only']['250']['fastapi']['ops_per_second']:.2f}\n"
        f"- db-backed 250 ops/s: tigrbl={results['db_backed']['250']['tigrbl']['ops_per_second']:.2f}, fastapi={results['db_backed']['250']['fastapi']['ops_per_second']:.2f}\n",
        encoding="utf-8",
    )
    RESULTS_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    await _profile_websocket_call_graph(
        create_app=create_tigrbl_websocket_db_app,
        endpoint="/ws/items",
        db_backed=True,
        results_path=TIGRBL_CALL_GRAPH_PATH,
    )
    await _profile_websocket_call_graph(
        create_app=create_fastapi_websocket_db_app,
        endpoint="/ws/items",
        db_backed=True,
        results_path=FASTAPI_CALL_GRAPH_PATH,
    )
    await _export_hot_block()


if __name__ == "__main__":
    asyncio.run(main())
