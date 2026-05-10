import pytest

from tigrbl_core._spec.binding_spec import WsBindingSpec


def test_ws_jsonld_fail_closed_contract() -> None:
    with pytest.raises(ValueError, match="jsonld|fail closed|planned"):
        WsBindingSpec(proto="ws", path="/jsonld", framing="jsonld")

    with pytest.raises(ValueError, match="jsonld|fail closed|planned"):
        WsBindingSpec(proto="wss", path="/jsonld", framing="jsonld")
