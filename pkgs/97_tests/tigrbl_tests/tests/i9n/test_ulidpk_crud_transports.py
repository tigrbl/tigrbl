"""Exercise ULID-backed built-in operations over REST and JSON-RPC on HTTP and WebSocket."""

import json
import re
import sys
from contextlib import asynccontextmanager
from dataclasses import replace

import pytest
from httpx import ASGITransport, AsyncClient

from tigrbl import (
    JsonRpcBulkCrudTable,
    RestBulkCrudTable,
    RestJsonRpcOltpTable,
    RestJsonRpcTable,
    TigrblApp,
)
from tigrbl._spec import F, IO, S
from tigrbl.factories.column import acol
from tigrbl.factories.engine import mem
from tigrbl.orm.mixins import ULIDPk
from tigrbl.orm.tables import TableBase
from tigrbl.types import String
from tigrbl_core._spec import (
    AppSpec,
    EngineSpec,
    HttpJsonRpcBindingSpec,
    HttpRestBindingSpec,
    JsonRpcFramingSpec,
    OpSpec,
    PathSpec,
    RouterSpec,
    TableSpec,
    WsBindingSpec,
)


ULID = re.compile(r"[0-7][0-9A-HJKMNP-TV-Z]{25}")
MISSING_ULID = "01ARZ3NDEKTSV4RRFFQ69G5FAV"
WRITE_VERBS = (
    "create",
    "update",
    "replace",
    "merge",
    "bulk_create",
    "bulk_update",
    "bulk_replace",
    "bulk_merge",
)


@asynccontextmanager
async def ulid_client(profile, name):
    attrs = {}
    if profile in (RestBulkCrudTable, JsonRpcBulkCrudTable):
        binding = (
            HttpRestBindingSpec(
                proto="http.rest",
                methods=("PATCH",),
                path=f"/{name.lower()}/merge",
            )
            if profile is RestBulkCrudTable
            else HttpJsonRpcBindingSpec(
                proto="http.jsonrpc", rpc_method=f"{name}.bulk_merge"
            )
        )
        attrs["TABLE_PROFILE"] = replace(
            profile.TABLE_PROFILE,
            ops=(
                *profile.TABLE_PROFILE.ops,
                OpSpec(
                    alias="bulk_merge",
                    target="bulk_merge",
                    arity="collection",
                    bindings=(binding,),
                ),
            ),
        )
    model = type(
        name,
        (profile, ULIDPk),
        {
            **attrs,
            "__module__": __name__,
            "__tablename__": name.lower(),
            "name": acol(
                storage=S(type_=String, nullable=False),
                field=F(py_type=str),
                io=IO(
                    in_verbs=WRITE_VERBS,
                    mutable_verbs=WRITE_VERBS,
                    out_verbs=("read", "list"),
                    filter_ops=("eq",),
                ),
            ),
        },
    )
    app = TigrblApp(engine=mem(async_=True))
    app.include_table(model)
    app.mount_jsonrpc()
    await app.initialize()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


async def rpc(client, model, verb, params):
    response = await client.post(
        "/rpc",
        json={"jsonrpc": "2.0", "method": f"{model}.{verb}", "params": params, "id": 1},
    )
    assert response.status_code == 200, response.text
    return response.json()


async def rpc_result(client, model, verb, params):
    envelope = await rpc(client, model, verb, params)
    assert "error" not in envelope, envelope
    assert envelope["id"] == 1
    return envelope["result"]


async def rest(client, method, path, body=None):
    response = await client.request(method, path, json=body)
    assert response.is_success, response.text
    return response.json() if response.content else None


@pytest.mark.asyncio
@pytest.mark.parametrize("via_rpc", [False, True], ids=["rest", "jsonrpc"])
async def test_ulidpk_builtin_crud(via_rpc):
    model = "UlidRpcWidget" if via_rpc else "UlidRestWidget"
    path = f"/{model.lower()}"

    async with ulid_client(RestJsonRpcTable, model) as client:

        async def call(verb, method, *, ident=None, body=None):
            if via_rpc:
                params = dict(body or {})
                if ident is not None:
                    params["id"] = ident
                return await rpc_result(client, model, verb, params)
            return await rest(
                client, method, f"{path}/{ident}" if ident else path, body
            )

        first = await call("create", "POST", body={"name": "first"})
        second = await call("create", "POST", body={"name": "second"})
        ident = first["id"]
        assert ULID.fullmatch(ident)
        assert ULID.fullmatch(second["id"])
        assert ident != second["id"]
        assert await call("read", "GET", ident=ident) == first
        assert await rpc_result(client, model, "read", {"id": ident}) == first
        assert await rest(client, "GET", f"{path}/{ident}") == first

        updated = await call("update", "PATCH", ident=ident, body={"name": "updated"})
        assert updated == {"id": ident, "name": "updated"}
        replaced = await call("replace", "PUT", ident=ident, body={"name": "replaced"})
        assert replaced == {"id": ident, "name": "replaced"}
        listed = {row["id"]: row["name"] for row in await call("list", "GET")}
        assert set(listed) == {ident, second["id"]}
        assert listed[second["id"]] == "second"

        await call("delete", "DELETE", ident=ident)
        missing = await client.get(f"{path}/{ident}")
        assert missing.status_code == 404, missing.text
        keeper = await call("create", "POST", body={"name": "keep"})
        rejected = {"filters": {"unknown_field": "second"}}
        if via_rpc:
            envelope = await rpc(client, model, "clear", rejected)
            assert envelope["error"]["code"] == -32602
        else:
            response = await client.request("DELETE", path, json=rejected)
            assert response.status_code == 422
        assert {row["id"] for row in await call("list", "GET")} == {
            second["id"],
            keeper["id"],
        }
        assert await call("clear", "DELETE", body={"filters": {"name": "second"}}) == {
            "deleted": 1,
        }
        assert await call("list", "GET") == [keeper]


@pytest.mark.asyncio
@pytest.mark.parametrize("via_rpc", [False, True], ids=["rest", "jsonrpc"])
async def test_ulidpk_oltp_operations(via_rpc):
    model = "UlidRpcOltp" if via_rpc else "UlidRestOltp"
    path = f"/{model.lower()}"
    async with ulid_client(RestJsonRpcOltpTable, model) as client:
        row = await rest(client, "POST", path, {"name": "first"})
        ident = row["id"]
        assert ULID.fullmatch(ident)
        if via_rpc:
            assert await rpc_result(client, model, "count", {}) == {"count": 1}
            assert await rpc_result(client, model, "exists", {"id": ident}) == {
                "exists": True
            }
            assert await rpc_result(client, model, "exists", {"id": MISSING_ULID}) == {
                "exists": False
            }
            merged = await rpc_result(
                client, model, "merge", {"id": ident, "name": "merged"}
            )
        else:
            assert await rest(client, "GET", path) == {"count": 1}
            assert await rest(client, "GET", f"{path}/{ident}") == {"exists": True}
            assert await rest(client, "GET", f"{path}/{MISSING_ULID}") == {
                "exists": False
            }
            merged = await rest(client, "PATCH", f"{path}/{ident}", {"name": "merged"})
        assert merged == {"id": ident, "name": "merged"}


@pytest.mark.asyncio
@pytest.mark.parametrize("via_rpc", [False, True], ids=["rest", "jsonrpc"])
async def test_ulidpk_bulk_crud(via_rpc):
    profile = JsonRpcBulkCrudTable if via_rpc else RestBulkCrudTable
    model = "UlidRpcBulk" if via_rpc else "UlidRestBulk"
    path = f"/{model.lower()}"
    async with ulid_client(profile, model) as client:

        async def call(verb, method, body):
            if via_rpc:
                return await rpc_result(client, model, verb, body)
            route = f"{path}/merge" if verb == "bulk_merge" else path
            return await rest(client, method, route, body)

        created = await call(
            "bulk_create", "POST", [{"name": "first"}, {"name": "second"}]
        )
        ids = {row["name"]: row["id"] for row in created}
        assert set(ids) == {"first", "second"}
        assert len(set(ids.values())) == 2
        assert all(ULID.fullmatch(ident) for ident in ids.values())

        async def read(name):
            ident = ids[name]
            if via_rpc:
                return await rpc_result(client, model, "read", {"id": ident})
            return await rest(client, "GET", f"{path}/{ident}")

        for verb, method, name in (
            ("bulk_update", "PATCH", "updated"),
            ("bulk_replace", "PUT", "replaced"),
            ("bulk_merge", "PATCH", "merged"),
        ):
            await call(verb, method, [{"id": ids["first"], "name": name}])
            first = await read("first")
            assert first == {"id": ids["first"], "name": name}
            assert await read("second") == {
                "id": ids["second"],
                "name": "second",
            }

        await call("bulk_delete", "DELETE", [ids["first"]])
        remaining = (
            await rpc_result(client, model, "list", {})
            if via_rpc
            else await rest(client, "GET", path)
        )
        assert remaining == [{"id": ids["second"], "name": "second"}]


async def websocket_rpc(model_name, monkeypatch):
    model = type(
        model_name,
        (TableBase, ULIDPk),
        {
            "__module__": __name__,
            "__tablename__": model_name.lower(),
            "name": acol(
                storage=S(type_=String, nullable=False),
                field=F(py_type=str),
                io=IO(
                    in_verbs=WRITE_VERBS, out_verbs=("read", "list"), filter_ops=("eq",)
                ),
            ),
        },
    )
    monkeypatch.setattr(sys.modules[__name__], model_name, model, raising=False)
    path = "/ws/ulid"
    binding = WsBindingSpec(proto="ws", path=path, framing=JsonRpcFramingSpec())
    table = TableSpec(
        name=model_name,
        model_ref=f"{__name__}:{model_name}",
        ops=tuple(
            OpSpec(alias=verb, target=verb, arity=arity, bindings=(binding,))
            for verb, arity in (
                ("create", "collection"),
                ("read", "member"),
                ("update", "member"),
                ("delete", "member"),
                ("replace", "member"),
                ("merge", "member"),
                ("list", "collection"),
                ("clear", "collection"),
                ("count", "collection"),
                ("exists", "member"),
                ("bulk_create", "collection"),
                ("bulk_update", "collection"),
                ("bulk_replace", "collection"),
                ("bulk_merge", "collection"),
                ("bulk_delete", "collection"),
            )
        ),
    )
    app = TigrblApp.from_spec(
        AppSpec(
            engines=(EngineSpec(name="primary", kind="sqlite", memory=True),),
            engine_name="primary",
            routers=(
                RouterSpec(
                    name="ulid_socket",
                    paths=(PathSpec(path=path, kind="ws-jsonrpc", tables=(table,)),),
                ),
            ),
        )
    )
    await app.initialize()

    async def call(verb, params):
        incoming = iter(
            [
                {"type": "websocket.connect"},
                {
                    "type": "websocket.receive",
                    "text": json.dumps(
                        {
                            "jsonrpc": "2.0",
                            "method": f"{model_name}.{verb}",
                            "params": params,
                            "id": 1,
                        }
                    ),
                },
                {"type": "websocket.disconnect", "code": 1000},
            ]
        )
        sent = []

        async def receive():
            return next(incoming)

        async def send(message):
            sent.append(message)

        await app(
            {
                "type": "websocket",
                "scheme": "ws",
                "path": path,
                "query_string": b"",
                "headers": [],
                "subprotocols": ["jsonrpc"],
            },
            receive,
            send,
        )
        assert sent[0] == {"type": "websocket.accept", "subprotocol": "jsonrpc"}
        envelope = json.loads(sent[1]["text"])
        assert envelope["id"] == 1
        return envelope

    return call


@pytest.mark.asyncio
async def test_ulidpk_websocket_jsonrpc(monkeypatch):
    call = await websocket_rpc("UlidSocketWidget", monkeypatch)
    created = await call("create", {"name": "socket"})
    assert "result" in created, created
    ident = created["result"]["id"]
    assert ULID.fullmatch(ident)
    assert (await call("read", {"id": ident}))["result"] == {
        "id": ident,
        "name": "socket",
    }
    assert (await call("update", {"id": ident, "name": "changed"}))["result"] == {
        "id": ident,
        "name": "changed",
    }
    assert (await call("replace", {"id": ident, "name": "replaced"}))["result"] == {
        "id": ident,
        "name": "replaced",
    }
    assert (await call("merge", {"id": ident, "name": "merged"}))["result"] == {
        "id": ident,
        "name": "merged",
    }
    assert (await call("exists", {"id": ident}))["result"] == {"exists": True}
    assert (await call("count", {}))["result"] == {"count": 1}
    assert [row["id"] for row in (await call("list", {}))["result"]] == [ident]
    assert (await call("delete", {"id": ident}))["result"] == {"deleted": 1}
    assert "error" in await call("read", {"id": ident})

    created = await call("bulk_create", [{"name": "first"}, {"name": "second"}])
    assert "result" in created, created
    ids = {row["name"]: row["id"] for row in created["result"]}
    assert len(set(ids.values())) == 2
    assert all(ULID.fullmatch(value) for value in ids.values())

    for verb, name in (
        ("bulk_update", "updated"),
        ("bulk_replace", "replaced"),
        ("bulk_merge", "merged"),
    ):
        payload = {"id": ids["first"], "name": name}
        result = await call(verb, [payload])
        assert result["result"] == [payload]
        assert (await call("read", {"id": ids["second"]}))["result"] == {
            "id": ids["second"],
            "name": "second",
        }

    assert (await call("bulk_delete", [ids["first"]]))["result"] == {"deleted": 1}
    assert (await call("clear", {"filters": {"name": "second"}}))["result"] == {
        "deleted": 1,
    }
    assert (await call("list", {}))["result"] == []


@pytest.mark.asyncio
@pytest.mark.parametrize("verb,method", [("update", "PATCH"), ("replace", "PUT")])
@pytest.mark.parametrize("via_rpc", [False, True], ids=["rest", "jsonrpc"])
async def test_ulidpk_scalar_mutation_persists(verb, method, via_rpc):
    protocol = "Rpc" if via_rpc else "Rest"
    model = f"Ulid{protocol}{verb.title()}"
    path = f"/{model.lower()}"

    async with ulid_client(RestJsonRpcTable, model) as client:
        row = await rest(client, "POST", path, {"name": "before"})
        ident = row["id"]
        member = f"{path}/{ident}"
        expected = {"id": ident, "name": "after"}

        if via_rpc:
            assert await rpc_result(client, model, verb, expected) == expected
        else:
            assert await rest(client, method, member, {"name": "after"}) == expected

        assert await rest(client, "GET", member) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("via_rpc", [False, True], ids=["rest", "jsonrpc"])
async def test_ulidpk_malformed_id_is_a_client_error(via_rpc):
    model = "UlidRpcInvalid" if via_rpc else "UlidRestInvalid"
    path = f"/{model.lower()}"

    async with ulid_client(RestJsonRpcTable, model) as client:
        if via_rpc:
            missing = await rpc(client, model, "read", {"id": MISSING_ULID})
            assert missing["error"]["code"] == -32003
            invalid = await rpc(client, model, "read", {"id": "invalid-ulid"})
            assert invalid["error"]["code"] == -32602
        else:
            missing = await client.get(f"{path}/{MISSING_ULID}")
            assert missing.status_code == 404
            invalid = await client.get(f"{path}/invalid-ulid")
            assert invalid.status_code in (400, 422)


@pytest.mark.asyncio
@pytest.mark.parametrize("verb", ["bulk_update", "bulk_replace", "bulk_merge"])
async def test_ulidpk_websocket_bulk_mutation_persists(verb, monkeypatch):
    call = await websocket_rpc(
        "UlidSocket" + verb.title().replace("_", ""), monkeypatch
    )
    row = (await call("create", {"name": "before"}))["result"]
    expected = {"id": row["id"], "name": "after"}
    assert (await call(verb, [expected]))["result"] == [expected]
    assert (await call("read", {"id": row["id"]}))["result"] == expected
