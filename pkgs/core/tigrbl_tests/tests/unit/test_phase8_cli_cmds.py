from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[5]
FIXTURE = REPO_ROOT / "pkgs" / "core" / "tigrbl_tests" / "tests" / "fixtures" / "phase8_cli_app.py"
TARGET = f"{FIXTURE}:app"


def _pythonpath() -> str:
    parts: list[str] = []
    for base in (REPO_ROOT / "pkgs" / "core", REPO_ROOT / "pkgs" / "apps", REPO_ROOT / "pkgs" / "engines"):
        if not base.exists():
            continue
        for child in sorted(base.iterdir()):
            if child.is_dir():
                parts.append(str(child))
                src = child / "src"
                if src.is_dir():
                    parts.append(str(src))
    parts.append(str(REPO_ROOT))
    return os.pathsep.join(parts)


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = _pythonpath()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, "-m", "tigrbl", *args],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_routes_command_smoke_lists_http_websocket_and_docs_routes() -> None:
    result = _run_cli(
        "routes",
        TARGET,
        "--docs-path",
        "/api-docs",
        "--openapi-path",
        "/schema.json",
        "--openrpc-path",
        "/rpc.json",
        "--lens-path",
        "/rpc-ui",
    )

    assert result.returncode == 0, result.stderr
    assert "/ping" in result.stdout
    assert "/ws/echo" in result.stdout
    assert "/api-docs" in result.stdout
    assert "/schema.json" in result.stdout
    assert "/rpc.json" in result.stdout
    assert "/rpc-ui" in result.stdout


def test_openapi_command_smoke_outputs_openapi_document() -> None:
    result = _run_cli("openapi", TARGET)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["openapi"] == "3.1.0"
    assert "/ping" in payload["paths"]


def test_openrpc_command_smoke_outputs_openrpc_document() -> None:
    result = _run_cli("openrpc", TARGET)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["openrpc"] == "1.2.6"
    assert "methods" in payload
    assert "servers" in payload


def test_doctor_command_smoke_outputs_app_summary() -> None:
    result = _run_cli(
        "doctor",
        TARGET,
        "--docs-path",
        "/api-docs",
        "--openapi-path",
        "/schema.json",
        "--openrpc-path",
        "/rpc.json",
        "--lens-path",
        "/rpc-ui",
        "--statsd-addr",
        "127.0.0.1:8125",
        "--dogstatsd-tags",
        "env:test,service:tigrbl",
        "--otel-endpoint",
        "http://127.0.0.1:4318",
        "--trace-sample-rate",
        "0.5",
        "--drain-timeout",
        "11",
        "--shutdown-timeout",
        "12",
        "--concurrency-limit",
        "64",
        "--admission-queue",
        "128",
        "--backlog",
        "256",
        "--ws-heartbeat",
        "15",
        "--ws-heartbeat-timeout",
        "18",
        "--http2-max-concurrent-streams",
        "99",
        "--http2-initial-window-size",
        "131072",
        "--http3-max-data",
        "2097152",
        "--http3-max-uni-streams",
        "24",
        "--alpn-policy",
        "h3,h2",
        "--ocsp-policy",
        "strict",
        "--revocation-policy",
        "strict",
        "--interop-bundle-dir",
        "docs/conformance/audit/2026/p8-cli",
        "--benchmark-bundle-dir",
        "reports/current_state/benchmarks",
        "--deployment-profile",
        "strict-h3-edge",
        "--proxy-contract",
        "edge-normalized",
        "--early-data-policy",
        "edge-replay-guarded",
        "--origin-static-policy",
        "edge-static",
        "--quic-metrics",
        "connections,retry",
        "--qlog-dir",
        "reports/current_state/benchmarks/qlog",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["title"] == "CLI Smoke App"
    assert payload["version"] == "8.0.0"
    assert payload["docs_paths"] == {
        "docs": "/api-docs",
        "openapi": "/schema.json",
        "openrpc": "/rpc.json",
        "lens": "/rpc-ui",
    }
    assert payload["routes"]["count"] >= 1
    assert payload["routes"]["websocket_count"] >= 1
    assert payload["operator_controls"] == {
        "statsd_addr": "127.0.0.1:8125",
        "dogstatsd_tags": ["env:test", "service:tigrbl"],
        "otel_endpoint": "http://127.0.0.1:4318",
        "trace_sample_rate": 0.5,
        "drain_timeout": 11.0,
        "shutdown_timeout": 12.0,
        "concurrency_limit": 64,
        "admission_queue": 128,
        "backlog": 256,
        "ws_heartbeat": 15.0,
        "ws_heartbeat_timeout": 18.0,
        "http2_max_concurrent_streams": 99,
        "http2_initial_window_size": 131072,
        "http3_max_data": 2097152,
        "http3_max_uni_streams": 24,
        "alpn_policy": ["h3", "h2"],
        "ocsp_policy": "strict",
        "revocation_policy": "strict",
        "interop_bundle_dir": "docs/conformance/audit/2026/p8-cli",
        "benchmark_bundle_dir": "reports/current_state/benchmarks",
        "deployment_profile": "strict-h3-edge",
        "proxy_contract": "edge-normalized",
        "early_data_policy": "edge-replay-guarded",
        "origin_static_policy": "edge-static",
        "quic_metrics": ["connections", "retry"],
        "qlog_dir": "reports/current_state/benchmarks/qlog",
    }


def test_capabilities_command_smoke_outputs_commands_flags_servers_and_target() -> None:
    result = _run_cli("capabilities", TARGET)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["commands"] == [
        "run",
        "serve",
        "dev",
        "routes",
        "openapi",
        "openrpc",
        "doctor",
        "capabilities",
    ]
    assert "--server" in payload["flags"]
    assert "--statsd-addr" in payload["flags"]
    assert "--otel-endpoint" in payload["flags"]
    assert "--concurrency-limit" in payload["flags"]
    assert "--http3-max-data" in payload["flags"]
    assert "--alpn-policy" in payload["flags"]
    assert "--interop-bundle-dir" in payload["flags"]
    assert "--deployment-profile" in payload["flags"]
    assert "--proxy-contract" in payload["flags"]
    assert "--early-data-policy" in payload["flags"]
    assert "--origin-static-policy" in payload["flags"]
    assert "--quic-metrics" in payload["flags"]
    assert "--qlog-dir" in payload["flags"]
    assert set(payload["servers"]) == {"uvicorn", "hypercorn", "gunicorn", "tigrcorn"}
    assert payload["app"]["title"] == "CLI Smoke App"
    assert "operator_controls" in payload["app"]
