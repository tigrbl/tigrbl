from ._nested_appspec_support import shared_rpc_path, widget_rest_paths


def test_shared_jsonrpc_dispatcher_contains_multiple_table_groups() -> None:
    rpc_path = shared_rpc_path()

    assert rpc_path.path == "/rpc"
    assert [table.name for table in rpc_path.tables] == ["Widget", "Account"]
    assert {
        binding.rpc_method
        for table in rpc_path.tables
        for op in table.ops
        for binding in op.bindings
    } == {"Widget.create", "Widget.list", "Account.create", "Account.list"}


def test_shared_jsonrpc_crud_aliases_match_rest_collection_aliases() -> None:
    rest_collection, _ = widget_rest_paths()
    rpc_path = shared_rpc_path()

    rest_aliases = {op.alias for op in rest_collection.tables[0].ops}
    rpc_widget_aliases = {op.alias for op in rpc_path.tables[0].ops}

    assert rest_aliases == rpc_widget_aliases == {"create", "list"}
