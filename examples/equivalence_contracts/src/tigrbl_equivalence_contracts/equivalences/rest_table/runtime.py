"""Runtime proof for the Widget REST CRUD equivalence."""

from __future__ import annotations

from typing import Any

from tigrbl_equivalence_contracts.runtime import ServerKind, start_http_server

WidgetCrudEvidence = tuple[dict, ...]

EXPECTED_WIDGET_CRUD_EVIDENCE: WidgetCrudEvidence = (
    {"step": "create", "status_code": 201, "json": {"id": "widget-1", "name": "First"}},
    {"step": "read_created", "status_code": 200, "json": {"id": "widget-1", "name": "First"}},
    {"step": "list_created", "status_code": 200, "json": [{"id": "widget-1", "name": "First"}]},
    {"step": "update", "status_code": 200, "json": {"id": "widget-1", "name": "Second"}},
    {"step": "delete", "status_code": 200, "json": {"deleted": 1}},
    {"step": "list_deleted", "status_code": 200, "json": []},
)


class WidgetCrudClientAssertions:
    """The single client-side proof for Widget REST CRUD parity."""

    def run(self, base_url: str) -> WidgetCrudEvidence:
        """Call the server with httpx and assert the expected CRUD outputs."""

        import httpx

        with httpx.Client(base_url=base_url, timeout=10.0) as client:
            client.delete("/widget/widget-1")
            create = client.post("/widget", json={"id": "widget-1", "name": "First"})
            assert create.status_code == 201
            assert create.json() == {"id": "widget-1", "name": "First"}
            read_created = client.get("/widget/widget-1")
            assert read_created.status_code == 200
            assert read_created.json() == {"id": "widget-1", "name": "First"}
            list_created = client.get("/widget")
            assert list_created.status_code == 200
            assert list_created.json() == [{"id": "widget-1", "name": "First"}]
            update = client.patch("/widget/widget-1", json={"id": "widget-1", "name": "Second"})
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
            {"step": "read_created", "status_code": 200, "json": read_created.json()},
            {"step": "list_created", "status_code": 200, "json": list_created.json()},
            {"step": "update", "status_code": 200, "json": update.json()},
            {"step": "delete", "status_code": 200, "json": delete.json()},
            {"step": "list_deleted", "status_code": 200, "json": list_deleted.json()},
        )
        assert evidence == EXPECTED_WIDGET_CRUD_EVIDENCE
        return evidence


def assert_equivalence(app: Any, server_kind: ServerKind) -> WidgetCrudEvidence:
    """Start one vendor app and run the shared Widget CRUD proof."""

    server = start_http_server(app, server_kind)
    try:
        return WidgetCrudClientAssertions().run(server.base_url)
    finally:
        server.stop()
