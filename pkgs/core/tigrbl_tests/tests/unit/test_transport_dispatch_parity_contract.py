from __future__ import annotations

from tigrbl import TigrblApp
from tigrbl.orm.mixins import BulkCapable, GUIDPk, Mergeable
from tigrbl.orm.tables import TableBase
from tigrbl.types import Column, String


def _route_aliases(router: object) -> set[str]:
    aliases: set[str] = set()
    for route in getattr(router, "routes", []):
        name = getattr(route, "name", "")
        if "." in name:
            aliases.add(name.split(".", 1)[1])
    return aliases


def test_rest_and_jsonrpc_semantic_parity_survives_binding_materialization() -> None:
    TableBase.metadata.clear()

    class Item(TableBase, GUIDPk, BulkCapable, Mergeable):
        __tablename__ = "transport_dispatch_parity_items"
        name = Column(String, nullable=False)

    ops = (
        "read",
        "update",
        "replace",
        "delete",
        "list",
        "merge",
        "bulk_create",
        "bulk_update",
        "bulk_replace",
        "bulk_merge",
        "bulk_delete",
    )
    Item.__tigrbl_ops__ = {verb: {"target": verb} for verb in ops}

    app = TigrblApp()
    app.include_table(Item, mount_router=False)

    rest_aliases = _route_aliases(Item.rest.router)
    rpc_aliases = {
        name for name in dir(app.rpc.Item) if not name.startswith("_")
    }
    shared = rest_aliases & rpc_aliases

    assert set(ops) <= shared
    assert "clear" not in rest_aliases
    assert "clear" in rpc_aliases
