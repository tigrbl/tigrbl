"""HTTP pedagogy for certifying framework equivalence.

The framework implementation files show how a Tigrbl, FastAPI, or Flask app is
authored.  This file shows the shared runtime lesson that every implementation
must satisfy:

1. start a real local HTTP server;
2. call that server with ``httpx``;
3. assert the exact Widget CRUD responses that developers should expect.

Keeping startup and client assertions here is intentional.  If three frameworks
claim the same REST CRUD behavior, they should be served and exercised by the
same proof code.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import socket
import threading
import time
from typing import Any, Literal, Mapping

WidgetCrudEvidence = tuple[dict, ...]
ServerKind = Literal["asgi", "wsgi"]
HttpMethod = Literal["DELETE", "GET", "PATCH", "POST", "PUT"]
RouteSurface = tuple[tuple[str, tuple[HttpMethod, ...]], ...]

EXPECTED_WIDGET_CRUD_EVIDENCE: WidgetCrudEvidence = (
    {
        "step": "create",
        "status_code": 201,
        "json": {"id": "widget-1", "name": "First"},
    },
    {
        "step": "read_created",
        "status_code": 200,
        "json": {"id": "widget-1", "name": "First"},
    },
    {
        "step": "list_created",
        "status_code": 200,
        "json": [{"id": "widget-1", "name": "First"}],
    },
    {
        "step": "update",
        "status_code": 200,
        "json": {"id": "widget-1", "name": "Second"},
    },
    {"step": "delete", "status_code": 200, "json": {"deleted": 1}},
    {"step": "list_deleted", "status_code": 200, "json": []},
)

TABLE_CLASS_SURFACES: tuple[dict[str, Any], ...] = (
    {
        "slug": "table-base",
        "class_name": "TableBase",
        "path_root": "/widgettablebase",
        "routes": (
            ("/widgettablebase", ("GET", "POST", "DELETE")),
            ("/widgettablebase/{item_id}", ("GET", "PATCH", "PUT", "DELETE")),
        ),
    },
    {
        "slug": "rest-table",
        "class_name": "RestTable",
        "path_root": "/widgetresttable",
        "routes": (
            ("/widgetresttable", ("GET", "POST", "DELETE")),
            ("/widgetresttable/{item_id}", ("GET", "PATCH", "PUT", "DELETE")),
        ),
    },
    {
        "slug": "json-rpc-table",
        "class_name": "JsonRpcTable",
        "path_root": "/widgetjsonrpctable",
        "routes": (
            ("/widgetjsonrpctable", ("GET", "POST", "DELETE")),
            ("/widgetjsonrpctable/{item_id}", ("GET", "PATCH", "PUT", "DELETE")),
        ),
    },
    {
        "slug": "rest-json-rpc-table",
        "class_name": "RestJsonRpcTable",
        "path_root": "/widgetrestjsonrpctable",
        "routes": (
            ("/widgetrestjsonrpctable", ("GET", "POST", "DELETE")),
            (
                "/widgetrestjsonrpctable/{item_id}",
                ("GET", "PATCH", "PUT", "DELETE"),
            ),
        ),
    },
    {
        "slug": "bulk-crud-table",
        "class_name": "BulkCrudTable",
        "path_root": "/widgetbulkcrudtable",
        "routes": (
            ("/widgetbulkcrudtable", ("GET", "POST", "PATCH", "PUT", "DELETE")),
            ("/widgetbulkcrudtable/{item_id}", ("GET", "PATCH", "PUT", "DELETE")),
        ),
    },
    {
        "slug": "rest-oltp-table",
        "class_name": "RestOltpTable",
        "path_root": "/widgetrestoltptable",
        "routes": (
            ("/widgetrestoltptable", ("GET", "POST")),
            ("/widgetrestoltptable/{item_id}", ("GET", "PATCH", "PUT", "DELETE")),
        ),
    },
    {
        "slug": "oltp-table",
        "class_name": "OltpTable",
        "path_root": "/widgetoltptable",
        "routes": (
            ("/widgetoltptable", ("GET", "POST")),
            ("/widgetoltptable/{item_id}", ("GET", "PATCH", "PUT", "DELETE")),
        ),
    },
    {
        "slug": "json-rpc-oltp-table",
        "class_name": "JsonRpcOltpTable",
        "path_root": "/widgetjsonrpcoltptable",
        "routes": (
            ("/widgetjsonrpcoltptable", ("GET", "POST")),
            ("/widgetjsonrpcoltptable/{item_id}", ("GET", "PATCH", "PUT", "DELETE")),
        ),
    },
    {
        "slug": "rest-json-rpc-oltp-table",
        "class_name": "RestJsonRpcOltpTable",
        "path_root": "/widgetrestjsonrpcoltptable",
        "routes": (
            ("/widgetrestjsonrpcoltptable", ("GET", "POST")),
            (
                "/widgetrestjsonrpcoltptable/{item_id}",
                ("GET", "PATCH", "PUT", "DELETE"),
            ),
        ),
    },
    {
        "slug": "rest-olap-table",
        "class_name": "RestOlapTable",
        "path_root": "/widgetrestolaptable",
        "routes": (
            ("/widgetrestolaptable", ("GET", "POST")),
            ("/widgetrestolaptable/{item_id}", ("GET",)),
        ),
    },
    {
        "slug": "olap-table",
        "class_name": "OlapTable",
        "path_root": "/widgetolaptable",
        "routes": (
            ("/widgetolaptable", ("GET", "POST")),
            ("/widgetolaptable/{item_id}", ("GET",)),
        ),
    },
    {
        "slug": "json-rpc-olap-table",
        "class_name": "JsonRpcOlapTable",
        "path_root": "/widgetjsonrpcolaptable",
        "routes": (
            ("/widgetjsonrpcolaptable", ("GET", "POST")),
            ("/widgetjsonrpcolaptable/{item_id}", ("GET",)),
        ),
    },
    {
        "slug": "rest-json-rpc-olap-table",
        "class_name": "RestJsonRpcOlapTable",
        "path_root": "/widgetrestjsonrpcolaptable",
        "routes": (
            ("/widgetrestjsonrpcolaptable", ("GET", "POST")),
            ("/widgetrestjsonrpcolaptable/{item_id}", ("GET",)),
        ),
    },
    {
        "slug": "stream-table",
        "class_name": "StreamTable",
        "path_root": "/widgetstreamtable",
        "routes": (("/widgetstreamtable", ("GET",)),),
    },
    {
        "slug": "sse-table",
        "class_name": "SseTable",
        "path_root": "/widgetssetable",
        "routes": (("/widgetssetable", ("GET",)),),
    },
    {
        "slug": "event-stream-table",
        "class_name": "EventStreamTable",
        "path_root": "/widgeteventstreamtable",
        "routes": (("/widgeteventstreamtable", ("GET",)),),
    },
    {
        "slug": "web-socket-table",
        "class_name": "WebSocketTable",
        "path_root": "/widgetwebsockettable",
        "routes": (("/widgetwebsockettable", ("GET", "POST")),),
    },
    {
        "slug": "web-socket-json-rpc-table",
        "class_name": "WebSocketJsonRpcTable",
        "path_root": "/widgetwebsocketjsonrpctable",
        "routes": (
            ("/widgetwebsocketjsonrpctable", ("GET", "POST")),
            (
                "/widgetwebsocketjsonrpctable/{item_id}",
                ("GET", "PATCH", "PUT", "DELETE"),
            ),
        ),
    },
    {
        "slug": "web-transport-table",
        "class_name": "WebTransportTable",
        "path_root": "/widgetwebtransporttable",
        "routes": (("/widgetwebtransporttable", ("GET", "POST")),),
    },
    {
        "slug": "web-transport-bidi-table",
        "class_name": "WebTransportBidiTable",
        "path_root": "/widgetwebtransportbiditable",
        "routes": (("/widgetwebtransportbiditable", ("GET", "POST")),),
    },
    {
        "slug": "web-transport-client-stream-table",
        "class_name": "WebTransportClientStreamTable",
        "path_root": "/widgetwebtransportclientstreamtable",
        "routes": (("/widgetwebtransportclientstreamtable", ("POST",)),),
    },
    {
        "slug": "web-transport-server-stream-table",
        "class_name": "WebTransportServerStreamTable",
        "path_root": "/widgetwebtransportserverstreamtable",
        "routes": (("/widgetwebtransportserverstreamtable", ("GET",)),),
    },
    {
        "slug": "web-transport-datagram-table",
        "class_name": "WebTransportDatagramTable",
        "path_root": "/widgetwebtransportdatagramtable",
        "routes": (("/widgetwebtransportdatagramtable", ("POST",)),),
    },
)


@dataclass(frozen=True)
class RunningHttpServer:
    """A tiny handle for a real local server created by this runtime lesson.

    The common startup path returns the base URL used by the shared client
    assertions and a stop callback used after the proof has finished.
    """

    base_url: str
    stop: Callable[[], None]


def start_http_server(app: Any, server_kind: ServerKind) -> RunningHttpServer:
    """Start an ASGI or WSGI app as a real local HTTP server.

    The app object comes from the framework example.  The mechanics here are
    deliberately shared so the equivalence proof does not depend on three
    separate copies of port selection, thread startup, readiness polling, or
    shutdown behavior.
    """

    if server_kind == "asgi":
        return _start_asgi_server(app)
    if server_kind == "wsgi":
        return _start_wsgi_server(app)
    raise ValueError(f"unsupported server kind: {server_kind}")


class WidgetCrudClientAssertions:
    """The single client-side proof used for every Widget CRUD equivalence.

    This class is written as documentation as much as test code.  Reading the
    ``run`` method should tell a developer the API shape, the request order, and
    the exact response payloads expected from Tigrbl, FastAPI, and Flask.
    """

    def run(self, base_url: str) -> WidgetCrudEvidence:
        """Call the server with ``httpx`` and assert the Widget CRUD contract."""

        import httpx

        with httpx.Client(base_url=base_url, timeout=10.0) as client:
            # The examples use an in-memory database, but cleanup keeps repeated
            # local test runs easy to reason about.
            client.delete("/widget/widget-1")

            create = client.post(
                "/widget", json={"id": "widget-1", "name": "First"}
            )
            assert create.status_code == 201
            assert create.json() == {"id": "widget-1", "name": "First"}

            read_created = client.get("/widget/widget-1")
            assert read_created.status_code == 200
            assert read_created.json() == {"id": "widget-1", "name": "First"}

            list_created = client.get("/widget")
            assert list_created.status_code == 200
            assert list_created.json() == [{"id": "widget-1", "name": "First"}]

            update = client.patch(
                "/widget/widget-1", json={"id": "widget-1", "name": "Second"}
            )
            assert update.status_code == 200
            assert update.json() == {"id": "widget-1", "name": "Second"}

            delete = client.delete("/widget/widget-1")
            assert delete.status_code == 200
            assert delete.json() == {"deleted": 1}

            list_deleted = client.get("/widget")
            assert list_deleted.status_code == 200
            assert list_deleted.json() == []

        evidence = (
            {"step": "create", "status_code": 201, "json": create.json()},
            {
                "step": "read_created",
                "status_code": 200,
                "json": read_created.json(),
            },
            {
                "step": "list_created",
                "status_code": 200,
                "json": list_created.json(),
            },
            {"step": "update", "status_code": 200, "json": update.json()},
            {"step": "delete", "status_code": 200, "json": delete.json()},
            {
                "step": "list_deleted",
                "status_code": 200,
                "json": list_deleted.json(),
            },
        )
        assert evidence == EXPECTED_WIDGET_CRUD_EVIDENCE
        return evidence


def assert_widget_rest_crud_over_http(
    app: Any,
    server_kind: ServerKind,
) -> WidgetCrudEvidence:
    """Start one framework app and run the shared Widget CRUD proof."""

    server = start_http_server(app, server_kind)
    try:
        return WidgetCrudClientAssertions().run(server.base_url)
    finally:
        server.stop()


def assert_table_class_surface_over_http(
    app: Any,
    server_kind: ServerKind,
    surface: Mapping[str, Any],
) -> tuple[dict[str, Any], ...]:
    """Start one app and assert the table class route surface over HTTP.

    This proof is intentionally narrower than Widget CRUD behavior. Some Tigrbl
    table classes represent streams, SSE, WebSocket, or WebTransport lanes, so
    their first comparable behavior is the HTTP route surface projected by the
    table class.
    """

    import httpx

    server = start_http_server(app, server_kind)
    try:
        with httpx.Client(base_url=server.base_url, timeout=10.0) as client:
            response = client.get("/openapi.json")
            assert response.status_code == 200
            observed = _select_route_surface(response.json(), surface["routes"])
        expected = _expected_route_surface(surface)
        assert observed == expected
        return observed
    finally:
        server.stop()


def _expected_route_surface(surface: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(
        {"path": path, "methods": tuple(methods)}
        for path, methods in surface["routes"]
    )


def _select_route_surface(
    openapi_payload: Mapping[str, Any],
    expected_routes: RouteSurface,
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
        uvicorn.Config(
            app,
            host="127.0.0.1",
            port=port,
            lifespan="off",
            log_level="warning",
        )
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
        except (
            httpx.ConnectError,
            httpx.ReadError,
            httpx.ConnectTimeout,
            httpx.ReadTimeout,
        ):
            time.sleep(0.05)
    raise RuntimeError(f"server did not start at {base_url}")


def _free_http_port() -> int:
    """Ask the OS for an available localhost TCP port for a demo server."""

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])
