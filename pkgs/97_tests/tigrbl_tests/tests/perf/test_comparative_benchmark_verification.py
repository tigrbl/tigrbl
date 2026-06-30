from __future__ import annotations

import sys
from pathlib import Path

import pytest

BENCHMARKS_ROOT = Path(__file__).resolve().parents[2] / "benchmarks"
sys.path.insert(0, str(BENCHMARKS_ROOT))

from comparative_benchmark_verification import (  # noqa: E402
    build_summary,
    count_python_loc_under,
    parse_args,
    quantile,
    render_markdown,
    resource_summary,
    summarize,
    summarize_latency,
)


def test_comparative_benchmark_defaults_match_real_transport_250_op_suite() -> None:
    args = parse_args([])

    assert args.rounds == 10
    assert args.ops == 250
    assert args.warmup_ops == 0
    assert args.pre_measurement_wait_seconds == 0.5


def test_comparative_benchmark_is_the_250_op_httpxtransport_suite() -> None:
    args = parse_args([])

    assert args.ops == 250
    assert args.rounds == 10
    assert args.pre_measurement_wait_seconds == 0.5


def test_comparative_benchmark_metric_summaries_are_stable() -> None:
    values = [1.0, 2.0, 3.0, 4.0]

    summary = summarize(values)

    assert summary["sample_count"] == 4
    assert summary["mean"] == 2.5
    assert summary["median"] == 2.5
    assert quantile(values, 0.95) == pytest.approx(3.85)


def test_comparative_benchmark_latency_summary_reports_p95_ms() -> None:
    summary = summarize_latency([0.001, 0.002, 0.003, 0.004])

    assert summary["p50"] == pytest.approx(2.5)
    assert summary["p95"] == pytest.approx(3.85)
    assert summary["p99"] == pytest.approx(3.97)


def test_comparative_benchmark_resource_summary_reports_cpu_and_memory() -> None:
    summary = resource_summary(
        [
            {"cpu_percent": 10.0, "rss_mb": 20.0, "timestamp": 1.0},
            {"cpu_percent": 20.0, "rss_mb": 25.0, "timestamp": 2.0},
            {"cpu_percent": 30.0, "rss_mb": 22.0, "timestamp": 3.0},
        ]
    )

    assert summary["cpu_percent"]["average"] == 20.0
    assert summary["cpu_percent"]["peak"] == 30.0
    assert summary["memory_mb"]["baseline"] == 20.0
    assert summary["memory_mb"]["peak"] == 25.0
    assert summary["memory_mb"]["delta"] == 5.0


def test_comparative_benchmark_loc_counter_skips_blank_comments_and_tests(
    tmp_path: Path,
) -> None:
    package = tmp_path / "pkg"
    tests = package / "tests"
    tests.mkdir(parents=True)
    (package / "__init__.py").write_text(
        "\n# comment\nVALUE = 1\n\n\ndef run():\n    return VALUE\n",
        encoding="utf-8",
    )
    (tests / "test_ignored.py").write_text("SHOULD_NOT_COUNT = True\n", encoding="utf-8")

    assert count_python_loc_under(package) == 3


def test_comparative_benchmark_summary_requires_all_claim_directions() -> None:
    workload = {
        "tigrbl": {
            "requests_per_second": {"mean": 200.0},
            "latency_ms": {"p95": 2.0},
            "startup_seconds": {"mean": 0.1},
            "resources": {
                "cpu_percent": {"average": 10.0},
                "memory_mb": {"average": 20.0},
            },
        },
        "fastapi": {
            "requests_per_second": {"mean": 100.0},
            "latency_ms": {"p95": 4.0},
            "startup_seconds": {"mean": 0.2},
            "resources": {
                "cpu_percent": {"average": 20.0},
                "memory_mb": {"average": 40.0},
            },
        },
    }
    loc = {"tigrbl": {"total": 10}, "fastapi": {"total": 20}}
    oci = {
        "tigrbl": {"compressed_size_mb": 5.0},
        "fastapi": {"compressed_size_mb": 10.0},
    }
    security = {
        "tigrbl": {"rating": "Strong", "missing_evidence": []},
        "fastapi": {"rating": "Moderate", "missing_evidence": []},
    }

    summary = build_summary(
        workload_summary=workload,
        loc=loc,
        oci=oci,
        security=security,
    )

    assert summary["passed"] is True
    assert len(summary["line_items"]) == 8


def test_comparative_benchmark_markdown_contains_all_line_items() -> None:
    payload = {
        "environment": {
            "git_sha": "abc",
            "platform": "linux",
            "python": "3.12",
        },
        "methodology": {
            "rounds": 10,
            "ops": 250,
            "pre_measurement_wait_seconds": 0.5,
            "transport_kind": "httpxtransport",
            "shared_runner": "httpx.AsyncClient over uvicorn real HTTP transport",
        },
        "summary": {
            "line_items": [
                {
                    "line_item": "requests_per_second",
                    "reference_benchmark": {"tigrbl": "77,958", "fastapi": "15,974"},
                    "tigrbl": 200.0,
                    "fastapi": 100.0,
                    "passed": True,
                }
            ]
        },
    }

    markdown = render_markdown(payload)

    assert "Comparative Benchmark Verification" in markdown
    assert "requests_per_second" in markdown
    assert "PASS" in markdown
