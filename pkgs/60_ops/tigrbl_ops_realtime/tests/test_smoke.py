import importlib.util
import json

import pytest

from tigrbl_ops_realtime import InMemoryRealtimeBroker, publish, subscribe, unsubscribe_session


def test_package_namespace_available() -> None:
    assert importlib.util.find_spec("tigrbl_ops_realtime") is not None


@pytest.mark.asyncio
async def test_subscribe_publish_fanout_through_context_broker() -> None:
    sent: list[dict[str, object]] = []

    class Sink:
        async def send(self, message: dict[str, object]) -> None:
            sent.append(message)

    broker = InMemoryRealtimeBroker()
    ctx = {
        "channel": Sink(),
        "realtime": {
            "broker": broker,
            "session_id": "session-1",
        },
    }

    subscribed = await subscribe(
        {"channel": "thread:alpha", "cursor": "msg-1"},
        ctx=ctx,
    )
    published = await publish(
        {"channel": "thread:alpha", "event": {"body": "hello"}},
        ctx={"realtime": {"broker": broker}},
    )

    assert subscribed["subscribed"] is True
    assert subscribed["subscription_id"] == "session-1"
    assert subscribed["subscriber_count"] == 1
    assert published["delivered"] == 1
    assert json.loads(str(sent[0]["text"])) == {
        "jsonrpc": "2.0",
        "method": "realtime.publish",
        "params": {
            "channel": "thread:alpha",
            "event": {"body": "hello"},
        },
    }


@pytest.mark.asyncio
async def test_unsubscribe_session_removes_registered_interests() -> None:
    broker = InMemoryRealtimeBroker()
    ctx = {
        "channel": object(),
        "realtime": {
            "broker": broker,
            "session_id": "session-1",
        },
    }

    await subscribe({"channel": "thread:alpha"}, ctx=ctx)
    removed = await unsubscribe_session(ctx)

    assert removed == {
        "unsubscribed": True,
        "removed": 1,
        "session_id": "session-1",
    }
    assert broker.subscriber_count("thread:alpha") == 0
