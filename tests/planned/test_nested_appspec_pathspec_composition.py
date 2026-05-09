from tigrbl_core._spec import AppSpec, PathSpec, RouterSpec, TableSpec

from ._nested_appspec_support import multisurface_appspec


def test_nested_appspec_pathspec_composition_is_address_first() -> None:
    app = multisurface_appspec()

    assert isinstance(app, AppSpec)
    assert len(app.routers) == 1
    router = app.routers[0]
    assert isinstance(router, RouterSpec)
    assert all(isinstance(path, PathSpec) for path in router.paths)
    assert {path.path for path in router.paths} >= {
        "/widgets",
        "/widgets/{item_id}",
        "/rpc",
        "/openapi.json",
        "/openrpc.json",
        "/docs",
    }

    widget_path = next(path for path in router.paths if path.path == "/widgets")
    assert isinstance(widget_path.tables[0], TableSpec)
    assert widget_path.tables[0].name == "Widget"
    assert widget_path.tables[0].resource == "widget"
    assert widget_path.tables[0].model_ref == "app.models:Widget"
