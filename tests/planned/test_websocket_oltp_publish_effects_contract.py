from __future__ import annotations

from tigrbl_kernel.protocol_chains.websocket import compile_websocket_chain


def test_websocket_oltp_create_only_does_not_publish() -> None:
    policy = compile_websocket_chain({"path": "/ws/thread/{thread_id}", "scheme": "ws"})[
        "publish_policy"
    ]

    assert policy["automatic_for_oltp"] is False
    assert policy["create_only_publishes"] is False


def test_websocket_oltp_create_and_publish_effect() -> None:
    policy = compile_websocket_chain({"path": "/ws/thread/{thread_id}", "scheme": "ws"})[
        "publish_policy"
    ]

    assert policy["create_and_publish_requires_effect"] is True
    assert policy["placement"]["POST_COMMIT"] == ("publish.prepare", "publish.enqueue")


def test_websocket_oltp_rollback_does_not_publish() -> None:
    policy = compile_websocket_chain({"path": "/ws/thread/{thread_id}", "scheme": "ws"})[
        "publish_policy"
    ]

    assert policy["rollback_suppresses_publish"] is True
