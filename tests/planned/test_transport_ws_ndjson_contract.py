import pytest

from tigrbl_core._spec.binding_spec import WsBindingSpec


def test_transport_ws_ndjson_contract() -> None:
    with pytest.raises(ValueError, match="ndjson|fail closed|planned"):
        WsBindingSpec(proto="ws", path="/ndjson", framing="ndjson")
