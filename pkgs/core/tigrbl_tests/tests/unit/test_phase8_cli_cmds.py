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
    parts.append(str(REPO_ROOT / "bindings" / "python" / "tigrbl_native" / "python"))
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
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["title"] == "Phase 8 CLI App"
    assert payload["version"] == "8.0.0"
    assert payload["docs_paths"] == {
        "docs": "/api-docs",
        "openapi": "/schema.json",
        "openrpc": "/rpc.json",
        "lens": "/rpc-ui",
    }
    assert payload["routes"]["count"] >= 1
    assert payload["routes"]["websocket_count"] >= 1


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
    assert set(payload["servers"]) == {"uvicorn", "hypercorn", "gunicorn", "tigrcorn"}
    assert payload["app"]["title"] == "Phase 8 CLI App"
