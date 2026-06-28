import pytest


pytestmark = pytest.mark.xfail(
    reason="planned WebSocket publish/subscribe fanout contract; implementation scope not frozen",
    strict=False,
)


def test_websocket_subscribe_ack_registers_interest() -> None:
    assert False


def test_websocket_publish_fanout_to_subscriber() -> None:
    assert False


def test_websocket_subscription_unregister_on_close() -> None:
    assert False


def test_websocket_publish_no_subscriber_no_error() -> None:
    assert False
