from __future__ import annotations

import argparse
import asyncio
import json
import platform
import re
import shutil
import subprocess
import sys
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from tests.i9n.uvicorn_utils import run_uvicorn_in_task, stop_uvicorn_server
from tests.perf.helper_tigrbl_create_app import (
    create_tigrbl_app,
    dispose_tigrbl_app,
    initialize_tigrbl_app,
    tigrbl_create_path,
    tigrbl_create_rpc_method,
)

ROOT = Path(__file__).resolve().parents[4]
TMP_OUTPUT_ROOT = ROOT / ".tmp" / "load-patterns"
PERF_DIR = ROOT / "pkgs" / "core" / "tigrbl_tests" / "tests" / "perf"
SUPPORTED_DRIVERS = {"vegeta", "wrk2"}
SUPPORTED_TARGETS = {"rest-create", "jsonrpc-create"}


@dataclass(frozen=True)
class Segment:
    name: str
    rate_per_second: int
    duration_seconds: int
    connections: int | None = None
    workers: int | None = None


@dataclass(frozen=True)
class Pattern:
    name: str
    driver: str
    target: str
    segments: tuple[Segment, ...]
    metadata: Mapping[str, Any]


@dataclass(frozen=True)
class CommandResult:
    stdout: bytes
    stderr: bytes
    returncode: int
    command: tuple[str, ...]


CommandRunner = Callable[[Sequence[str], bytes | None], CommandResult]


BUILTIN_PATTERNS: dict[str, dict[str, Any]] = {
    "steady-rest": {
        "name": "steady-rest",
        "driver": "vegeta",
        "target": "rest-create",
        "segments": [
            {"name": "warmup", "rate_per_second": 100, "duration_seconds": 10},
            {"name": "steady", "rate_per_second": 500, "duration_seconds": 60},
        ],
        "metadata": {
            "server": "uvicorn",
            "transport": "http.rest",
            "engine_mode": "sqlite",
            "operation_count": 1,
            "warmup_policy": "explicit warmup segment",
        },
    },
    "steady-jsonrpc": {
        "name": "steady-jsonrpc",
        "driver": "vegeta",
        "target": "jsonrpc-create",
        "segments": [
            {"name": "warmup", "rate_per_second": 100, "duration_seconds": 10},
            {"name": "steady", "rate_per_second": 500, "duration_seconds": 60},
        ],
        "metadata": {
            "server": "uvicorn",
            "transport": "http.jsonrpc",
            "engine_mode": "sqlite",
            "operation_count": 1,
            "warmup_policy": "explicit warmup segment",
        },
    },
    "spike-jsonrpc": {
        "name": "spike-jsonrpc",
        "driver": "wrk2",
        "target": "jsonrpc-create",
        "segments": [
            {
                "name": "baseline",
                "rate_per_second": 250,
                "duration_seconds": 30,
                "connections": 64,
                "workers": 4,
            },
            {
                "name": "spike",
                "rate_per_second": 1000,
                "duration_seconds": 30,
                "connections": 128,
                "workers": 4,
            },
            {
                "name": "recover",
                "rate_per_second": 250,
                "duration_seconds": 30,
                "connections": 64,
                "workers": 4,
            },
        ],
        "metadata": {
            "server": "uvicorn",
            "transport": "http.jsonrpc",
            "engine_mode": "sqlite",
            "operation_count": 1,
            "warmup_policy": "baseline segment precedes spike",
        },
    },
}


class PatternValidationError(ValueError):
    pass


class DriverExecutionError(RuntimeError):
    pass


def parse_pattern(data: Mapping[str, Any]) -> Pattern:
    name = _required_str(data, "name")
    driver = _required_str(data, "driver")
    target = _required_str(data, "target")
    if driver not in SUPPORTED_DRIVERS:
        raise PatternValidationError(f"unsupported driver {driver!r}")
    if target not in SUPPORTED_TARGETS:
        raise PatternValidationError(f"unsupported target {target!r}")

    raw_segments = data.get("segments")
    if not isinstance(raw_segments, list) or not raw_segments:
        raise PatternValidationError("pattern must define at least one segment")
    segments = tuple(_parse_segment(item) for item in raw_segments)

    metadata = data.get("metadata", {})
    if not isinstance(metadata, Mapping):
        raise PatternValidationError("metadata must be an object")
    return Pattern(
        name=name,
        driver=driver,
        target=target,
        segments=segments,
        metadata=dict(metadata),
    )


def load_pattern(name: str, *, driver_override: str | None = None) -> Pattern:
    try:
        raw = dict(BUILTIN_PATTERNS[name])
    except KeyError as exc:
        choices = ", ".join(sorted(BUILTIN_PATTERNS))
        raise PatternValidationError(f"unknown pattern {name!r}; choose one of: {choices}") from exc
    if driver_override is not None:
        raw["driver"] = driver_override
    return parse_pattern(raw)


def render_target(base_url: str, target: str, body_path: Path) -> str:
    if target == "rest-create":
        return (
            f"POST {base_url.rstrip('/')}{tigrbl_create_path()}\n"
            "Content-Type: application/json\n"
            f"@{body_path}\n"
        )
    if target == "jsonrpc-create":
        return (
            f"POST {base_url.rstrip('/')}/rpc\n"
            "Content-Type: application/json\n"
            f"@{body_path}\n"
        )
    raise PatternValidationError(f"unsupported target {target!r}")


def render_body(target: str, segment: Segment) -> str:
    request_id = f"{segment.name}-1"
    if target == "rest-create":
        return json.dumps({"name": f"open-loop-{segment.name}"}, separators=(",", ":"))
    if target == "jsonrpc-create":
        return json.dumps(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": tigrbl_create_rpc_method(),
                "params": {"name": f"open-loop-{segment.name}"},
            },
            separators=(",", ":"),
        )
    raise PatternValidationError(f"unsupported target {target!r}")


def normalize_vegeta_report(
    report: Mapping[str, Any],
    *,
    segment: Segment,
    command: Sequence[str],
) -> dict[str, Any]:
    requests = int(report.get("requests", 0) or 0)
    duration_seconds = _nanoseconds_to_seconds(report.get("duration")) or float(
        segment.duration_seconds
    )
    status_codes = {
        str(key): int(value)
        for key, value in dict(report.get("status_codes", {}) or {}).items()
    }
    success_count = sum(
        count for code, count in status_codes.items() if 200 <= int(code) <= 399
    )
    timeout_count = _count_timeout_errors(report.get("errors", []))
    error_count = max(0, requests - success_count)
    latencies = dict(report.get("latencies", {}) or {})
    return {
        "driver": "vegeta",
        "segment": asdict(segment),
        "command": list(command),
        "offered_rate_per_second": segment.rate_per_second,
        "achieved_throughput_per_second": _as_float(report.get("throughput"))
        or _safe_rate(success_count, duration_seconds),
        "success_count": success_count,
        "error_count": error_count,
        "timeout_count": timeout_count,
        "duration_seconds": duration_seconds,
        "latency_ms": {
            "p50": _nanoseconds_to_milliseconds(latencies.get("50th")),
            "p90": _nanoseconds_to_milliseconds(latencies.get("90th")),
            "p95": _nanoseconds_to_milliseconds(latencies.get("95th")),
            "p99": _nanoseconds_to_milliseconds(latencies.get("99th")),
            "p99_9": _nanoseconds_to_milliseconds(
                latencies.get("99.9th", latencies.get("999th"))
            ),
        },
        "status_codes": status_codes,
        "raw": dict(report),
    }


def parse_wrk2_output(
    text: str,
    *,
    segment: Segment,
    command: Sequence[str],
) -> dict[str, Any]:
    requests = _parse_int_match(r"(\d+)\s+requests in", text) or 0
    non_success = _parse_int_match(r"Non-2xx or 3xx responses:\s*(\d+)", text) or 0
    socket_timeout = _parse_int_match(r"timeout\s+(\d+)", text) or 0
    throughput = _parse_float_match(r"Requests/sec:\s*([0-9.]+)", text) or 0.0
    latency = _parse_wrk2_latency_distribution(text)
    return {
        "driver": "wrk2",
        "segment": asdict(segment),
        "command": list(command),
        "offered_rate_per_second": segment.rate_per_second,
        "achieved_throughput_per_second": throughput,
        "success_count": max(0, requests - non_success),
        "error_count": non_success + socket_timeout,
        "timeout_count": socket_timeout,
        "duration_seconds": float(segment.duration_seconds),
        "latency_ms": latency,
        "raw": text,
    }


def run_pattern_segments(
    pattern: Pattern,
    *,
    base_url: str,
    output_dir: Path,
    driver_executable: str | None = None,
    runner: CommandRunner | None = None,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    driver = driver_executable or resolve_driver_executable(pattern.driver)
    run_command = runner or _run_command
    segment_summaries: list[dict[str, Any]] = []

    for segment in pattern.segments:
        segment_dir = output_dir / segment.name
        segment_dir.mkdir(parents=True, exist_ok=True)
        body_path = segment_dir / f"{pattern.target}.json"
        target_path = segment_dir / f"{pattern.target}.target"
        body = render_body(pattern.target, segment)
        body_path.write_text(body, encoding="utf-8")
        target_path.write_text(render_target(base_url, pattern.target, body_path), encoding="utf-8")
        if pattern.driver == "vegeta":
            summary = _run_vegeta_segment(
                driver,
                pattern.target,
                segment,
                target_path,
                segment_dir,
                run_command,
            )
        else:
            summary = _run_wrk2_segment(
                driver,
                base_url,
                pattern.target,
                segment,
                body,
                segment_dir,
                run_command,
            )
        summary_path = segment_dir / "summary.json"
        summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        segment_summaries.append({**summary, "summary_path": str(summary_path)})

    manifest = {
        "suite": "open_loop_load_patterns",
        "pattern": pattern.name,
        "driver": pattern.driver,
        "target": pattern.target,
        "metadata": dict(pattern.metadata),
        "environment": _environment(base_url),
        "segments": segment_summaries,
    }
    manifest_path = output_dir / f"{pattern.name}.json"
    report_path = output_dir / f"{pattern.name}.md"
    manifest["manifest_path"] = str(manifest_path)
    manifest["report_path"] = str(report_path)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    report_path.write_text(render_markdown_report(manifest), encoding="utf-8")
    return manifest


async def run_live_pattern(
    pattern: Pattern,
    *,
    output_root: Path = TMP_OUTPUT_ROOT,
    publish_artifacts: bool = False,
    driver_executable: str | None = None,
) -> dict[str, Any]:
    run_id = f"{pattern.name}-{uuid.uuid4().hex[:12]}"
    output_dir = output_root / run_id
    db_path = output_dir / "open-loop.sqlite3"
    output_dir.mkdir(parents=True, exist_ok=True)
    app = create_tigrbl_app(db_path)
    server = None
    task = None
    try:
        await initialize_tigrbl_app(app)
        base_url, server, task = await run_uvicorn_in_task(app)
        manifest = run_pattern_segments(
            pattern,
            base_url=base_url,
            output_dir=output_dir,
            driver_executable=driver_executable,
        )
    finally:
        if server is not None and task is not None:
            await stop_uvicorn_server(server, task)
        await dispose_tigrbl_app(app)
    if publish_artifacts:
        manifest["published_artifacts"] = publish_artifacts_for_manifest(manifest)
    return manifest


def publish_artifacts_for_manifest(manifest: Mapping[str, Any]) -> dict[str, str]:
    PERF_DIR.mkdir(parents=True, exist_ok=True)
    pattern = str(manifest["pattern"])
    source_manifest = Path(str(manifest["manifest_path"]))
    source_report = Path(str(manifest["report_path"]))
    published_manifest = PERF_DIR / f"open_loop_load_patterns_{pattern}.json"
    published_report = PERF_DIR / f"open_loop_load_patterns_{pattern}.md"
    shutil.copyfile(source_manifest, published_manifest)
    shutil.copyfile(source_report, published_report)
    return {
        "manifest": str(published_manifest),
        "report": str(published_report),
    }


def render_markdown_report(manifest: Mapping[str, Any]) -> str:
    lines = [
        "# Open-Loop Load Pattern Report",
        "",
        f"- Pattern: `{manifest['pattern']}`",
        f"- Driver: `{manifest['driver']}`",
        f"- Target: `{manifest['target']}`",
        f"- Server URL: `{manifest['environment']['server_url']}`",
        "",
        "| Segment | Offered rps | Achieved rps | Success | Errors | Timeouts | p50 ms | p95 ms | p99 ms |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for segment in manifest.get("segments", []):
        latency = segment.get("latency_ms", {})
        lines.append(
            "| {name} | {offered} | {achieved:.2f} | {success} | {errors} | {timeouts} | {p50} | {p95} | {p99} |".format(
                name=segment["segment"]["name"],
                offered=segment["offered_rate_per_second"],
                achieved=float(segment["achieved_throughput_per_second"] or 0.0),
                success=segment["success_count"],
                errors=segment["error_count"],
                timeouts=segment["timeout_count"],
                p50=_format_optional_float(latency.get("p50")),
                p95=_format_optional_float(latency.get("p95")),
                p99=_format_optional_float(latency.get("p99")),
            )
        )
    return "\n".join(lines) + "\n"


def resolve_driver_executable(driver: str) -> str:
    executable = shutil.which(driver)
    if executable is None:
        if driver == "vegeta":
            raise DriverExecutionError(
                "vegeta executable not found; install vegeta or choose --driver wrk2"
            )
        if driver == "wrk2":
            raise DriverExecutionError(
                "wrk2 executable not found; install wrk2 or choose --driver vegeta"
            )
        raise DriverExecutionError(f"{driver} executable not found")
    return executable


def list_patterns() -> str:
    rows = []
    for name in sorted(BUILTIN_PATTERNS):
        pattern = parse_pattern(BUILTIN_PATTERNS[name])
        rows.append(f"{name}\tdriver={pattern.driver}\ttarget={pattern.target}")
    return "\n".join(rows)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run open-loop REST and JSON-RPC load patterns against the Tigrbl "
            "benchmark app using vegeta or wrk2."
        )
    )
    parser.add_argument("--list-patterns", action="store_true")
    parser.add_argument("--pattern", default="steady-rest")
    parser.add_argument("--driver", choices=sorted(SUPPORTED_DRIVERS))
    parser.add_argument("--driver-path")
    parser.add_argument("--output-dir", default=str(TMP_OUTPUT_ROOT))
    parser.add_argument("--publish-artifacts", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    if args.list_patterns:
        print(list_patterns())
        return
    pattern = load_pattern(args.pattern, driver_override=args.driver)
    manifest = asyncio.run(
        run_live_pattern(
            pattern,
            output_root=Path(args.output_dir),
            publish_artifacts=bool(args.publish_artifacts),
            driver_executable=args.driver_path,
        )
    )
    print(json.dumps({"manifest": manifest["manifest_path"], "report": manifest["report_path"]}))


def _parse_segment(data: Any) -> Segment:
    if not isinstance(data, Mapping):
        raise PatternValidationError("segment must be an object")
    name = _required_str(data, "name")
    rate = _required_positive_int(data, "rate_per_second")
    duration = _required_positive_int(data, "duration_seconds")
    connections = _optional_positive_int(data, "connections")
    workers = _optional_positive_int(data, "workers")
    return Segment(
        name=name,
        rate_per_second=rate,
        duration_seconds=duration,
        connections=connections,
        workers=workers,
    )


def _required_str(data: Mapping[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise PatternValidationError(f"{key} must be a non-empty string")
    return value


def _required_positive_int(data: Mapping[str, Any], key: str) -> int:
    value = data.get(key)
    if not isinstance(value, int) or value <= 0:
        raise PatternValidationError(f"{key} must be a positive integer")
    return value


def _optional_positive_int(data: Mapping[str, Any], key: str) -> int | None:
    value = data.get(key)
    if value is None:
        return None
    if not isinstance(value, int) or value <= 0:
        raise PatternValidationError(f"{key} must be a positive integer")
    return value


def _run_vegeta_segment(
    driver: str,
    target: str,
    segment: Segment,
    target_path: Path,
    segment_dir: Path,
    runner: CommandRunner,
) -> dict[str, Any]:
    raw_path = segment_dir / f"{target}.vegeta.bin"
    command = (
        driver,
        "attack",
        f"-rate={segment.rate_per_second}/s",
        f"-duration={segment.duration_seconds}s",
        f"-targets={target_path}",
    )
    attack = runner(command, None)
    if attack.returncode != 0:
        raise DriverExecutionError(_driver_error("vegeta attack", attack))
    raw_path.write_bytes(attack.stdout)

    report_command = (driver, "report", "-type=json", str(raw_path))
    report = runner(report_command, None)
    if report.returncode != 0:
        raise DriverExecutionError(_driver_error("vegeta report", report))
    report_payload = json.loads(report.stdout.decode("utf-8"))
    return {
        **normalize_vegeta_report(report_payload, segment=segment, command=command),
        "raw_path": str(raw_path),
    }


def _run_wrk2_segment(
    driver: str,
    base_url: str,
    target: str,
    segment: Segment,
    body: str,
    segment_dir: Path,
    runner: CommandRunner,
) -> dict[str, Any]:
    script_path = segment_dir / f"{target}.lua"
    raw_path = segment_dir / f"{target}.wrk2.txt"
    script_path.write_text(_render_wrk_lua(body), encoding="utf-8")
    command = (
        driver,
        f"-t{segment.workers or 4}",
        f"-c{segment.connections or 64}",
        f"-d{segment.duration_seconds}s",
        f"-R{segment.rate_per_second}",
        "--latency",
        "-s",
        str(script_path),
        _target_url(base_url, target),
    )
    result = runner(command, None)
    raw_text = result.stdout.decode("utf-8", errors="replace")
    raw_path.write_text(raw_text, encoding="utf-8")
    if result.returncode != 0:
        raise DriverExecutionError(_driver_error("wrk2", result))
    return {
        **parse_wrk2_output(raw_text, segment=segment, command=command),
        "raw_path": str(raw_path),
    }


def _render_wrk_lua(body: str) -> str:
    escaped = body.replace("\\", "\\\\").replace('"', '\\"')
    return (
        'wrk.method = "POST"\n'
        'wrk.headers["Content-Type"] = "application/json"\n'
        f'wrk.body = "{escaped}"\n'
    )


def _target_url(base_url: str, target: str) -> str:
    if target == "rest-create":
        return f"{base_url.rstrip('/')}{tigrbl_create_path()}"
    if target == "jsonrpc-create":
        return f"{base_url.rstrip('/')}/rpc"
    raise PatternValidationError(f"unsupported target {target!r}")


def _run_command(command: Sequence[str], stdin: bytes | None) -> CommandResult:
    result = subprocess.run(
        list(command),
        input=stdin,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return CommandResult(
        stdout=result.stdout,
        stderr=result.stderr,
        returncode=result.returncode,
        command=tuple(command),
    )


def _driver_error(label: str, result: CommandResult) -> str:
    stderr = result.stderr.decode("utf-8", errors="replace").strip()
    stdout = result.stdout.decode("utf-8", errors="replace").strip()
    detail = stderr or stdout or f"exit code {result.returncode}"
    return f"{label} failed: {detail}"


def _environment(base_url: str) -> dict[str, Any]:
    return {
        "git_sha": _git_sha(),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "server_url": base_url,
        "cwd": str(ROOT),
        "timestamp_seconds": time.time(),
    }


def _git_sha() -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.decode("utf-8").strip()


def _nanoseconds_to_seconds(value: Any) -> float | None:
    numeric = _as_float(value)
    if numeric is None:
        return None
    return numeric / 1_000_000_000.0


def _nanoseconds_to_milliseconds(value: Any) -> float | None:
    numeric = _as_float(value)
    if numeric is None:
        return None
    return numeric / 1_000_000.0


def _as_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_rate(count: int, seconds: float) -> float:
    if seconds <= 0:
        return 0.0
    return float(count) / seconds


def _count_timeout_errors(errors: Any) -> int:
    if not isinstance(errors, list):
        return 0
    return sum(1 for error in errors if "timeout" in str(error).lower())


def _parse_wrk2_latency_distribution(text: str) -> dict[str, float | None]:
    percentile_map = {
        "50.000": "p50",
        "90.000": "p90",
        "95.000": "p95",
        "99.000": "p99",
        "99.900": "p99_9",
    }
    values: dict[str, float | None] = {
        "p50": None,
        "p90": None,
        "p95": None,
        "p99": None,
        "p99_9": None,
    }
    for match in re.finditer(r"^\s*([0-9.]+)%\s+([0-9.]+)(us|ms|s)\s*$", text, re.MULTILINE):
        key = percentile_map.get(match.group(1))
        if key is None:
            continue
        values[key] = _duration_to_milliseconds(float(match.group(2)), match.group(3))
    return values


def _duration_to_milliseconds(value: float, unit: str) -> float:
    if unit == "us":
        return value / 1000.0
    if unit == "ms":
        return value
    if unit == "s":
        return value * 1000.0
    raise ValueError(f"unsupported duration unit {unit!r}")


def _parse_int_match(pattern: str, text: str) -> int | None:
    match = re.search(pattern, text)
    if match is None:
        return None
    return int(match.group(1))


def _parse_float_match(pattern: str, text: str) -> float | None:
    match = re.search(pattern, text)
    if match is None:
        return None
    return float(match.group(1))


def _format_optional_float(value: Any) -> str:
    numeric = _as_float(value)
    if numeric is None:
        return "n/a"
    return f"{numeric:.2f}"


if __name__ == "__main__":
    main()
