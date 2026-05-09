from ._nested_appspec_support import shared_rpc_path, widget_rest_paths


def test_crud_rest_and_jsonrpc_corpus_preserves_path_ownership() -> None:
    rest_collection, rest_member = widget_rest_paths()
    rpc_path = shared_rpc_path()

    assert [path.path for path in (rest_collection, rest_member, rpc_path)] == [
        "/widgets",
        "/widgets/{item_id}",
        "/rpc",
    ]
    assert {
        rest_collection.binding_path(op.bindings[0])
        for op in rest_collection.tables[0].ops
    } == {"/widgets"}
    assert {
        rest_member.binding_path(op.bindings[0])
        for op in rest_member.tables[0].ops
    } == {"/widgets/{item_id}"}
    assert {rpc_path.binding_path(op.bindings[0]) for op in rpc_path.iter_ops()} == {
        "/rpc"
    }


def test_crud_rest_and_jsonrpc_corpus_keeps_table_groups_separate() -> None:
    rpc_path = shared_rpc_path()

    by_table = {
        table.name: {binding.rpc_method for op in table.ops for binding in op.bindings}
        for table in rpc_path.tables
    }

    assert by_table == {
        "Widget": {"Widget.create", "Widget.list"},
        "Account": {"Account.create", "Account.list"},
    }
