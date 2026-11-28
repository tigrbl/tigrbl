import asyncio
import os

import pytest

from tigrbl import TigrblApp
from tigrbl_engine_redis import RedisSubscriptionQuotaStore
from tigrbl_ops_realtime.quotas import (
    SubscriptionAdmissionError,
    SubscriptionIdentity,
    SubscriptionPolicy,
)

ALICE = SubscriptionIdentity("issuer", "alice", "tenant")
BOB = SubscriptionIdentity("issuer", "bob", "tenant")


class Sink:
    def __init__(self):
        self.events = []

    async def send_realtime(self, event):
        self.events.append(event)


@pytest.mark.asyncio
async def test_redis_shared_atomicity_rate_tokens_fencing_and_outage():
    import fakeredis.aioredis

    server = fakeredis.FakeServer()
    p = SubscriptionPolicy(
        scope="deployment",
        max_active_per_tenant=2,
        open_rate_per_user=0.1,
        open_burst_per_user=2,
    )
    client = fakeredis.aioredis.FakeRedis(server=server)
    a = RedisSubscriptionQuotaStore(p, client=client)
    b = RedisSubscriptionQuotaStore(
        p, client=fakeredis.aioredis.FakeRedis(server=server)
    )
    first = await a.acquire(ALICE, "one")
    second = await b.acquire(BOB, "two")
    with pytest.raises(SubscriptionAdmissionError) as exc:
        await b.acquire(ALICE, "three")
    assert exc.value.scope == "tenant"
    await second.release()
    with pytest.raises(SubscriptionAdmissionError) as exc:
        await b.acquire(ALICE, "three")
    assert exc.value.code == "subscription_rate_exceeded"
    transferred = await b.transfer(first.id, first.generation)
    assert not await a.owns(first) and await b.owns(transferred)
    await first.release()
    assert await b.owns(transferred)
    await transferred.release()
    server.connected = False
    with pytest.raises(SubscriptionAdmissionError) as exc:
        await b.acquire(BOB, "four")
    assert exc.value.status_code == 503
    await client.aclose()
    await b.client.aclose()


@pytest.mark.asyncio
async def test_real_redis_multiple_clients():
    url = os.environ.get("TIGRBL_TEST_REDIS_URL")
    if not url:
        pytest.skip("set TIGRBL_TEST_REDIS_URL for real Redis integration")
    from uuid import uuid4
    from redis.asyncio import Redis

    p = SubscriptionPolicy(scope="deployment", max_active_per_tenant=3)
    clients = [Redis.from_url(url) for _ in range(4)]
    namespace = "test:" + uuid4().hex
    stores = [
        RedisSubscriptionQuotaStore(p, client=c, namespace=namespace) for c in clients
    ]
    try:
        results = await asyncio.gather(
            *(
                stores[n % 4].acquire(
                    SubscriptionIdentity("issuer", str(n), "tenant"), "watch"
                )
                for n in range(30)
            ),
            return_exceptions=True,
        )
        leases = [x for x in results if not isinstance(x, Exception)]
        assert len(leases) == 3
        await asyncio.gather(*(x.release() for x in leases))
        await (await stores[0].acquire(ALICE, "again")).release()

        app = TigrblApp(
            subscription_policy=p,
            subscription_identity=lambda ctx: ctx["verified"],
            subscription_store=stores[0],
            subscription_resume_ttl=5,
        )
        broker = app.__realtime_broker__
        assert broker.admission.store is stores[0]
        try:
            old_sink, new_sink = Sink(), Sink()
            initial = await broker.subscribe(
                channel="events",
                sink=old_sink,
                session_id="redis-old",
                ctx={"verified": ALICE},
            )
            assert await broker.disconnect_session("redis-old") == 1
            resumed = await broker.resume(
                initial.subscription_id,
                expected_generation=initial.generation,
                session_id="redis-new",
                sink=new_sink,
                ctx={"verified": ALICE},
            )
            assert resumed.subscription_id == initial.subscription_id
            assert resumed.quota_lease.id == initial.quota_lease.id
            assert not await stores[1].owns(initial.quota_lease)
            assert await stores[1].owns(resumed.quota_lease)
            assert await broker.unsubscribe_session("redis-old") == 0

            publish = await broker.publish(
                channel="events",
                event={"ready": True},
                origin_correlation_id="origin",
            )
            await asyncio.wait_for(resumed.queue.join(), 3)
            assert not old_sink.events and len(new_sink.events) == 1
            (event,) = broker.delivery_events()
            assert event["publication_id"] == publish.publication_id
            assert event["lease_id"] == resumed.quota_lease.id
            assert event["subscription_id"] == initial.subscription_id
            assert event["attachment_generation"] == resumed.generation
        finally:
            await broker.close()
    finally:
        await clients[0].delete(stores[0].key)
        await asyncio.gather(*(c.aclose() for c in clients))
