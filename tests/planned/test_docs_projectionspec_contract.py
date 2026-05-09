from tigrbl_core._spec import DocsProjectionSpec

from ._nested_appspec_support import multisurface_paths


def test_docs_projectionspec_selects_by_protocol_path_table_and_method() -> None:
    paths = multisurface_paths()
    projection = DocsProjectionSpec(
        name="widget-rpc",
        include_protocols=("http.jsonrpc",),
        include_paths=("/rpc",),
        include_tables=("Widget",),
        rpc_methods=("Widget.create",),
    )

    selected = projection.select(paths)

    assert len(selected) == 1
    assert selected[0].path == "/rpc"
    assert selected[0].table == "Widget"
    assert selected[0].op == "create"
    assert selected[0].rpc_methods == ("Widget.create",)


def test_docs_projectionspec_excludes_non_selected_protocols() -> None:
    selected = DocsProjectionSpec(
        name="public-http",
        include_protocols=("http.rest",),
        exclude_paths=("/widgets/{item_id}",),
    ).select(multisurface_paths())

    assert {item.path for item in selected} == {"/widgets"}
    assert all("http.jsonrpc" not in item.protocols for item in selected)
