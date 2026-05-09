import pytest

from tigrbl_core._spec import HttpRestBindingSpec, PathSpec

from ._nested_appspec_support import shared_rpc_path, widget_rest_paths


def test_protocol_bindings_inherit_containing_pathspec_address() -> None:
    rest_path, _ = widget_rest_paths()
    rest_binding = rest_path.tables[0].ops[0].bindings[0]
    rpc_path = shared_rpc_path()
    rpc_binding = rpc_path.tables[0].ops[0].bindings[0]

    assert rest_path.binding_path(rest_binding) == "/widgets"
    assert rpc_path.binding_path(rpc_binding) == "/rpc"
    assert rpc_binding.rpc_method == "Widget.create"


def test_conflicting_binding_path_is_rejected() -> None:
    path = PathSpec(path="/widgets")
    binding = HttpRestBindingSpec(
        proto="http.rest",
        methods=("POST",),
        path="/accounts",
    )

    with pytest.raises(ValueError, match="conflicts"):
        path.binding_path(binding)
