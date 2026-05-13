from tigrbl_core._spec.binding_spec import HttpStreamBindingSpec
from tigrbl_core._spec.path_spec import PathSpec


def test_transport_stream_pathkind_contract() -> None:
    binding = HttpStreamBindingSpec(proto="http.stream", path="/items/stream")
    path = PathSpec(path="/items/stream", kind="stream")

    assert path.binding_path(binding) == "/items/stream"
