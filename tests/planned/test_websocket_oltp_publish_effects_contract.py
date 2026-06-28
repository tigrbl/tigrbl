import pytest


pytestmark = pytest.mark.xfail(
    reason="planned WebSocket OLTP publish effect contract; implementation scope not frozen",
    strict=False,
)


def test_websocket_oltp_create_only_does_not_publish() -> None:
    assert False


def test_websocket_oltp_create_and_publish_effect() -> None:
    assert False


def test_websocket_oltp_rollback_does_not_publish() -> None:
    assert False
