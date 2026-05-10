import pytest

from tigrbl_core._spec.binding_spec import WsBindingSpec


def test_transport_ws_jsonld_contract() -> None:
    with pytest.raises(ValueError, match="jsonld|fail closed|planned"):
        WsBindingSpec(proto="ws", path="/jsonld", framing="jsonld")
