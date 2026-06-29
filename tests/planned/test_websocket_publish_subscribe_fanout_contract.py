from __future__ import annotations

from tigrbl_kernel.protocol_chains.websocket import compile_websocket_chain


def test_websocket_subscribe_ack_registers_interest() -> None:
    policy = compile_websocket_chain({"path": "/ws/thread/{thread_id}", "scheme": "ws"})[
        "subscribe_policy"
    ]

    assert policy["operation_shape"] == "finite_request_response"
    assert policy["ack_framing"] == "jsonrpc"
    assert policy["owns_receive_loop"] is False
    assert policy["registration"] == {
        "atom": "subscription.register",
        "phase": "POST_COMMIT",
    }


def test_websocket_publish_fanout_to_subscriber() -> None:
    policy = compile_websocket_chain({"path": "/ws/thread/{thread_id}", "scheme": "ws"})[
        "publish_policy"
    ]

    assert policy["publish_only_op"] is True
    assert policy["placement"]["EGRESS_FINALIZE"] == (
        "publish.fanout",
        "framing.encode",
        "transport.emit",
    )


def test_websocket_subscription_unregister_on_close() -> None:
    policy = compile_websocket_chain({"path": "/ws/thread/{thread_id}", "scheme": "ws"})[
        "subscribe_policy"
    ]

    assert policy["cleanup"] == {
        "atom": "subscription.unregister",
        "phase": "PRE_SESSION_CLOSE",
    }


def test_websocket_publish_no_subscriber_no_error() -> None:
    policy = compile_websocket_chain({"path": "/ws/thread/{thread_id}", "scheme": "ws"})[
        "publish_policy"
    ]

    assert "publish.fanout" in policy["placement"]["EGRESS_FINALIZE"]
