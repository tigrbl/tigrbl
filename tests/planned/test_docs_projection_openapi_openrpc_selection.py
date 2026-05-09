from tigrbl_core._spec import DocsProjectionSpec

from ._nested_appspec_support import multisurface_paths


def test_openapi_and_openrpc_projections_are_disjoint_by_protocol() -> None:
    paths = multisurface_paths()
    openapi = DocsProjectionSpec(name="openapi", include_protocols=("http.rest",))
    openrpc = DocsProjectionSpec(name="openrpc", include_protocols=("http.jsonrpc",))

    openapi_selection = openapi.select(paths)
    openrpc_selection = openrpc.select(paths)

    assert {item.path for item in openapi_selection} == {
        "/widgets",
        "/widgets/{item_id}",
    }
    assert {item.path for item in openrpc_selection} == {"/rpc"}
    assert all("http.jsonrpc" not in item.protocols for item in openapi_selection)
    assert all("http.rest" not in item.protocols for item in openrpc_selection)
