from __future__ import annotations

import inspect

import httpx
import pytest

from tests.harness_v3._support import running_server
from tigrbl import TableBase, TigrblApp
from tigrbl.factories.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String
from tigrbl_core._spec.alias_spec import AliasSpec
from tigrbl_core._spec.app_spec import AppSpec, normalize_app_spec
from tigrbl_core._spec.binding_spec import (
    BindingRegistrySpec,
    BindingSpec,
    HttpJsonRpcBindingSpec,
    HttpRestBindingSpec,
    HttpStreamBindingSpec,
    compile_binding_event_key,
    project_binding_runtime_metadata,
)
from tigrbl_core._spec.engine_spec import EngineProviderSpec, EngineSpec
from tigrbl_core._spec.router_spec import RouterSpec


class _AliasContract(AliasSpec):
    @property
    def alias(self) -> str:
        return "publish_now"

    @property
    def request_schema(self):
        return None

    @property
    def response_schema(self):
        return None

    @property
    def persist(self):
        return "default"

    @property
    def arity(self):
        return "collection"

    @property
    def rest(self):
        return True


def test_http_binding_specs_project_canonical_transport_metadata() -> None:
    rest = HttpRestBindingSpec(
        proto="http.rest",
        methods=("GET", "POST"),
        path="/widgets",
    )
    rpc = HttpJsonRpcBindingSpec(
        proto="http.jsonrpc",
        rpc_method="Widget.create",
    )
    stream = HttpStreamBindingSpec(proto="http.stream", path="/widgets/tail")

    rest_meta = project_binding_runtime_metadata(rest)
    rpc_meta = project_binding_runtime_metadata(rpc)
    stream_meta = project_binding_runtime_metadata(stream)

    assert rest.methods == ("GET", "POST")
    assert rest.exchange == "request_response"
    assert rest_meta["family"] == "request_response"
    assert rest_meta["subevents"] == ("request.received", "response.sent")

    assert rpc.endpoint == "default"
    assert rpc.exchange == "request_response"
    assert rpc.framing == "jsonrpc"
    assert rpc_meta["family"] == "rpc"
    assert rpc_meta["subevents"] == ("rpc.request", "rpc.response")

    assert stream.methods == ("GET",)
    assert stream.exchange == "server_stream"
    assert stream.framing == "stream"
    assert stream_meta["family"] == "stream"
    assert stream_meta["subevents"] == (
        "stream.open",
        "stream.message",
        "stream.close",
    )


def test_binding_spec_registry_and_event_keys_round_trip() -> None:
    rest_binding = BindingSpec(
        name="widget.list",
        spec=HttpRestBindingSpec(proto="http.rest", methods=("GET",), path="/widgets"),
    )
    rpc_binding = BindingSpec(
        name="widget.create.rpc",
        spec=HttpJsonRpcBindingSpec(
            proto="http.jsonrpc",
            rpc_method="Widget.create",
        ),
    )
    registry = BindingRegistrySpec()

    registry.register(rest_binding)
    registry.register(rpc_binding)

    restored_registry = BindingRegistrySpec.from_json(registry.to_json())
    restored_rpc = BindingSpec.from_json(rpc_binding.to_json())

    assert set(restored_registry.values()) == {rest_binding, rpc_binding}
    assert restored_registry.get("widget.list") == rest_binding
    assert isinstance(restored_rpc.spec, HttpJsonRpcBindingSpec)
    assert compile_binding_event_key(rest_binding.spec).family_code == 10
    assert compile_binding_event_key(rpc_binding.spec).family_code == 11


def test_bindings_integration_rejects_exchange_family_mismatches() -> None:
    with pytest.raises(ValueError, match="invalid exchange"):
        project_binding_runtime_metadata(
            HttpStreamBindingSpec(
                proto="http.stream",
                path="/bad",
                exchange="request_response",
            )
        )


def test_appspec_normalization_and_imperative_materialization_preserve_plan() -> None:
    class Widget(TableBase, GUIDPk):
        __tablename__ = "spec_binding_contract_widget"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    class HarnessApp(TigrblApp):
        TITLE = "Spec Binding Harness"
        VERSION = "1.2.3"
        ENGINE = mem(async_=False)
        TABLES = (Widget,)
        JSONRPC_PREFIX = "/rpc-spec-binding"
        SYSTEM_PREFIX = "/system-spec-binding"

    collected = AppSpec.collect(HarnessApp)
    router_gen = (router for router in (RouterSpec(name="contract"),))
    normalized = normalize_app_spec(
        AppSpec(
            title="",
            version="",
            routers=router_gen,
            tables=collected.tables,
            engine=collected.engine,
            jsonrpc_prefix="",
            system_prefix="",
        )
    )
    materialized = TigrblApp.from_spec(
        AppSpec(
            title=collected.title,
            version=collected.version,
            tables=collected.tables,
            engine=collected.engine,
            jsonrpc_prefix=collected.jsonrpc_prefix,
            system_prefix=collected.system_prefix,
        )
    )

    assert collected.title == "Spec Binding Harness"
    assert collected.version == "1.2.3"
    assert collected.tables == (Widget,)
    assert normalized.title == "Tigrbl"
    assert normalized.version == "0.1.0"
    assert normalized.jsonrpc_prefix == "/rpc"
    assert normalized.system_prefix == "/system"
    assert normalized.routers == (RouterSpec(name="contract"),)
    assert materialized.title == "Spec Binding Harness"
    assert materialized.version == "1.2.3"
    assert materialized.jsonrpc_prefix == "/rpc-spec-binding"
    assert materialized.system_prefix == "/system-spec-binding"


def test_appspec_nested_router_entries_validate_fail_closed() -> None:
    with pytest.raises(TypeError, match="RouterSpec.tables entries"):
        RouterSpec(name="widgets", tables=("not-a-table-spec",))

    with pytest.raises(TypeError, match="RouterSpec.ops entries"):
        RouterSpec(name="widgets", ops=("not-an-op-spec",))


@pytest.mark.asyncio
async def test_appspec_uvicorn_e2e_rest_rpc_parity() -> None:
    class Widget(TableBase, GUIDPk):
        __tablename__ = "spec_binding_uvicorn_widget"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    class HarnessApp(TigrblApp):
        ENGINE = mem(async_=False)
        TABLES = (Widget,)
        JSONRPC_PREFIX = "/rpc-spec-binding-e2e"
        SYSTEM_PREFIX = "/system-spec-binding-e2e"

    app = HarnessApp()
    initialized = app.initialize()
    if inspect.isawaitable(initialized):
        await initialized

    async with running_server(app) as base_url:
        async with httpx.AsyncClient(base_url=base_url, timeout=5.0) as client:
            health = await client.get("/system-spec-binding-e2e/healthz")
            assert health.status_code == 200
            assert health.json()["ok"] is True

            rest = await client.post("/widget", json={"name": "Alpha"})
            assert rest.status_code == 201
            alpha = rest.json()

            rpc = await client.post(
                "/rpc-spec-binding-e2e",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "Widget.create",
                    "params": {"name": "Beta"},
                },
            )
            assert rpc.status_code == 200
            beta = rpc.json()["result"]

            listed = await client.get("/widget")
            assert listed.status_code == 200
            names = {row["name"] for row in listed.json()}
            assert {alpha["name"], beta["name"]} <= names


def test_aliasspec_engine_and_provider_contracts_are_public_and_normalized() -> None:
    with pytest.raises(TypeError):
        AliasSpec()

    alias = _AliasContract()
    sqlite = EngineSpec.from_any("sqlite://:memory:")
    provider = EngineProviderSpec.from_any(sqlite)
    postgres = EngineSpec.from_any(
        {
            "engine": "postgres",
            "async": True,
            "password": "secret",
            "db": "app",
            "max_size": "7",
        }
    )

    assert alias.alias == "publish_now"
    assert alias.persist == "default"
    assert alias.arity == "collection"
    assert alias.rest is True

    assert sqlite is not None
    assert sqlite.kind == "sqlite"
    assert sqlite.memory is True
    assert provider is not None
    assert provider.spec is sqlite
    assert postgres is not None
    assert postgres.kind == "postgres"
    assert postgres.async_ is True
    assert postgres.name == "app"
    assert postgres.max == 7
    assert "secret" not in repr(postgres)
