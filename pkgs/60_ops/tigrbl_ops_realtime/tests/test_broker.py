from __future__ import annotations

import asyncio

from tigrbl_ops_realtime import (
    InMemoryRealtimeBroker,
    RealtimeEnvelope,
    WebSocketRealtimeSink,
    WebTransportRealtimeSink,
)


class RecordingSink:
    def __init__(self) -> None:
        self.events: list[RealtimeEnvelope] = []

    async def send_realtime(self, envelope: RealtimeEnvelope) -> None:
        self.events.append(envelope)


def test_room_channels_are_isolated_and_disconnect_cleans_up() -> None:
    async def exercise() -> None:
        broker = InMemoryRealtimeBroker()
        room_a = RecordingSink()
        room_b = RecordingSink()
        await broker.subscribe(channel="room:a", sink=room_a, session_id="a")
        await broker.subscribe(channel="room:b", sink=room_b, session_id="b")

        result = await broker.publish(
            channel="room:a",
            event={"message": "hello"},
            publication_id="pub-room-a",
        )
        await asyncio.sleep(0)

        assert result.queued == 1
        assert result.publication_id == "pub-room-a"
        assert room_a.events[0].publication_id == "pub-room-a"
        assert [item.event for item in room_a.events] == [{"message": "hello"}]
        assert room_b.events == []
        assert await broker.unsubscribe_session("a") == 1
        assert broker.subscriber_count("room:a") == 0
        await broker.close()

    asyncio.run(exercise())


def test_one_publication_has_distinct_subscriber_notification_ids() -> None:
    async def exercise() -> None:
        broker = InMemoryRealtimeBroker()
        first = RecordingSink()
        second = RecordingSink()
        await broker.subscribe(channel="room", sink=first, session_id="first")
        await broker.subscribe(channel="room", sink=second, session_id="second")

        result = await broker.publish(channel="room", event={"sequence": 1})
        await asyncio.sleep(0)

        assert result.publication_id.startswith("pub_")
        assert first.events[0].publication_id == result.publication_id
        assert second.events[0].publication_id == result.publication_id
        assert first.events[0].published_at == result.published_at
        assert second.events[0].published_at == result.published_at
        assert first.events[0].notification_id != second.events[0].notification_id
        await broker.close()

    asyncio.run(exercise())


def test_slow_subscriber_is_bounded_and_drops_without_blocking_publish() -> None:
    class BlockedSink:
        async def send_realtime(self, envelope: RealtimeEnvelope) -> None:
            await asyncio.Event().wait()

    async def exercise() -> None:
        broker = InMemoryRealtimeBroker(queue_size=1)
        await broker.subscribe(channel="room", sink=BlockedSink(), session_id="slow")
        first = await broker.publish(channel="room", event=1)
        await asyncio.sleep(0)
        second = await broker.publish(channel="room", event=2)
        third = await broker.publish(channel="room", event=3)

        assert first.queued == 1
        assert second.queued == 1
        assert third.dropped == 1
        assert broker.metrics("room")["dropped"] == 1
        await broker.close()

    asyncio.run(exercise())


def test_transport_sinks_own_transport_projection() -> None:
    async def exercise() -> None:
        websocket_messages: list[dict] = []
        webtransport_messages: list[dict] = []
        envelope = RealtimeEnvelope(channel="room", event={"kind": "presence"})

        await WebSocketRealtimeSink(websocket_messages.append).send_realtime(envelope)
        await WebTransportRealtimeSink(
            webtransport_messages.append,
            session_id="session-1",
        ).send_realtime(envelope)

        assert websocket_messages[0]["type"] == "websocket.send"
        assert webtransport_messages[0]["type"] == "webtransport.stream.send"
        assert webtransport_messages[0]["stream_id"] == "realtime-events"
        assert webtransport_messages[0]["more"] is True
        assert webtransport_messages[0]["emit_id"]
        websocket_frame = __import__("json").loads(websocket_messages[0]["text"])
        assert websocket_frame["params"]["publication_id"] == envelope.publication_id
        assert websocket_frame["params"]["notification_id"] == envelope.notification_id

    asyncio.run(exercise())
