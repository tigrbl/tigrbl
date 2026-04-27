from __future__ import annotations

import httpx
import pytest
from sqlalchemy import Column, String

from tigrbl import TableBase, TigrblApp
from tigrbl._spec import AppSpec, HttpJsonRpcBindingSpec, HttpRestBindingSpec, OpSpec
from tigrbl.factories.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl_tests.tests.harness_v3._support import pick_unique_port, start_uvicorn, stop_uvicorn
from tigrbl_tests.tests.fixtures.appspec_corpus_loader import load_corpus, validate_corpus


def _make_widget_model(*, tablename: str, resource: str, include_jsonrpc: bool) -> type:
    class Widget(TableBase, GUIDPk):
        __tablename__ = tablename
        __resource__ = resource
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

    bindings: list[object] = [
        HttpRestBindingSpec(proto="http.rest", path=f"/{resource}", methods=("POST",))
    ]
    if include_jsonrpc:
        bindings.append(
            HttpJsonRpcBindingSpec(proto="http.jsonrpc", rpc_method="Widget.create")
        )
        bindings.append(
            HttpJsonRpcBindingSpec(proto="http.jsonrpc", rpc_method="Widget.list")
        )

    Widget.__tigrbl_ops__ = (
        OpSpec(alias="create", target="create", bindings=tuple(bindings)),
        OpSpec(alias="list", target="list", bindings=tuple(bindings[1:])),
    )
    return Widget


@pytest.mark.acceptance
@pytest.mark.asyncio
async def test_canonical_corpus_rest_rpc_roundtrip() -> None:
    corpus = load_corpus("appspec_corpus.canonical.json")
    validate_corpus(corpus, lane="canonical")

    for case in corpus["cases"]:
        widget = _make_widget_model(
            tablename=case["table"]["tablename"],
            resource=case["table"]["resource"],
            include_jsonrpc=True,
        )
        spec = AppSpec(
            title=case["app"]["title"],
            version=case["app"]["version"],
            engine=mem(async_=False),
            tables=(widget,),
            jsonrpc_prefix=case["app"]["jsonrpc_prefix"],
            system_prefix=case["app"]["system_prefix"],
        )
        app = TigrblApp.from_spec(spec)
        port = pick_unique_port()
        base_url, server, task = await start_uvicorn(app, port=port)
        try:
            async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
                rest = await client.post(
                    f"/{case['table']['resource']}",
                    json={"name": f"{case['mode']}-rest"},
                )
                rpc_create = await client.post(
                    f"{case['app']['jsonrpc_prefix']}/",
                    json={
                        "jsonrpc": "2.0",
                        "method": "Widget.create",
                        "params": {"name": f"{case['mode']}-rpc"},
                        "id": 1,
                    },
                )
                rpc_list = await client.post(
                    f"{case['app']['jsonrpc_prefix']}/",
                    json={
                        "jsonrpc": "2.0",
                        "method": "Widget.list",
                        "params": {},
                        "id": 2,
                    },
                )

            assert rest.status_code in set(case["expect"]["rest_status"])
            assert rpc_create.status_code in set(case["expect"]["rpc_status"])
            assert rpc_list.status_code in set(case["expect"]["rpc_status"])

            payload = rpc_list.json()
            items = payload.get("result", payload)
            if isinstance(items, dict):
                items = items.get("items", [items])
            assert isinstance(items, list)
            assert any(isinstance(item, dict) and "name" in item for item in items)
        finally:
            await stop_uvicorn(server, task)


@pytest.mark.acceptance
@pytest.mark.asyncio
async def test_negative_corpus_unknown_rpc_method_returns_fail_closed_contract() -> None:
    corpus = load_corpus("appspec_corpus.negative.json")
    validate_corpus(corpus, lane="negative")
    case = next(c for c in corpus["cases"] if c["mode"] == "unknown_rpc_method_404")

    widget = _make_widget_model(
        tablename=case["table"]["tablename"],
        resource=case["table"]["resource"],
        include_jsonrpc=True,
    )
    spec = AppSpec(
        title=case["app"]["title"],
        version=case["app"]["version"],
        engine=mem(async_=False),
        tables=(widget,),
        jsonrpc_prefix=case["app"]["jsonrpc_prefix"],
        system_prefix=case["app"]["system_prefix"],
    )
    app = TigrblApp.from_spec(spec)
    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)
    try:
        async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
            response = await client.post(
                f"{case['app']['jsonrpc_prefix']}/",
                json={
                    "jsonrpc": "2.0",
                    "method": "Widget.unknown",
                    "params": {},
                    "id": 99,
                },
            )
        body = response.json()
        assert response.status_code == case["expect"]["status"]
        assert body.get("detail") == case["expect"]["detail"]
    finally:
        await stop_uvicorn(server, task)


@pytest.mark.acceptance
@pytest.mark.asyncio
async def test_negative_corpus_no_rpc_binding_has_no_rpc_runtime_side_effect() -> None:
    corpus = load_corpus("appspec_corpus.negative.json")
    validate_corpus(corpus, lane="negative")
    case = next(c for c in corpus["cases"] if c["mode"] == "no_rpc_binding_no_mount")

    widget = _make_widget_model(
        tablename=case["table"]["tablename"],
        resource=case["table"]["resource"],
        include_jsonrpc=False,
    )
    spec = AppSpec(
        title=case["app"]["title"],
        version=case["app"]["version"],
        engine=mem(async_=False),
        tables=(widget,),
        jsonrpc_prefix=case["app"]["jsonrpc_prefix"],
        system_prefix=case["app"]["system_prefix"],
    )
    app = TigrblApp.from_spec(spec)
    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)
    try:
        async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
            missing_rpc = await client.post(
                f"{case['app']['jsonrpc_prefix']}/",
                json={
                    "jsonrpc": "2.0",
                    "method": "Widget.create",
                    "params": {"name": "should-not-execute"},
                    "id": 44,
                },
            )
            rest = await client.post(
                f"/{case['table']['resource']}",
                json={"name": "rest-still-works"},
            )

        assert missing_rpc.status_code == 404
        assert missing_rpc.json()["detail"] == "No runtime operation matched request."
        assert rest.status_code in {200, 201}
    finally:
        await stop_uvicorn(server, task)
