from __future__ import annotations

import pytest

from tigrbl import AppSpec, ResponseSpec, RouterSpec, TableSpec
from tigrbl_core._spec.app_spec import normalize_app_spec


def test_appspec_defaults_are_stable_and_normalized() -> None:
    app = normalize_app_spec(
        AppSpec(
            title="",
            version="",
            jsonrpc_prefix="",
            system_prefix="",
            routers=[RouterSpec(name="api")],
        )
    )

    assert app.title == "Tigrbl"
    assert app.version == "0.1.0"
    assert app.execution_backend == "auto"
    assert app.jsonrpc_prefix == "/rpc"
    assert app.system_prefix == "/system"
    assert isinstance(app.routers, tuple)


def test_appspec_preserves_router_owned_tables_without_leaking_to_app_tables() -> None:
    table = TableSpec(model_ref="pkg.models:Book")
    router_response = ResponseSpec(kind="json", status_code=202)
    router = RouterSpec(
        name="library",
        prefix="/v1",
        tags=("Library",),
        response=router_response,
        tables=(table,),
    )
    app = AppSpec(
        title="Library",
        version="1.0.0",
        routers=(router,),
        tables=(),
        response=ResponseSpec(kind="json"),
    )

    assert app.routers == (router,)
    assert app.tables == ()
    assert app.routers[0].tables == (table,)
    assert app.routers[0].response is router_response


def test_routerspec_rejects_legacy_models_key() -> None:
    with pytest.raises(ValueError, match="does not accept 'models'"):
        RouterSpec.from_dict({"name": "legacy", "models": ["pkg.models:Book"]})


def test_routerspec_rejects_string_table_entries() -> None:
    with pytest.raises(TypeError, match="tables entries must be nested specs"):
        RouterSpec(name="bad", tables=("pkg.models:Book",))


def test_routerspec_preserves_router_level_metadata_separately_from_app() -> None:
    router = RouterSpec(
        name="admin",
        prefix="/admin",
        tags=("Admin", "Internal"),
        response=ResponseSpec(kind="json", status_code=200),
    )
    app = AppSpec(
        title="Service",
        response=ResponseSpec(kind="json", status_code=204),
        routers=(router,),
    )

    assert app.response.status_code == 204
    assert app.routers[0].response.status_code == 200
    assert app.routers[0].prefix == "/admin"
    assert app.routers[0].tags == ("Admin", "Internal")
