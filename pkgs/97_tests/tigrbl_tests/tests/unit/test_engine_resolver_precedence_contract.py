import pytest

from tigrbl._spec import EngineSpec
from tigrbl.engine import resolver


class Widget:
    pass


class Api:
    pass


def _sqlite_engine(name: str) -> EngineSpec:
    return EngineSpec(kind="sqlite", memory=True, name=name)


def test_named_engine_resolution_uses_nearest_scope_precedence() -> None:
    router = Api()

    resolver.register_engines(
        (
            _sqlite_engine("app"),
            _sqlite_engine("router"),
            _sqlite_engine("table"),
            _sqlite_engine("op"),
        )
    )
    resolver.set_default_engine_name("app")
    resolver.register_router_engine_name(router, "router")
    resolver.register_table_engine_name(Widget, "table")
    resolver.register_op_engine_name(Widget, "create", "op")

    assert resolver.resolve_provider().spec.name == "app"
    assert resolver.resolve_provider(router=router).spec.name == "router"
    assert resolver.resolve_provider(router=router, model=Widget).spec.name == "table"
    assert (
        resolver.resolve_provider(router=router, model=Widget, op_alias="create")
        .spec.name
        == "op"
    )


def test_named_engine_resolution_fails_closed_for_unknown_names() -> None:
    resolver.register_engines((_sqlite_engine("known"),))

    with pytest.raises(RuntimeError, match="Unknown engine name 'missing'"):
        resolver.resolve_provider(engine_name="missing")

    with pytest.raises(RuntimeError, match="Unknown engine name 'missing'"):
        resolver.register_table_engine_name(Widget, "missing")


def test_legacy_object_bindings_continue_to_resolve_after_named_inventory() -> None:
    router = Api()
    resolver.register_engine("inventory", _sqlite_engine("inventory"))
    resolver.register_router(router, _sqlite_engine("legacy-router"))

    provider = resolver.resolve_provider(router=router)

    assert provider is not None
    assert provider.spec.name == "legacy-router"

