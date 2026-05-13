from tigrbl_core._spec import DocsPayloadSpec

from ._nested_appspec_support import multisurface_paths


def test_docs_payload_path_is_ordinary_pathspec_with_projection() -> None:
    payload_paths = {
        path.path: path.docs_payload
        for path in multisurface_paths()
        if path.kind == "docs-payload"
    }

    openapi = payload_paths["/openapi.json"]
    openrpc = payload_paths["/openrpc.json"]

    assert isinstance(openapi, DocsPayloadSpec)
    assert openapi.kind == "openapi"
    assert openapi.projection.name == "public-http"
    assert openapi.projection.include_protocols == ("http.rest",)

    assert isinstance(openrpc, DocsPayloadSpec)
    assert openrpc.kind == "openrpc"
    assert openrpc.projection.name == "public-rpc"
    assert openrpc.projection.include_protocols == ("http.jsonrpc",)
