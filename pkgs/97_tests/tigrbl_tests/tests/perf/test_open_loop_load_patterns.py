from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

BENCHMARKS_ROOT = Path(__file__).resolve().parents[2] / "benchmarks"
sys.path.insert(0, str(BENCHMARKS_ROOT))

from open_loop_load_patterns import (  # noqa: E402
    CommandResult,
    DriverExecutionError,
    PatternValidationError,
    Segment,
    list_patterns,
    load_pattern,
    normalize_vegeta_report,
    parse_pattern,
    parse_wrk2_output,
    render_body,
    render_markdown_report,
    render_target,
    resolve_driver_executable,
    run_pattern_segments,
)


def test_parse_pattern_validates_required_shape() -> None:
    pattern = parse_pattern(
        {
            "name": "small",
            "driver": "vegeta",
            "target": "rest-create",
            "segments": [
                {"name": "steady", "rate_per_second": 100, "duration_seconds": 5}
            ],
            "metadata": {"server": "uvicorn"},
        }
    )

    assert pattern.name == "small"
    assert pattern.driver == "vegeta"
    assert pattern.segments[0].rate_per_second == 100
    assert pattern.metadata["server"] == "uvicorn"


def test_parse_pattern_rejects_unknown_driver() -> None:
    with pytest.raises(PatternValidationError, match="unsupported driver"):
        parse_pattern(
            {
                "name": "bad",
                "driver": "closed-loop",
                "target": "rest-create",
                "segments": [
                    {"name": "steady", "rate_per_second": 1, "duration_seconds": 1}
                ],
            }
        )


def test_builtin_pattern_driver_override_is_validated() -> None:
    pattern = load_pattern("steady-rest", driver_override="wrk2")

    assert pattern.driver == "wrk2"
    assert "steady-rest" in list_patterns()


def test_render_targets_and_bodies() -> None:
    body_path = Path("body.json")

    rest_target = render_target("http://127.0.0.1:8000", "rest-create", body_path)
    rpc_target = render_target("http://127.0.0.1:8000", "jsonrpc-create", body_path)
    rest_body = json.loads(render_body("rest-create", Segment("steady", 10, 1)))
    rpc_body = json.loads(render_body("jsonrpc-create", Segment("steady", 10, 1)))

    assert rest_target.startswith("POST http://127.0.0.1:8000/items")
    assert rpc_target.startswith("POST http://127.0.0.1:8000/rpc")
    assert rest_body == {"name": "open-loop-steady"}
    assert rpc_body["method"] == "BenchmarkItem.create"
    assert rpc_body["params"] == {"name": "open-loop-steady"}


def test_normalize_vegeta_report_converts_latency_and_counts() -> None:
    segment = Segment("steady", 100, 10)
    summary = normalize_vegeta_report(
        {
            "requests": 10,
            "throughput": 9.5,
            "duration": 10_000_000_000,
            "status_codes": {"201": 8, "500": 2},
            "errors": ["Get http://x: timeout"],
            "latencies": {
                "50th": 1_000_000,
                "90th": 2_000_000,
                "95th": 3_000_000,
                "99th": 4_000_000,
                "99.9th": 5_000_000,
            },
        },
        segment=segment,
        command=("vegeta", "report"),
    )

    assert summary["success_count"] == 8
    assert summary["error_count"] == 2
    assert summary["timeout_count"] == 1
    assert summary["latency_ms"]["p95"] == 3.0
    assert summary["achieved_throughput_per_second"] == 9.5


def test_parse_wrk2_output_reads_distribution_and_errors() -> None:
    output = """
Running 10s test @ http://127.0.0.1:8000/items
  4 threads and 64 connections
  Latency Distribution (HdrHistogram - Recorded Latency)
     50.000%    1.20ms
     90.000%    2.50ms
     95.000%    3.50ms
     99.000%    8.00ms
     99.900%   12.00ms
  1000 requests in 10.00s, 1.20MB read
  Socket errors: connect 0, read 0, write 0, timeout 2
  Non-2xx or 3xx responses: 3
Requests/sec:    99.50
"""

    summary = parse_wrk2_output(
        output,
        segment=Segment("steady", 100, 10),
        command=("wrk2", "--latency"),
    )

    assert summary["success_count"] == 997
    assert summary["error_count"] == 5
    assert summary["timeout_count"] == 2
    assert summary["latency_ms"]["p99_9"] == 12.0
    assert summary["achieved_throughput_per_second"] == 99.5


def test_missing_driver_messages_are_actionable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("open_loop_load_patterns.shutil.which", lambda _driver: None)

    with pytest.raises(DriverExecutionError, match="install vegeta or choose --driver wrk2"):
        resolve_driver_executable("vegeta")
    with pytest.raises(DriverExecutionError, match="install wrk2 or choose --driver vegeta"):
        resolve_driver_executable("wrk2")


def test_markdown_report_contains_segment_table() -> None:
    markdown = render_markdown_report(
        {
            "pattern": "steady-rest",
            "driver": "vegeta",
            "target": "rest-create",
            "environment": {"server_url": "http://127.0.0.1:8000"},
            "segments": [
                {
                    "segment": {"name": "steady"},
                    "offered_rate_per_second": 100,
                    "achieved_throughput_per_second": 99.5,
                    "success_count": 995,
                    "error_count": 5,
                    "timeout_count": 1,
                    "latency_ms": {"p50": 1.0, "p95": 3.0, "p99": 5.0},
                }
            ],
        }
    )

    assert "Open-Loop Load Pattern Report" in markdown
    assert "| steady | 100 | 99.50 | 995 | 5 | 1 | 1.00 | 3.00 | 5.00 |" in markdown


def test_run_pattern_segments_with_fake_vegeta_writes_artifacts(tmp_path: Path) -> None:
    pattern = parse_pattern(
        {
            "name": "fake",
            "driver": "vegeta",
            "target": "rest-create",
            "segments": [
                {"name": "steady", "rate_per_second": 10, "duration_seconds": 1}
            ],
            "metadata": {"server": "fake"},
        }
    )

    def fake_runner(command, _stdin):
        if "attack" in command:
            return CommandResult(b"raw-result", b"", 0, tuple(command))
        return CommandResult(
            json.dumps(
                {
                    "requests": 10,
                    "throughput": 10.0,
                    "duration": 1_000_000_000,
                    "status_codes": {"201": 10},
                    "latencies": {"50th": 1_000_000, "95th": 2_000_000},
                }
            ).encode("utf-8"),
            b"",
            0,
            tuple(command),
        )

    manifest = run_pattern_segments(
        pattern,
        base_url="http://127.0.0.1:8000",
        output_dir=tmp_path,
        driver_executable="vegeta",
        runner=fake_runner,
    )

    assert Path(manifest["manifest_path"]).exists()
    assert Path(manifest["report_path"]).exists()
    assert Path(manifest["segments"][0]["raw_path"]).read_bytes() == b"raw-result"
    assert manifest["segments"][0]["success_count"] == 10
