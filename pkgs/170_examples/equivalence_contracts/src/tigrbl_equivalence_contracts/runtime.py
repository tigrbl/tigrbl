"""Shared runtime mechanics for per-equivalence proofs."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
import socket
import threading
import time
from typing import Any, Literal

ServerKind = Literal["asgi", "wsgi"]


@dataclass(frozen=True)
class RunningHttpServer:
    """A real local HTTP server started for one equivalence proof."""

    base_url: str
    stop: Callable[[], None]


def start_http_server(app: Any, server_kind: ServerKind) -> RunningHttpServer:
    """Start an ASGI or WSGI app with the shared local-server lifecycle."""

    if server_kind == "asgi":
        return _start_asgi_server(app)
    if server_kind == "wsgi":
        return _start_wsgi_server(app)
    raise ValueError(f"unsupported server kind: {server_kind}")


def assert_route_surface_over_http(
    app: Any,
    server_kind: ServerKind,
    expected_routes: tuple[tuple[str, tuple[str, ...]], ...],
) -> tuple[dict[str, Any], ...]:
    """Start one app and assert its OpenAPI route surface over HTTP."""

    import httpx

    server = start_http_server(app, server_kind)
    try:
        with httpx.Client(base_url=server.base_url, timeout=10.0) as client:
            response = client.get("/openapi.json")
            assert response.status_code == 200
            return _select_route_surface(response.json(), expected_routes)
    finally:
        server.stop()


def _select_route_surface(
    openapi_payload: Mapping[str, Any],
    expected_routes: tuple[tuple[str, tuple[str, ...]], ...],
) -> tuple[dict[str, Any], ...]:
    paths = openapi_payload.get("paths", {})
    selected: list[dict[str, Any]] = []
    for path, expected_methods in expected_routes:
        operations = paths.get(path)
        assert operations is not None, f"missing path {path}"
        observed_methods = tuple(
            method for method in expected_methods if method.lower() in operations
        )
        assert observed_methods == expected_methods
        selected.append({"path": path, "methods": observed_methods})
    return tuple(selected)


def _start_asgi_server(app: Any) -> RunningHttpServer:
    """Serve a Tigrbl or FastAPI ASGI app with uvicorn."""

    import uvicorn

    port = _free_http_port()
    server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=port, lifespan="off", log_level="warning")
    )
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{port}"
    _wait_for_http_server(base_url)

    def stop() -> None:
        server.should_exit = True
        thread.join(timeout=10)

    return RunningHttpServer(base_url=base_url, stop=stop)


def _start_wsgi_server(app: Any) -> RunningHttpServer:
    """Serve a Flask WSGI app with Werkzeug's local server."""

    from werkzeug.serving import make_server

    port = _free_http_port()
    server = make_server("127.0.0.1", port, app)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{port}"
    _wait_for_http_server(base_url)

    def stop() -> None:
        server.shutdown()
        thread.join(timeout=10)

    return RunningHttpServer(base_url=base_url, stop=stop)


def _wait_for_http_server(base_url: str) -> None:
    """Block until a just-started local server accepts HTTP requests."""

    import httpx

    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        try:
            httpx.get(f"{base_url}/healthz", timeout=2.0)
            return
        except (httpx.ConnectError, httpx.ReadError, httpx.ConnectTimeout, httpx.ReadTimeout):
            time.sleep(0.05)
    raise RuntimeError(f"server did not start at {base_url}")


def _free_http_port() -> int:
    """Ask the OS for an available localhost TCP port for a demo server."""

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])
