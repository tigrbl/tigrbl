import pytest

from tigrbl_ops_realtime import InMemoryRealtimeBroker, resume_subscription, subscribe


@pytest.mark.asyncio
async def test_subscription_ack_versions_and_authorized_resume():
    frames = []

    async def sink(event):
        frames.append(event)

    def allow_resume(ctx, previous, destination):
        return ctx.get("verified_requester") == previous.metadata.get("session_id")

    broker = InMemoryRealtimeBroker(
        authorize_subscription_resume=allow_resume, resume_ttl_seconds=10
    )

    def context(transport, version):
        return {
            "verified_requester": "requester",
            "identity": {"transport_session_id": transport, "session_id": "requester"},
            "realtime": {
                "sink": sink, "broker": broker, "transport": "websocket",
                "subscription_ack_version": version,
            },
        }

    try:
        old = context("socket-v1", 1)
        assert (await subscribe({"channel": "legacy"}, ctx=old))["subscription_id"] == "socket-v1"
        initial = await subscribe({"channel": "v2"}, ctx=context("old", 2))
        assert initial["subscription_id"] != initial["transport_session_id"]
        params = {key: initial[key] for key in ("subscription_id", "attachment_generation")}
        denied = context("wrong", 2)
        denied["verified_requester"] = "other"
        with pytest.raises(PermissionError):
            await resume_subscription(params, ctx=denied)
        assert await broker.disconnect_session("old") == 1
        assert broker.subscriber_count("v2") == 0
        resumed = await resume_subscription(params, ctx=context("new", 2))
        assert resumed["subscription_id"] == initial["subscription_id"]
        assert resumed["transport_session_id"] == "new"
        assert resumed["attachment_generation"] != initial["attachment_generation"]
        assert await broker.unsubscribe_session("old") == 0
        assert await broker.unsubscribe_session("new") == 1
    finally:
        await broker.close()


@pytest.mark.asyncio
async def test_webtransport_delivery_uses_recipient_egress_stream_and_session():
    import asyncio
    from tigrbl_ops_realtime import publish

    broker = InMemoryRealtimeBroker()
    delivered = asyncio.Event()
    frames = []

    async def send(message):
        frames.append(message)
        delivered.set()

    subscriber = {
        "realtime": {
            "broker": broker, "sink": send, "transport": "webtransport",
            "session_id": "wt-destination", "event_stream_id": "events-1",
            "identity_for_stream": lambda stream: {"stream_correlation_id": f"corr-{stream}"},
            "subscription_ack_version": 2,
        },
        "identity": {
            "transport_session_id": "wt-destination", "correlation_id": "destination-correlation",
            "stream_id": "control", "stream_correlation_id": "control-correlation",
        },
    }
    publisher = {
        "identity": {"invocation_id": "origin-invocation", "correlation_id": "origin-correlation"},
        "realtime": {"broker": broker},
    }
    try:
        subscription = await subscribe({"channel": "events"}, ctx=subscriber)
        publication = await publish({"channel": "events", "event": {"n": 1}}, ctx=publisher)
        await asyncio.wait_for(delivered.wait(), 1)
        delivery, = broker.delivery_events()
        frame, = frames
        assert delivery["subscription_id"] == subscription["subscription_id"]
        assert delivery["publication_id"] == publication["publication_id"]
        assert delivery["stream_id"] == frame["stream_id"] == "events-1"
        assert delivery["stream_correlation_id"] == "corr-events-1"
        assert delivery["correlation_id"] == "destination-correlation"
        assert delivery["origin_correlation_id"] == "origin-correlation"
        assert delivery["origin_invocation_id"] == "origin-invocation"
    finally:
        await broker.close()


@pytest.mark.asyncio
async def test_quota_broker_releases_suspended_attachment_on_app_shutdown():
    from tigrbl import TigrblApp
    from tigrbl.subscriptions import SubscriptionIdentity, SubscriptionPolicy

    principal = SubscriptionIdentity("issuer", "user", "tenant")
    app = TigrblApp(
        subscription_identity=lambda ctx: ctx.get("verified"),
        subscription_policy=SubscriptionPolicy(max_active_per_user=1),
        subscription_resume_ttl=15,
    )
    broker = app.__realtime_broker__

    async def sink(message):
        pass

    await subscribe({"channel": "events"}, ctx={
        "verified": principal,
        "identity": {"transport_session_id": "closing"},
        "realtime": {"sink": sink, "broker": broker, "transport": "websocket"},
    })
    await broker.disconnect_session("closing")
    assert len(broker.admission.store.leases) == 1

    incoming = iter(["lifespan.startup", "lifespan.shutdown"])
    statuses = []

    async def receive():
        return {"type": next(incoming)}

    async def send(message):
        statuses.append(message["type"])

    await app({"type": "lifespan"}, receive, send)
    assert statuses == ["lifespan.startup.complete", "lifespan.shutdown.complete"]
    assert not broker.admission.store.leases
