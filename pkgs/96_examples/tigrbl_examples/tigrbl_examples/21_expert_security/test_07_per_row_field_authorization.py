"""Project fields per row for authenticated REST and JSON-RPC reads."""

from __future__ import annotations

from dataclasses import replace

import httpx
import pytest

from tigrbl import Column, Request, RestJsonRpcTable, TigrblApp, hook_ctx
from tigrbl.factories.engine import engine, mem
from tigrbl.runtime.status import HTTPException
from tigrbl.types import Integer, Mapped, String


async def authenticate(request: Request) -> str:
    # This fixture uses one fixed credential for the example's requester.
    if request.headers.get("authorization") != "Bearer example-alice-token":
        raise HTTPException(status_code=401, detail="Authentication required")
    request.state.account_id = "alice"
    return request.state.account_id


def can_view_cost_basis(account_id: str, asset: Asset) -> bool:
    return account_id == asset.owner_id


class Asset(RestJsonRpcTable):
    __tablename__ = "lesson_field_authorization_assets"
    TABLE_PROFILE = replace(
        RestJsonRpcTable.TABLE_PROFILE,
        ops=tuple(
            op
            for op in RestJsonRpcTable.TABLE_PROFILE.ops
            if op.alias in {"read", "list"}
        ),
    )

    id: Mapped[str] = Column.make(
        storage=Column.S(type_=String, primary_key=True),
        io=Column.IO(out_verbs=("read", "list")),
    )
    name: Mapped[str] = Column.make(
        storage=Column.S(type_=String, nullable=False),
        io=Column.IO(out_verbs=("read", "list")),
    )
    # An explicit input-only IO spec keeps these out of the generated read schemas.
    # The profile for this example exposes only read and list.
    owner_id: Mapped[str] = Column.make(
        storage=Column.S(type_=String, nullable=False),
        io=Column.IO(in_verbs=("create",)),
    )
    cost_basis: Mapped[int | None] = Column.make(
        storage=Column.S(type_=Integer, nullable=True),
        io=Column.IO(in_verbs=("create",)),
    )

    @hook_ctx(ops=("read", "list"), phase="POST_HANDLER")
    async def project_visible_fields(cls, ctx):
        account_id = ctx["request"].state.account_id

        def project(asset: Asset) -> dict[str, str | int | None]:
            visible: dict[str, str | int | None] = {"id": asset.id, "name": asset.name}
            if can_view_cost_basis(account_id, asset):
                visible["cost_basis"] = asset.cost_basis
            return visible

        result = ctx["result"]
        ctx["result"] = (
            [project(asset) for asset in result]
            if isinstance(result, list)
            else project(result)
        )


@pytest.mark.asyncio
@pytest.mark.parametrize("protocol", ["rest", "jsonrpc"])
async def test_per_row_field_authorization(protocol, monkeypatch):
    database = engine(mem(async_=False))
    app = TigrblApp(engine=database)
    app.set_auth(authn=authenticate)
    app.include_table(Asset)
    assert set(Asset.ops.by_alias) == {"read", "list"}
    await app.initialize()
    app.mount_jsonrpc(prefix="/rpc")

    # Seed the database directly so the example can focus on the read policy.
    async with database.asession() as session:
        await session.executemany(
            Asset.__table__.insert(),
            [
                {
                    "id": "a",
                    "name": "Alice's asset",
                    "owner_id": "alice",
                    "cost_basis": None,
                },
                {
                    "id": "b",
                    "name": "Bob's asset",
                    "owner_id": "bob",
                    "cost_basis": 34567,
                },
            ],
        )
        await session.commit()

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
        headers={"Authorization": "Bearer example-alice-token"},
    ) as client:

        async def request(alias, **params):
            if protocol == "rest":
                path = f"/asset/{params['id']}" if alias == "read" else "/asset"
                return await client.get(path)
            return await client.post(
                "/rpc",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": f"Asset.{alias}",
                    "params": params,
                },
            )

        def result(response):
            assert response.status_code == 200, response.text
            payload = response.json()
            return payload["result"] if protocol == "jsonrpc" else payload

        alice = {"id": "a", "name": "Alice's asset", "cost_basis": None}
        bob = {"id": "b", "name": "Bob's asset"}
        assert result(await request("read", id="a")) == alice
        assert result(await request("read", id="b")) == bob
        assert {row["id"]: row for row in result(await request("list"))} == {
            "a": alice,
            "b": bob,
        }

        def unavailable_policy(account_id: str, asset: Asset) -> bool:
            if asset.owner_id == account_id:
                return True
            raise HTTPException(status_code=503, detail="Field policy unavailable")

        monkeypatch.setitem(globals(), "can_view_cost_basis", unavailable_policy)
        response = await request("list")
        if protocol == "jsonrpc":
            assert response.status_code == 200
            assert "error" in response.json()
            assert "result" not in response.json()
        else:
            assert response.status_code == 503
        assert "Field policy unavailable" in response.text
        assert "cost_basis" not in response.text
        assert "34567" not in response.text
        assert "asset" not in response.text
