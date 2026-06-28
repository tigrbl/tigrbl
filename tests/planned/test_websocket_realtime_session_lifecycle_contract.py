import pytest


pytestmark = pytest.mark.xfail(
    reason="planned WebSocket realtime lifecycle contract; implementation scope not frozen",
    strict=False,
)


def test_websocket_session_phase_order_contract() -> None:
    assert False


def test_websocket_session_close_cleanup_order_contract() -> None:
    assert False


def test_websocket_app_handler_does_not_own_loop_contract() -> None:
    assert False
