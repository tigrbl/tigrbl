from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient

from tigrbl import TableBase, TigrblApp
from tigrbl._spec import HttpJsonRpcBindingSpec, HttpRestBindingSpec, OpSpec
from tigrbl.factories.engine import mem
from tigrbl.types import Column, String


def _make_widget_model() -> type[TableBase]:
    attrs = {
        "__module__": __name__,
        "__tablename__": "transport_dispatch_parity_widgets",
        "__allow_unmapped__": True,
        "id": Column(String, primary_key=True),
        "name": Column(String, nullable=False),
        "__tigrbl_ops__": (
            OpSpec(
                alias="widgets.create",
                target="create",
                bindings=(
                    HttpRestBindingSpec(
                        proto="http.rest",
                        methods=("POST",),
                        path="/widgets",
                    ),
                    HttpJsonRpcBindingSpec(
                        proto="http.jsonrpc",
                        rpc_method="widgets.create",
                    ),
                ),
            ),
            OpSpec(
                alias="widgets.read",
                target="read",
                bindings=(
                    HttpRestBindingSpec(
                        proto="http.rest",
                        methods=("GET",),
                        path="/widgets/{item_id}",
                    ),
                    HttpJsonRpcBindingSpec(
                        proto="http.jsonrpc",
                        rpc_method="widgets.read",
                    ),
                ),
            ),
            OpSpec(
                alias="widgets.list",
                target="list",
                bindings=(
                    HttpRestBindingSpec(
                        proto="http.rest",
                        methods=("GET",),
                        path="/widgets",
                    ),
                    HttpJsonRpcBindingSpec(
                        proto="http.jsonrpc",
                        rpc_method="widgets.list",
                    ),
                ),
            ),
        ),
    }
    return type("DispatchParityWidget", (TableBase,), attrs)


async def _jsonrpc(
    client: AsyncClient,
    method: str,
    params: Mapping[str, Any] | None = None,
) -> Any:
    response = await client.post(
        "/rpc",
        json={"jsonrpc": "2.0", "method": method, "params": dict(params or {}), "id": 1},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "error" not in payload, payload
    return payload["result"]


@pytest.mark.asyncio
async def test_rest_and_jsonrpc_semantic_parity_survives_binding_materialization() -> None:
    app = TigrblApp(engine=mem(async_=False), mount_system=False)
    app.include_table(_make_widget_model())
    initialized = app.initialize()
    if hasattr(initialized, "__await__"):
        await initialized

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        rest_create = await client.post("/widgets", json={"id": "rest-1", "name": "Ada"})
        assert rest_create.status_code == 201

        rpc_read_rest_row = await _jsonrpc(client, "widgets.read", {"id": "rest-1"})
        assert rpc_read_rest_row["id"] == "rest-1"
        assert rpc_read_rest_row["name"] == "Ada"

        rpc_create = await _jsonrpc(
            client,
            "widgets.create",
            {"id": "rpc-1", "name": "Grace"},
        )
        assert rpc_create["id"] == "rpc-1"

        rest_read_rpc_row = await client.get("/widgets/rpc-1")
        assert rest_read_rpc_row.status_code == 200
        assert rest_read_rpc_row.json()["name"] == "Grace"

        rest_list = (await client.get("/widgets")).json()
        rpc_list = await _jsonrpc(client, "widgets.list")
        assert {row["id"] for row in rest_list} == {"rest-1", "rpc-1"}
        assert rpc_list == rest_list
