"""HTTP pedagogy for certifying framework equivalence.

The framework implementation files show how a Tigrbl, FastAPI, or Flask app is
authored and started.  This file shows the one client-side lesson that every
implementation must satisfy:

1. start a real local HTTP server;
2. call that server with ``httpx``;
3. assert the exact Widget CRUD responses that developers should expect.

Keeping the client assertions here is intentional.  If three frameworks claim
the same REST CRUD behavior, they should be exercised by the same client code.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import socket
import time

WidgetCrudEvidence = tuple[dict, ...]

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


@dataclass(frozen=True)
class RunningHttpServer:
    """A tiny handle for the real server created by a framework example.

    The framework modules own their app construction and server startup.  The
    shared client assertion only needs the base URL and a way to stop the server
    after the HTTP proof has finished.
    """

    base_url: str
    stop: Callable[[], None]


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
    server: RunningHttpServer,
) -> WidgetCrudEvidence:
    """Run the shared Widget CRUD proof against one started framework server."""

    try:
        return WidgetCrudClientAssertions().run(server.base_url)
    finally:
        server.stop()


def wait_for_http_server(base_url: str) -> None:
    """Block until a just-started local server accepts HTTP requests."""

    import httpx

    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        try:
            httpx.get(base_url, timeout=0.5)
            return
        except (httpx.ConnectError, httpx.ReadError, httpx.ConnectTimeout):
            time.sleep(0.05)
    raise RuntimeError(f"server did not start at {base_url}")


def free_http_port() -> int:
    """Ask the OS for an available localhost TCP port for a demo server."""

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])
