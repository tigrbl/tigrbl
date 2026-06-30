from tigrbl import TigrblApp


def test_openapi_schema_is_cached_on_app() -> None:
    app = TigrblApp()

    assert getattr(app, "openapi_schema", None) is None

    document = app.openapi()

    assert app.openapi_schema is document
    assert document["openapi"] == "3.1.0"


def test_openapi_schema_cache_is_invalidated_when_routes_change() -> None:
    app = TigrblApp()
    original = app.openapi()

    def ping(_request):
        return {"ok": True}

    app.add_route("/ping", ping, methods=["GET"], include_in_schema=True)

    assert app.openapi_schema is None

    updated = app.openapi()

    assert updated is app.openapi_schema
    assert updated is not original
    assert "/ping" in updated["paths"]
