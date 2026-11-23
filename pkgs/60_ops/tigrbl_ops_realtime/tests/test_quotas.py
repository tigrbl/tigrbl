import asyncio
from dataclasses import asdict
import os

import pytest

from tigrbl_ops_realtime.broker import InMemoryRealtimeBroker
from tigrbl_ops_realtime.configuration import resolve_subscription_policy
from tigrbl_ops_realtime.quotas import (
    LocalSubscriptionQuotaStore,
    SubscriptionAdmission,
    SubscriptionAdmissionError,
    SubscriptionIdentity,
    SubscriptionPolicy,
)


ALICE = SubscriptionIdentity("issuer", "alice", "tenant")
BOB = SubscriptionIdentity("issuer", "bob", "tenant")


class Clock:
    def __init__(self):
        self.now = 100.0

    def __call__(self):
        return self.now


@pytest.mark.parametrize(
    "kwargs",
    [
        {"max_active_per_user": True},
        {"max_active_per_tenant": 0},
        {"open_rate_per_user": float("inf"), "open_burst_per_user": 2},
        {"open_rate_per_tenant": 1},
        {"open_burst_per_user": 2},
        {"lease_renewal_seconds": 60},
        {"scope": "deployment", "store": "local"},
        {"namespace": ""},
        {"max_active_per_user": 1.5},
    ],
)
def test_strict_policy(kwargs):
    with pytest.raises(ValueError):
        SubscriptionPolicy(**kwargs)


@pytest.mark.asyncio
async def test_atomic_user_tenant_operation_caps_and_rollback():
    store = LocalSubscriptionQuotaStore(
        SubscriptionPolicy(max_active_per_user=2, max_active_per_tenant=2)
    )
    a = await store.acquire(ALICE, "watch", operation_limit=1)
    with pytest.raises(
        SubscriptionAdmissionError, match="subscription_quota_exceeded"
    ) as exc:
        await store.acquire(ALICE, "watch", operation_limit=1)
    assert exc.value.scope == "operation"
    b = await store.acquire(BOB, "watch")
    with pytest.raises(SubscriptionAdmissionError) as exc:
        await store.acquire(ALICE, "other")
    assert exc.value.scope == "tenant" and len(store.leases) == 2
    await b.release()
    c = await store.acquire(ALICE, "other")
    assert len(store.leases) == 2
    await a.release()
    await a.release()
    await c.release()
    assert not store.leases


@pytest.mark.asyncio
async def test_close_and_capacity_refusal_do_not_refund_open_rate():
    clock = Clock()
    store = LocalSubscriptionQuotaStore(
        SubscriptionPolicy(
            max_active_per_user=1, open_rate_per_user=1, open_burst_per_user=2
        ),
        clock=clock,
    )
    a = await store.acquire(ALICE, "one")
    with pytest.raises(SubscriptionAdmissionError) as exc:
        await store.acquire(ALICE, "two")
    assert exc.value.code == "subscription_quota_exceeded"
    await a.release()
    with pytest.raises(SubscriptionAdmissionError) as exc:
        await store.acquire(ALICE, "two")
    assert exc.value.code == "subscription_rate_exceeded"
    clock.now += 1
    await (await store.acquire(ALICE, "two")).release()


@pytest.mark.asyncio
async def test_expiry_and_resume_fence_old_generations():
    clock = Clock()
    store = LocalSubscriptionQuotaStore(
        SubscriptionPolicy(max_active_per_user=1), clock=clock
    )
    old = await store.acquire(ALICE, "watch")
    new = await store.transfer(old.id, old.generation)
    assert not await store.owns(old) and await store.owns(new)
    await old.release()
    assert await store.owns(new)
    clock.now += 61
    assert not await store.owns(new)
    await (await store.acquire(ALICE, "watch")).release()


@pytest.mark.asyncio
async def test_many_concurrent_acquires_cannot_exceed_cap():
    store = LocalSubscriptionQuotaStore(SubscriptionPolicy(max_active_per_tenant=3))
    results = await asyncio.gather(
        *(
            store.acquire(SubscriptionIdentity("issuer", str(n), "tenant"), "watch")
            for n in range(30)
        ),
        return_exceptions=True,
    )
    assert sum(not isinstance(x, Exception) for x in results) == 3


class Sink:
    def __init__(self):
        self.events = []

    async def send_realtime(self, event):
        self.events.append(event)


@pytest.mark.asyncio
async def test_broker_multiplexing_refusal_keeps_admitted_work_and_cleanup():
    admission = SubscriptionAdmission(
        SubscriptionPolicy(max_active_per_user=2), lambda ctx: ctx["verified"]
    )
    broker = InMemoryRealtimeBroker(admission=admission)
    sink = Sink()
    ctx = {"verified": ALICE, "payload": {"principal": "forged"}}
    await broker.subscribe(channel="orders", sink=sink, session_id="socket-a", ctx=ctx)
    await broker.subscribe(
        channel="inventory", sink=sink, session_id="socket-a", ctx=ctx
    )
    with pytest.raises(SubscriptionAdmissionError):
        await broker.subscribe(
            channel="third", sink=sink, session_id="socket-b", ctx=ctx
        )
    await broker.publish(channel="orders", event={"ok": True})
    await asyncio.sleep(0)
    await asyncio.sleep(0)
    assert broker.subscriber_count("orders") == 1
    await broker.unsubscribe_session("socket-a")
    assert not admission.store.leases
    await broker.close()


@pytest.mark.asyncio
async def test_unverified_identity_cannot_allocate_subscription():
    admission = SubscriptionAdmission(
        SubscriptionPolicy(max_active_per_user=1), lambda ctx: ctx.get("verified")
    )
    with pytest.raises(SubscriptionAdmissionError) as exc:
        await admission.acquire({"payload": asdict(ALICE)}, "watch")
    assert exc.value.status_code == 403
    assert not admission.store.leases


@pytest.mark.asyncio
async def test_resume_reauthorizes_consumes_rate_and_revocation_releases():
    admission = SubscriptionAdmission(
        SubscriptionPolicy(
            max_active_per_user=1, open_rate_per_user=0.1, open_burst_per_user=2
        ),
        lambda ctx: ctx["verified"],
    )
    broker = InMemoryRealtimeBroker(admission=admission, resume_ttl_seconds=15)
    first = await broker.subscribe(
        channel="orders", sink=Sink(), session_id="old", ctx={"verified": ALICE}
    )
    with pytest.raises(SubscriptionAdmissionError):
        await broker.resume(
            first.subscription_id,
            expected_generation=first.generation,
            session_id="forged",
            sink=Sink(),
            ctx={"verified": BOB},
        )
    assert await broker.disconnect_session("old") == 1
    resumed = await broker.resume(
        first.subscription_id,
        expected_generation=first.generation,
        session_id="new",
        sink=Sink(),
        ctx={"verified": ALICE},
    )
    assert resumed.subscription_id == first.subscription_id
    assert resumed.quota_lease.id == first.quota_lease.id
    assert resumed.generation != first.generation
    assert await broker.unsubscribe_session("old") == 0
    assert len(admission.store.leases) == 1 and not await admission.store.owns(
        first.quota_lease
    )
    with pytest.raises(SubscriptionAdmissionError) as exc:
        await broker.resume(
            resumed.subscription_id,
            expected_generation=resumed.generation,
            session_id="newer",
            sink=Sink(),
            ctx={"verified": ALICE},
        )
    assert exc.value.code == "subscription_rate_exceeded"
    assert await broker.revoke_identity(ALICE) == 1
    assert not admission.store.leases
    await broker.close()


def test_configuration_precedence_and_authoritative_python(tmp_path):
    path = tmp_path / "app.toml"
    path.write_text(
        "[subscriptions]\nmax_active_per_user=2\nmax_active_per_tenant=20\n",
        encoding="utf-8",
    )
    policy, source = resolve_subscription_policy(
        config_file=path,
        environ={"TIGRBL_SUBSCRIPTIONS_MAX_ACTIVE_PER_USER": "3"},
        overrides={"max_active_per_user": 4},
    )
    assert policy.max_active_per_user == 4 and policy.max_active_per_tenant == 20
    assert (
        source["max_active_per_user"] == "explicit"
        and source["max_active_per_tenant"] == "toml"
    )
    typed = SubscriptionPolicy(max_active_per_user=7)
    assert (
        resolve_subscription_policy(
            authoritative=typed,
            environ={"TIGRBL_SUBSCRIPTIONS_MAX_ACTIVE_PER_USER": "8"},
        )[0]
        is typed
    )
    with pytest.raises(ValueError):
        resolve_subscription_policy(
            authoritative=typed, overrides={"max_active_per_user": 2}
        )


@pytest.mark.asyncio
async def test_redis_shared_atomicity_rate_tokens_fencing_and_outage():
    from tigrbl_ops_realtime.redis_quotas import RedisSubscriptionQuotaStore
    import fakeredis.aioredis

    server = fakeredis.FakeServer()
    p = SubscriptionPolicy(
        store="redis",
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
    from tigrbl_ops_realtime.redis_quotas import RedisSubscriptionQuotaStore

    p = SubscriptionPolicy(
        store="redis", namespace="test:" + uuid4().hex, max_active_per_tenant=3
    )
    clients = [Redis.from_url(url) for _ in range(4)]
    stores = [RedisSubscriptionQuotaStore(p, client=c) for c in clients]
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

        admission = SubscriptionAdmission(p, lambda ctx: ctx["verified"], store=stores[0])
        broker = InMemoryRealtimeBroker(admission=admission, resume_ttl_seconds=5)
        try:
            old_sink, new_sink = Sink(), Sink()
            initial = await broker.subscribe(
                channel="events", sink=old_sink, session_id="redis-old", ctx={"verified": ALICE},
            )
            assert await broker.disconnect_session("redis-old") == 1
            resumed = await broker.resume(
                initial.subscription_id, expected_generation=initial.generation,
                session_id="redis-new", sink=new_sink, ctx={"verified": ALICE},
            )
            assert resumed.subscription_id == initial.subscription_id
            assert resumed.quota_lease.id == initial.quota_lease.id
            assert not await stores[1].owns(initial.quota_lease)
            assert await stores[1].owns(resumed.quota_lease)
            assert await broker.unsubscribe_session("redis-old") == 0

            publish = await broker.publish(
                channel="events", event={"ready": True}, origin_correlation_id="origin",
            )
            await asyncio.wait_for(resumed.queue.join(), 3)
            assert not old_sink.events and len(new_sink.events) == 1
            event, = broker.delivery_events()
            assert event["publication_id"] == publish.publication_id
            assert event["lease_id"] == resumed.quota_lease.id
            assert event["subscription_id"] == initial.subscription_id
            assert event["attachment_generation"] == resumed.generation
        finally:
            await broker.close()
    finally:
        await clients[0].delete(stores[0].key)
        await asyncio.gather(*(c.aclose() for c in clients))
