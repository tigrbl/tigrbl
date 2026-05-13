from ._nested_appspec_support import multisurface_appspec


def test_nested_appspec_multisurface_corpus_covers_required_surfaces() -> None:
    app = multisurface_appspec()
    paths = app.routers[0].paths

    assert {path.kind for path in paths} >= {
        "resource",
        "jsonrpc",
        "websocket",
        "sse",
        "webtransport",
        "docs-payload",
        "docs-uix",
        "static",
        "mount",
    }
    assert app.routers[0].middlewares == ("authn", "audit")
