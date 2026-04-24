from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener, urlopen


REPO_ROOT = Path(__file__).resolve().parents[4]
EXAMPLE_DIR = REPO_ROOT / "examples" / "rust_runtime_demo"
SERVER = EXAMPLE_DIR / "server.py"


def _server_env() -> dict[str, str]:
    env = os.environ.copy()
    path_parts = [
        str(EXAMPLE_DIR),
        env.get("PYTHONPATH", ""),
    ]
    env["PYTHONPATH"] = os.pathsep.join(part for part in path_parts if part)
    return env


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        return None


def _read_text(url: str) -> str:
    with urlopen(url, timeout=5) as response:
        return response.read().decode("utf-8")


def _read_redirect(url: str) -> tuple[int, str]:
    opener = build_opener(_NoRedirect)
    try:
        opener.open(Request(url), timeout=5)
    except HTTPError as exc:
        return exc.code, exc.headers.get("Location", "")
    raise AssertionError(f"{url} did not redirect")


class DemoServer:
    def __init__(self) -> None:
        self.port = _free_port()
        self.base_url = f"http://127.0.0.1:{self.port}"
        self.process: subprocess.Popen[str] | None = None

    def __enter__(self) -> "DemoServer":
        self.process = subprocess.Popen(
            [sys.executable, str(SERVER), "--port", str(self.port)],
            cwd=REPO_ROOT,
            env=_server_env(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        deadline = time.time() + 20
        while time.time() < deadline:
            if self.process.poll() is not None:
                _, stderr = self.process.communicate(timeout=5)
                raise AssertionError(f"rust runtime demo exited early: {stderr}")
            try:
                _read_text(f"{self.base_url}/docs")
                return self
            except (ConnectionError, OSError, URLError):
                time.sleep(0.25)
        raise AssertionError("rust runtime demo did not become ready")

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
        if self.process is None:
            return
        self.process.terminate()
        self.process.communicate(timeout=10)

    def stop(self) -> tuple[str, str]:
        assert self.process is not None
        self.process.terminate()
        stdout, stderr = self.process.communicate(timeout=10)
        self.process = None
        return stdout, stderr


def test_rust_runtime_demo_favicon_routes() -> None:
    with DemoServer() as server:
        favicon = _read_text(f"{server.base_url}/favicon.svg")
        redirect_code, redirect_target = _read_redirect(f"{server.base_url}/favicon.ico")

    assert "<svg" in favicon
    assert redirect_code == 307
    assert redirect_target == "/favicon.svg"


def test_rust_runtime_demo_swagger_uix() -> None:
    with DemoServer() as server:
        swagger = _read_text(f"{server.base_url}/swagger")

    assert "swagger-ui" in swagger.lower()
    assert 'url: "/openapi.json"' in swagger
    assert "console.info" in swagger
    assert 'href="/favicon.svg"' in swagger


def test_rust_runtime_demo_lens_uix() -> None:
    with DemoServer() as server:
        lens = _read_text(f"{server.base_url}/lens")

    assert "@tigrbljs/tigrbl-lens" in lens
    assert 'url: "/openrpc.json"' in lens
    assert "console.info" in lens
    assert 'href="/favicon.svg"' in lens


def test_rust_runtime_demo_console_logs() -> None:
    server = DemoServer()
    with server:
        _read_text(f"{server.base_url}/docs")
        _read_text(f"{server.base_url}/swagger")
        _read_text(f"{server.base_url}/lens")
        _, stderr = server.stop()

    assert '"event": "http.request"' in stderr
    assert "/docs" in stderr
    assert "/swagger" in stderr
    assert "/lens" in stderr
