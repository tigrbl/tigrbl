import pytest

from tigrbl_core._spec.binding_spec import WsBindingSpec


def test_ws_ndjson_fail_closed_contract() -> None:
    with pytest.raises(ValueError, match="ndjson|fail closed|planned"):
        WsBindingSpec(proto="ws", path="/ndjson", framing="ndjson")

    with pytest.raises(ValueError, match="ndjson|fail closed|planned"):
        WsBindingSpec(proto="wss", path="/ndjson", framing="ndjson")
