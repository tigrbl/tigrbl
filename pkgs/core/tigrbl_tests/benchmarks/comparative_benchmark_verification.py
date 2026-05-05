from __future__ import annotations

import argparse
import asyncio
import gzip
import importlib
import inspect
import json
import math
import os
import platform
import random
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median, pstdev
from typing import Any, Callable

import httpx

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

ROOT = Path(__file__).resolve().parents[4]
PERF_DIR = ROOT / "pkgs" / "core" / "tigrbl_tests" / "tests" / "perf"
TMP_ROOT = ROOT / ".tmp" / "comparative-benchmark"
DEFAULT_JSON_OUTPUT = PERF_DIR / "comparative_benchmark_verification.json"
DEFAULT_MD_OUTPUT = PERF_DIR / "comparative_benchmark_verification.md"

SCENARIOS = ("tigrbl", "fastapi")
REFERENCE_BENCHMARK_VALUES = {
    "requests_per_second": {"tigrbl": "77,958", "fastapi": "15,974"},
    "p95_latency_ms": {"tigrbl": "2.58", "fastapi": "18.33"},
    "cpu_usage_percent": {"tigrbl": "11.03%", "fastapi": "23.52%"},
    "memory_usage_mb": {"tigrbl": "13.93 MB", "fastapi": "62.88 MB"},
    "lines_of_code": {"tigrbl": "~6,500", "fastapi": "~28,000"},
    "startup_time_seconds": {"tigrbl": "0.013", "fastapi": "0.233"},
    "deployment_artifact_size_mb": {"tigrbl": "~6.5 MB", "fastapi": "~76 MB"},
    "compliance_security": {"tigrbl": "Strong", "fastapi": "Moderate"},
}


@dataclass(frozen=True)
class ScenarioConfig:
    name: str
    create_app: Callable[[Path], Any]
    initialize: Callable[[Any], Any] | None
    dispose: Callable[[Any], Any]
    fetch_names: Callable[[Path], list[str]]
    endpoint_path: str
    loc_packages: tuple[str, ...]


def scenario_configs() -> dict[str, ScenarioConfig]:
    return {
        "tigrbl": ScenarioConfig(
            name="tigrbl",
            create_app=create_tigrbl_app,
            initialize=initialize_tigrbl_app,
            dispose=dispose_tigrbl_app,
            fetch_names=fetch_tigrbl_names,
            endpoint_path=tigrbl_create_path(),
            loc_packages=(
                "tigrbl",
                "tigrbl_base",
                "tigrbl_core",
                "tigrbl_concrete",
                "tigrbl_runtime",
            ),
        ),
        "fastapi": ScenarioConfig(
            name="fastapi",
            create_app=create_fastapi_app,
            initialize=None,
            dispose=dispose_fastapi_app,
            fetch_names=fetch_fastapi_names,
            endpoint_path=fastapi_create_path(),
            loc_packages=("fastapi",),
        ),
    }


def quantile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("cannot compute quantile for an empty sample")
    if len(ordered) == 1:
        return ordered[0]
    pos = (len(ordered) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(ordered) - 1)
    frac = pos - lo
    return ordered[lo] * (1.0 - frac) + ordered[hi] * frac


def summarize(values: list[float]) -> dict[str, float | int]:
    if not values:
        raise ValueError("cannot summarize an empty sample")
    avg = mean(values)
    stddev = pstdev(values)
    stderr = stddev / math.sqrt(len(values)) if values else 0.0
    return {
        "sample_count": len(values),
        "min": min(values),
        "max": max(values),
        "mean": avg,
        "median": median(values),
        "stddev": stddev,
        "confidence_interval_95_low": avg - (1.96 * stderr),
        "confidence_interval_95_high": avg + (1.96 * stderr),
    }


def summarize_latency(seconds: list[float]) -> dict[str, float | int]:
    milliseconds = [value * 1000.0 for value in seconds]
    summary = summarize(milliseconds)
    summary.update(
        {
            "p50": quantile(milliseconds, 0.50),
            "p90": quantile(milliseconds, 0.90),
            "p95": quantile(milliseconds, 0.95),
            "p99": quantile(milliseconds, 0.99),
        }
    )
    return summary


class ProcSampler:
    def __init__(self, pid: int, *, interval_seconds: float = 0.05) -> None:
        self.pid = pid
        self.interval_seconds = interval_seconds
        self.samples: list[dict[str, float]] = []
        self._stop = asyncio.Event()
        self._clock_ticks = os.sysconf("SC_CLK_TCK") if hasattr(os, "sysconf") else 100
        self._page_size = os.sysconf("SC_PAGE_SIZE") if hasattr(os, "sysconf") else 4096

    async def run(self) -> None:
        previous = self._read_proc()
        while not self._stop.is_set():
            await asyncio.sleep(self.interval_seconds)
            current = self._read_proc()
            if previous is None or current is None:
                previous = current
                continue
            elapsed = current["time"] - previous["time"]
            cpu_delta = current["cpu_seconds"] - previous["cpu_seconds"]
            cpu_percent = (cpu_delta / elapsed) * 100.0 if elapsed > 0 else 0.0
            self.samples.append(
                {
                    "cpu_percent": cpu_percent,
                    "rss_mb": current["rss_mb"],
                    "timestamp": current["time"],
                }
            )
            previous = current

    def stop(self) -> None:
        self._stop.set()

    def _read_proc(self) -> dict[str, float] | None:
        stat_path = Path("/proc") / str(self.pid) / "stat"
        if not stat_path.exists():
            return {
                "time": time.perf_counter(),
                "cpu_seconds": time.process_time(),
                "rss_mb": 0.0,
            }
        try:
            parts = stat_path.read_text(encoding="utf-8").split()
            utime = float(parts[13]) / float(self._clock_ticks)
            stime = float(parts[14]) / float(self._clock_ticks)
            rss_pages = float(parts[23])
        except (OSError, IndexError, ValueError):
            return None
        return {
            "time": time.perf_counter(),
            "cpu_seconds": utime + stime,
            "rss_mb": (rss_pages * float(self._page_size)) / (1024.0 * 1024.0),
        }


def resource_summary(samples: list[dict[str, float]]) -> dict[str, Any]:
    if not samples:
        raise ValueError("resource telemetry is missing")
    cpu = [sample["cpu_percent"] for sample in samples]
    rss = [sample["rss_mb"] for sample in samples]
    return {
        "cpu_percent": {
            "average": mean(cpu),
            "peak": max(cpu),
            "sample_count": len(cpu),
        },
        "memory_mb": {
            "baseline": rss[0],
            "average": mean(rss),
            "peak": max(rss),
            "delta": max(rss) - rss[0],
            "sample_count": len(rss),
        },
    }


async def _maybe_await(value: Any) -> Any:
    if inspect.isawaitable(value):
        return await value
    return value


async def benchmark_once(
    config: ScenarioConfig,
    *,
    round_index: int,
    ops: int,
    warmup_ops: int,
) -> dict[str, Any]:
    tmpdir = Path(tempfile.mkdtemp(dir=TMP_ROOT))
    db_path = tmpdir / f"{config.name}.sqlite3"
    expected_names = [f"{config.name}-{round_index}-{idx}" for idx in range(ops)]
    warmup_names = [f"warmup-{config.name}-{round_index}-{idx}" for idx in range(warmup_ops)]

    app = config.create_app(db_path)
    start = time.perf_counter()
    if config.initialize is not None:
        await _maybe_await(config.initialize(app))
    base_url, server, task = await run_uvicorn_in_task(app)
    startup_seconds = time.perf_counter() - start

    sampler = ProcSampler(os.getpid())
    sampler_task = asyncio.create_task(sampler.run(), name=f"{config.name}-proc-sampler")
    latencies: list[float] = []
    try:
        async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
            for idx, item_name in enumerate(warmup_names):
                response = await client.post(config.endpoint_path, json={"name": item_name})
                assert response.status_code in {200, 201}, response.text
                assert response.json()["name"] == item_name

            start_exec = time.perf_counter()
            for item_name in expected_names:
                op_start = time.perf_counter()
                response = await client.post(config.endpoint_path, json={"name": item_name})
                latencies.append(time.perf_counter() - op_start)
                assert response.status_code in {200, 201}, response.text
                assert response.json()["name"] == item_name
            execution_seconds = time.perf_counter() - start_exec

        persisted = config.fetch_names(db_path)
        if persisted[-ops:] != expected_names:
            raise AssertionError(f"{config.name} persisted rows did not match measured requests")
    finally:
        sampler.stop()
        await sampler_task
        await stop_uvicorn_server(server, task)
        await _maybe_await(config.dispose(app))
        shutil.rmtree(tmpdir, ignore_errors=True)

    return {
        "scenario": config.name,
        "round": round_index,
        "ops": ops,
        "warmup_ops": warmup_ops,
        "startup_seconds": startup_seconds,
        "execution_seconds": execution_seconds,
        "requests_per_second": ops / execution_seconds,
        "latency_seconds": latencies,
        "resource_samples": sampler.samples,
    }


async def run_workload(*, rounds: int, ops: int, warmup_ops: int) -> dict[str, Any]:
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    configs = scenario_configs()
    rng = random.Random(20260505)
    round_payloads: list[dict[str, Any]] = []
    for round_index in range(1, rounds + 1):
        order = list(SCENARIOS)
        rng.shuffle(order)
        results = []
        for name in order:
            results.append(
                await benchmark_once(
                    configs[name],
                    round_index=round_index,
                    ops=ops,
                    warmup_ops=warmup_ops,
                )
            )
        round_payloads.append({"round": round_index, "order": order, "results": results})
    return {"rounds": round_payloads}


def collapse_workload(workload: dict[str, Any]) -> dict[str, Any]:
    by_scenario: dict[str, dict[str, list[Any]]] = {
        name: {
            "requests_per_second": [],
            "latency_seconds": [],
            "startup_seconds": [],
            "resource_samples": [],
        }
        for name in SCENARIOS
    }
    for round_payload in workload["rounds"]:
        for result in round_payload["results"]:
            bucket = by_scenario[result["scenario"]]
            bucket["requests_per_second"].append(result["requests_per_second"])
            bucket["latency_seconds"].extend(result["latency_seconds"])
            bucket["startup_seconds"].append(result["startup_seconds"])
            bucket["resource_samples"].extend(result["resource_samples"])

    return {
        name: {
            "requests_per_second": summarize(bucket["requests_per_second"]),
            "latency_ms": summarize_latency(bucket["latency_seconds"]),
            "startup_seconds": summarize(bucket["startup_seconds"]),
            "resources": resource_summary(bucket["resource_samples"]),
        }
        for name, bucket in by_scenario.items()
    }


def count_python_loc(package_names: tuple[str, ...]) -> dict[str, Any]:
    package_rows = []
    total = 0
    for package_name in package_names:
        module = importlib.import_module(package_name)
        roots = package_roots(module)
        loc = sum(count_python_loc_under(root) for root in roots)
        package_rows.append(
            {
                "package": package_name,
                "path": ";".join(str(root) for root in roots),
                "loc": loc,
            }
        )
        total += loc
    return {"total": total, "packages": package_rows}


def package_roots(module: Any) -> list[Path]:
    paths = getattr(module, "__path__", None)
    if paths is not None:
        return [Path(path) for path in paths]
    package_file_raw = getattr(module, "__file__", None)
    if not package_file_raw:
        raise ValueError(f"cannot resolve package root for {module!r}")
    package_file = Path(package_file_raw)
    return [package_file.parent if package_file.name == "__init__.py" else package_file]


def count_python_loc_under(root: Path) -> int:
    total = 0
    for path in sorted(root.rglob("*.py") if root.is_dir() else [root]):
        if any(part in {"tests", "__pycache__", ".tmp"} for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for raw_line in text.splitlines():
            stripped = raw_line.strip()
            if stripped and not stripped.startswith("#"):
                total += 1
    return total


def build_oci_size(
    scenario: str,
    *,
    base_image: str,
    output_dir: Path,
    require_docker: bool,
) -> dict[str, Any]:
    docker = shutil.which("docker")
    if docker is None:
        if require_docker:
            raise RuntimeError("docker is required for OCI artifact size verification")
        return {
            "status": "skipped",
            "reason": "docker not found",
            "compressed_size_mb": None,
        }

    context_dir = output_dir / f"oci-{scenario}"
    context_dir.mkdir(parents=True, exist_ok=True)
    package = "tigrbl" if scenario == "tigrbl" else "fastapi"
    dockerfile_lines = [
        f"FROM {base_image} AS builder",
        "RUN python -m pip install --no-cache-dir --upgrade pip",
        "RUN python -m venv /opt/venv",
    ]
    if scenario == "tigrbl":
        dockerfile_lines.extend(
            [
                "RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*",
                "COPY pkgs/core/tigrbl /opt/tigrbl/pkgs/core/tigrbl",
                "RUN /opt/venv/bin/pip install --no-cache-dir /opt/tigrbl/pkgs/core/tigrbl",
            ]
        )
    else:
        dockerfile_lines.append("RUN /opt/venv/bin/pip install --no-cache-dir fastapi")
    dockerfile_lines.extend(
        [
            f"FROM {base_image}",
            "COPY --from=builder /opt/venv /opt/venv",
            'ENV PATH="/opt/venv/bin:$PATH"',
            f'CMD ["python", "-c", "import {package}; print({package}.__name__)"]',
        ]
    )
    dockerfile = context_dir / "Dockerfile"
    dockerfile.write_text("\n".join(dockerfile_lines) + "\n", encoding="utf-8")
    tag = f"tigrbl-comparative-benchmark-{scenario}:local"
    build = subprocess.run(
        [docker, "build", "-q", "-t", tag, "-f", str(dockerfile), str(ROOT)],
        capture_output=True,
        text=True,
    )
    if build.returncode != 0:
        raise RuntimeError(
            "OCI image build failed for "
            f"{scenario}:\nSTDOUT:\n{build.stdout}\nSTDERR:\n{build.stderr}"
        )
    image_id = build.stdout.strip()
    archive = output_dir / f"{scenario}.image.tar.gz"
    with archive.open("wb") as raw_file:
        with gzip.GzipFile(fileobj=raw_file, mode="wb") as gz_file:
            save = subprocess.run([docker, "save", tag], check=True, stdout=subprocess.PIPE)
            gz_file.write(save.stdout)
    size_bytes = archive.stat().st_size
    return {
        "status": "measured",
        "base_image": base_image,
        "image_tag": tag,
        "image_id": image_id,
        "compressed_size_bytes": size_bytes,
        "compressed_size_mb": size_bytes / (1024.0 * 1024.0),
        "dockerfile": str(dockerfile),
    }


def compliance_security_posture() -> dict[str, Any]:
    tigrbl_evidence = [
        "pkgs/core/tigrbl_tests/tests/security/test_schemes.py",
        "pkgs/core/tigrbl_tests/tests/unit/test_openapi_documentation_security_behavior.py",
        "pkgs/core/tigrbl_tests/tests/unit/test_docs_security_parity.py",
        "pkgs/core/tigrbl_tests/tests/unit/test_jsonrpc_openrpc.py",
        "certification/claims/current.yaml",
    ]
    fastapi_evidence = []
    for module_name in ("fastapi.security", "fastapi.openapi", "fastapi.exceptions"):
        module = importlib.import_module(module_name)
        fastapi_evidence.append(str(Path(module.__file__ or "")))

    return {
        "tigrbl": {
            "rating": "Strong",
            "score": 2,
            "evidence": tigrbl_evidence,
            "missing_evidence": [
                path for path in tigrbl_evidence if not (ROOT / path).exists()
            ],
            "methodology": (
                "Requires repo evidence for security schemes, OpenAPI/OpenRPC "
                "projection, anonymous-route controls, sanitized errors, and "
                "governance claims."
            ),
        },
        "fastapi": {
            "rating": "Moderate",
            "score": 1,
            "evidence": fastapi_evidence,
            "missing_evidence": [path for path in fastapi_evidence if not Path(path).exists()],
            "methodology": (
                "Requires installed framework evidence for security helpers, "
                "OpenAPI generation, and exception handling modules."
            ),
        },
    }


def machine_info(command: list[str]) -> dict[str, Any]:
    return {
        "command": command,
        "git_sha": _run_text(["git", "rev-parse", "HEAD"]),
        "python": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
    }


def _run_text(command: list[str]) -> str:
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return result.stdout.strip()


def compare_direction(
    line_item: str,
    tigrbl_value: float | str | None,
    fastapi_value: float | str | None,
    *,
    higher_is_better: bool,
) -> dict[str, Any]:
    if tigrbl_value is None or fastapi_value is None:
        passed = False
    elif isinstance(tigrbl_value, str) or isinstance(fastapi_value, str):
        rank = {"Moderate": 1, "Strong": 2}
        passed = rank[str(tigrbl_value)] > rank[str(fastapi_value)]
    elif higher_is_better:
        passed = tigrbl_value > fastapi_value
    else:
        passed = tigrbl_value < fastapi_value
    return {
        "line_item": line_item,
        "reference_benchmark": REFERENCE_BENCHMARK_VALUES[line_item],
        "tigrbl": tigrbl_value,
        "fastapi": fastapi_value,
        "higher_is_better": higher_is_better,
        "passed": passed,
    }


def build_summary(
    *,
    workload_summary: dict[str, Any],
    loc: dict[str, Any],
    oci: dict[str, Any],
    security: dict[str, Any],
) -> dict[str, Any]:
    rows = [
        compare_direction(
            "requests_per_second",
            workload_summary["tigrbl"]["requests_per_second"]["mean"],
            workload_summary["fastapi"]["requests_per_second"]["mean"],
            higher_is_better=True,
        ),
        compare_direction(
            "p95_latency_ms",
            workload_summary["tigrbl"]["latency_ms"]["p95"],
            workload_summary["fastapi"]["latency_ms"]["p95"],
            higher_is_better=False,
        ),
        compare_direction(
            "cpu_usage_percent",
            workload_summary["tigrbl"]["resources"]["cpu_percent"]["average"],
            workload_summary["fastapi"]["resources"]["cpu_percent"]["average"],
            higher_is_better=False,
        ),
        compare_direction(
            "memory_usage_mb",
            workload_summary["tigrbl"]["resources"]["memory_mb"]["average"],
            workload_summary["fastapi"]["resources"]["memory_mb"]["average"],
            higher_is_better=False,
        ),
        compare_direction(
            "lines_of_code",
            loc["tigrbl"]["total"],
            loc["fastapi"]["total"],
            higher_is_better=False,
        ),
        compare_direction(
            "startup_time_seconds",
            workload_summary["tigrbl"]["startup_seconds"]["mean"],
            workload_summary["fastapi"]["startup_seconds"]["mean"],
            higher_is_better=False,
        ),
        compare_direction(
            "deployment_artifact_size_mb",
            oci["tigrbl"]["compressed_size_mb"],
            oci["fastapi"]["compressed_size_mb"],
            higher_is_better=False,
        ),
        compare_direction(
            "compliance_security",
            security["tigrbl"]["rating"],
            security["fastapi"]["rating"],
            higher_is_better=True,
        ),
    ]
    return {
        "line_items": rows,
        "passed": all(row["passed"] for row in rows)
        and not security["tigrbl"]["missing_evidence"]
        and not security["fastapi"]["missing_evidence"],
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Comparative Benchmark Verification",
        "",
        "This report verifies the eight Tigrbl vs FastAPI comparative benchmark line items by measured claim direction, not exact historical value reproduction.",
        "",
        "## Environment",
        f"- git SHA: `{payload['environment']['git_sha']}`",
        f"- platform: `{payload['environment']['platform']}`",
        f"- Python: `{payload['environment']['python'].splitlines()[0]}`",
        "",
        "## Line Item Results",
        "",
        "| Line item | Reference Tigrbl | Reference FastAPI | Measured Tigrbl | Measured FastAPI | Result |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in payload["summary"]["line_items"]:
        result = "PASS" if row["passed"] else "FAIL"
        lines.append(
            "| {line_item} | {it} | {ifast} | {mt} | {mf} | {result} |".format(
                line_item=row["line_item"],
                it=row["reference_benchmark"]["tigrbl"],
                ifast=row["reference_benchmark"]["fastapi"],
                mt=_format_value(row["tigrbl"]),
                mf=_format_value(row["fastapi"]),
                result=result,
            )
        )
    lines.extend(
        [
            "",
            "## Evidence Notes",
            "- RPS, p95 latency, CPU, memory, and startup come from repeated randomized uvicorn parity runs.",
            "- LOC uses the same nonblank, noncomment Python scanner over declared public runtime packages.",
            "- Deployment artifact size uses compressed OCI images built from the same Python base image.",
            "- Compliance and security requires evidence pointers for security projection, controls, errors, and governance posture.",
            "",
        ]
    )
    return "\n".join(lines)


def _format_value(value: float | int | str | None) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


async def run_verification(args: argparse.Namespace, command: list[str]) -> dict[str, Any]:
    workload = await run_workload(
        rounds=args.rounds,
        ops=args.ops,
        warmup_ops=args.warmup_ops,
    )
    workload_summary = collapse_workload(workload)
    configs = scenario_configs()
    loc = {
        name: count_python_loc(configs[name].loc_packages)
        for name in SCENARIOS
    }
    oci_output = Path(args.oci_output_dir)
    oci_output.mkdir(parents=True, exist_ok=True)
    if args.skip_oci:
        oci = {
            name: {
                "status": "skipped",
                "reason": "--skip-oci was set",
                "compressed_size_mb": None,
            }
            for name in SCENARIOS
        }
    else:
        oci = {
            name: build_oci_size(
                name,
                base_image=args.oci_base_image,
                output_dir=oci_output,
                require_docker=True,
            )
            for name in SCENARIOS
        }
    security = compliance_security_posture()
    summary = build_summary(
        workload_summary=workload_summary,
        loc=loc,
        oci=oci,
        security=security,
    )
    return {
        "environment": machine_info(command),
        "methodology": {
            "rounds": args.rounds,
            "ops": args.ops,
            "warmup_ops": args.warmup_ops,
            "runner": "CI Linux authoritative lane",
            "pass_fail": "claim direction",
            "oci_base_image": args.oci_base_image,
        },
        "raw_workload": workload,
        "workload_summary": workload_summary,
        "loc": loc,
        "oci": oci,
        "compliance_security": security,
        "summary": summary,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify all eight Tigrbl vs FastAPI comparative benchmark line items."
    )
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--ops", type=int, default=100)
    parser.add_argument("--warmup-ops", type=int, default=10)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_OUTPUT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MD_OUTPUT)
    parser.add_argument("--oci-output-dir", type=Path, default=TMP_ROOT / "oci")
    parser.add_argument("--oci-base-image", default="python:3.12-slim")
    parser.add_argument("--skip-oci", action="store_true")
    parser.add_argument("--no-fail", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    command = [sys.executable, *sys.argv]
    args = parse_args(list(argv or sys.argv[1:]))
    payload = asyncio.run(run_verification(args, command))
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    args.markdown_output.write_text(render_markdown(payload), encoding="utf-8")
    print(f"Wrote {args.json_output}")
    print(f"Wrote {args.markdown_output}")
    if not payload["summary"]["passed"] and not args.no_fail:
        failed = [
            row["line_item"]
            for row in payload["summary"]["line_items"]
            if not row["passed"]
        ]
        raise SystemExit(f"Comparative benchmark verification failed: {', '.join(failed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
