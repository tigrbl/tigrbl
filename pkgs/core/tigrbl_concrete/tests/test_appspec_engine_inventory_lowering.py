from __future__ import annotations

import pytest

from tigrbl_core._spec import (
    AppSpec,
    EngineSpec,
    OpSpec,
    PathSpec,
    RouterSpec,
    TableSpec,
)
from tigrbl import TigrblApp
from tigrbl_concrete._concrete import engine_resolver as resolver
from tigrbl_concrete._mapping.appspec import lower_concrete_engine_inputs
from tigrbl_concrete.webhooks import DefineWebhook


def _sqlite(name: str) -> dict[str, object]:
    return {"kind": "sqlite", "memory": True, "name": name}


def _op(
    alias: str, engine: object | None = None, engine_name: str | None = None
) -> OpSpec:
    return OpSpec(
        alias=alias,
        target="custom",
        engine=engine,
        engine_name=engine_name,
    )


@pytest.fixture(autouse=True)
def _reset_resolver() -> None:
    resolver.reset()
    yield
    resolver.reset()


def test_concrete_app_engine_lowers_to_named_inventory_before_runtime_install() -> None:
    spec = AppSpec(engine=_sqlite("primary"))

    app = TigrblApp.from_spec(spec)
    lowered = app._tigrbl_app_spec

    assert lowered.engine is None
    assert lowered.engine_name == "primary"
    assert tuple(engine.name for engine in lowered.engines) == ("primary",)
    assert getattr(app, "engine", None) is None
    assert tuple(engine.name for engine in app._tigrbl_engine_inventory) == ("primary",)
    assert resolver.resolve_provider().spec.name == "primary"
    assert resolver.resolve_provider(engine_name="primary").spec.name == "primary"


def test_concrete_router_table_and_op_engines_lower_to_scope_names() -> None:
    table = TableSpec(
        name="Widget",
        model_ref="tests.widgets:Widget",
        engine=_sqlite("table_store"),
        ops=(
            _op("read", engine=_sqlite("read_store")),
            _op("write"),
        ),
    )
    router = RouterSpec(
        name="admin",
        engine=_sqlite("router_store"),
        paths=(PathSpec(path="/widgets", kind="resource", tables=(table,)),),
    )
    spec = AppSpec(engine=_sqlite("app_store"), routers=(router,))

    lowered = lower_concrete_engine_inputs(spec)
    lowered_router = lowered.routers[0]
    lowered_table = lowered_router.paths[0].tables[0]
    lowered_read = lowered_table.ops[0]
    lowered_write = lowered_table.ops[1]

    assert lowered.engine is None
    assert lowered.engine_name == "app_store"
    assert lowered_router.engine is None
    assert lowered_router.engine_name == "router_store"
    assert lowered_table.engine is None
    assert lowered_table.engine_name == "table_store"
    assert lowered_read.engine is None
    assert lowered_read.engine_name == "read_store"
    assert lowered_write.engine is None
    assert lowered_write.engine_name is None
    assert tuple(engine.name for engine in lowered.engines) == (
        "app_store",
        "router_store",
        "table_store",
        "read_store",
    )


def test_concrete_lowering_generates_stable_names_for_unnamed_inputs() -> None:
    spec = AppSpec(
        engine="sqlite://:memory:",
        routers=(
            RouterSpec(
                name="Api",
                engine={"kind": "sqlite", "memory": True},
                paths=(
                    PathSpec(
                        path="/items",
                        kind="resource",
                        tables=(
                            TableSpec(
                                name="Inventory Item",
                                model_ref="tests.items:InventoryItem",
                                engine={"kind": "sqlite", "memory": True},
                                ops=(
                                    _op(
                                        "bulk load",
                                        engine={"kind": "sqlite", "memory": True},
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )

    lowered = lower_concrete_engine_inputs(spec)

    assert tuple(engine.name for engine in lowered.engines) == (
        "app",
        "router_api",
        "api_table_inventory_item",
        "api_table_inventory_item_bulk_load",
    )


def test_concrete_lowering_rejects_conflicting_duplicate_inventory_names() -> None:
    spec = AppSpec(
        engines=(EngineSpec(kind="sqlite", memory=True, name="primary"),),
        engine={
            "kind": "sqlite",
            "memory": False,
            "name": "primary",
            "path": "other.db",
        },
    )

    with pytest.raises(
        ValueError, match="conflicts with existing engine name 'primary'"
    ):
        lower_concrete_engine_inputs(spec)


def test_webhook_authoring_lowers_to_core_path_and_op_specs() -> None:
    path = DefineWebhook(
        path="/webhooks/stripe",
        provider="stripe",
        event_type="invoice.paid",
    )

    assert isinstance(path, PathSpec)
    assert path.kind == "resource"
    assert path.path == "/webhooks/stripe"
    assert len(path.ops) == 1

    op = path.ops[0]
    assert isinstance(op, OpSpec)
    assert op.alias == "webhook_stripe_invoice_paid"
    assert op.target == "custom"
    assert op.expose_rpc is False
    assert op.http_methods == ("POST",)
    assert op.status_code == 202

    binding = op.bindings[0]
    assert binding.methods == ("POST",)
    assert binding.path == "/webhooks/stripe"
    assert op.extra["webhook"]["direction"] == "inbound"
    assert set(op.extra["webhook"]) == {"direction", "provider", "event_type"}
