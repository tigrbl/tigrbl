from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
EXAMPLE_DIR = REPO_ROOT / "examples" / "native_runtime_demo"
SERVER = EXAMPLE_DIR / "server.py"


def _server_env() -> dict[str, str]:
    env = os.environ.copy()
    path_parts = [
        str(EXAMPLE_DIR),
        env.get("PYTHONPATH", ""),
    ]
    env["PYTHONPATH"] = os.pathsep.join(part for part in path_parts if part)
    return env


def _wait_for_server() -> None:
    deadline = time.time() + 20
    while time.time() < deadline:
        probe = subprocess.run(
            [
                "curl.exe",
                "--silent",
                "--output",
                "NUL",
                "--write-out",
                "%{http_code}",
                "http://127.0.0.1:8765/healthz",
            ],
            capture_output=True,
            text=True,
            env=_server_env(),
            check=False,
        )
        if probe.returncode == 0 and probe.stdout.strip() == "200":
            return
        time.sleep(0.25)
    raise AssertionError("server did not become ready")


def test_python_authored_spec_executes_via_rust_runtime_with_curl() -> None:
    preflight = subprocess.run(
        [
            sys.executable,
            "-c",
            "\n".join(
                [
                    "import app_spec",
                    "from tigrbl_runtime import Runtime, compiled_extension_available",
                    "spec = app_spec.compose_app_spec()",
                    "payload = app_spec.build_native_payload()",
                    "handle = Runtime(executor_backend='rust').native_handle(spec)",
                    "assert compiled_extension_available() is True",
                    "assert spec.execution_backend == 'rust'",
                    "assert payload['bindings'][0]['table']['name'] == 'users'",
                    "assert handle.describe().startswith('runtime handle')",
                ]
            ),
        ],
        capture_output=True,
        text=True,
        check=True,
        cwd=EXAMPLE_DIR,
        env=_server_env(),
    )
    assert preflight.returncode == 0

    server = subprocess.Popen(
        [sys.executable, str(SERVER), "--port", "8765"],
        cwd=REPO_ROOT,
        env=_server_env(),
    )
    try:
        _wait_for_server()

        create = subprocess.run(
            [
                "curl.exe",
                "--silent",
                "--show-error",
                "--request",
                "POST",
                "http://127.0.0.1:8765/users",
                "--header",
                "Content-Type: application/json",
                "--data-binary",
                f"@{EXAMPLE_DIR / 'rest-create.json'}",
            ],
            capture_output=True,
            text=True,
            check=True,
            env=_server_env(),
        )
        assert '"id": "u1"' in create.stdout
        assert '"name": "Ada"' in create.stdout

        read = subprocess.run(
            [
                "curl.exe",
                "--silent",
                "--show-error",
                "http://127.0.0.1:8765/users/u1",
            ],
            capture_output=True,
            text=True,
            check=True,
            env=_server_env(),
        )
        assert '"id": "u1"' in read.stdout
        assert '"name": "Ada"' in read.stdout

        rpc_create = subprocess.run(
            [
                "curl.exe",
                "--silent",
                "--show-error",
                "--request",
                "POST",
                "http://127.0.0.1:8765/rpc",
                "--header",
                "Content-Type: application/json",
                "--data-binary",
                f"@{EXAMPLE_DIR / 'rpc-create.json'}",
            ],
            capture_output=True,
            text=True,
            check=True,
            env=_server_env(),
        )
        assert '"name": "Bob"' in rpc_create.stdout

        rpc_read = subprocess.run(
            [
                "curl.exe",
                "--silent",
                "--show-error",
                "--request",
                "POST",
                "http://127.0.0.1:8765/rpc",
                "--header",
                "Content-Type: application/json",
                "--data-binary",
                f"@{EXAMPLE_DIR / 'rpc-read.json'}",
            ],
            capture_output=True,
            text=True,
            check=True,
            env=_server_env(),
        )
        assert '"name": "Bob"' in rpc_read.stdout
    finally:
        server.terminate()
        server.wait(timeout=10)
