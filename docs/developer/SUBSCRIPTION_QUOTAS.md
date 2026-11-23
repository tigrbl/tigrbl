# Subscription admission

A subscription keeps delivering events after the initial subscribe call. For example,
one WebSocket can subscribe to orders and inventory, consuming two active slots.
Subscription limits control how many subscriptions a verified user or tenant can
keep open and how fast they can open new ones. Each admitted subscription holds a
lease. When a client resumes a subscription, the store transfers the lease to a
new owner generation so the old connection can no longer deliver events.

The default store keeps counts and leases in process. Tigrcorn's connection,
session, and stream limits apply independently.

```python
from tigrbl import TigrblApp
from tigrbl.subscriptions import SubscriptionIdentity, SubscriptionPolicy

def verified_identity(ctx):
    # Your authentication dependency establishes this trusted request state.
    principal = ctx.request.state.authenticated_principal
    return SubscriptionIdentity(
        principal.issuer, principal.subject, principal.authorized_tenant,
    )

app = TigrblApp(
    subscription_identity=verified_identity,
    subscription_policy=SubscriptionPolicy(
        max_active_per_user=10, max_active_per_tenant=200,
        open_rate_per_user=2, open_burst_per_user=5,
    ),
    subscription_operation_limits={"Orders.subscribe": 2},
)
```

Return `None` when verified authentication or tenant membership is absent. Payload IDs
never select quota identity. User quotas include issuer/principal and span connections
and IPs; tenant quotas aggregate members. Operation caps intersect aggregate caps.

## Configuration

Applications can build a policy in Python or call
`tigrbl.subscriptions.resolve_subscription_policy` and pass the resolved policy
to the app. For deployment-wide quotas, set `scope="deployment"` and inject a
store that implements `SubscriptionQuotaStore` through `subscription_store`.
The application owns the store's lifecycle.

The Redis adapter is supplied by `tigrbl_engine_redis`. Pass its URL or an
existing async Redis client directly to the adapter. Migrate older backend
settings such as `store`, `store_url_env`, and `namespace` from the policy to
application wiring. The policy now contains the quota limits and desired scope.

```python
import os
from contextlib import asynccontextmanager

from tigrbl_engine_redis import RedisSubscriptionQuotaStore

policy = SubscriptionPolicy(max_active_per_user=10, scope="deployment")
store = RedisSubscriptionQuotaStore(
    policy,
    url=os.environ["APP_SUBSCRIPTION_REDIS_URL"],
    namespace="orders:subscriptions",
)

@asynccontextmanager
async def lifespan(app):
    try:
        yield
    finally:
        await store.aclose()

app = TigrblApp(
    lifespan=lifespan,
    subscription_identity=verified_identity,
    subscription_policy=policy,
    subscription_store=store,
)
```

Set `subscription_resume_ttl` on the app to retain an attachment briefly after
disconnect. The broker retains the quota slot for at most that interval and
never beyond the current lease deadline. Resume rechecks the trusted identity,
consumes the opening-rate budget, and fences the old lease generation.

## Outcomes and cleanup

Quota exhaustion produces `subscription_quota_exceeded` (429); rate exhaustion produces
`subscription_rate_exceeded` with a retry delay; store failure produces
`subscription_admission_unavailable` (503). Persistent carriers use their existing
correlated error envelope and preserve other subscriptions.

Unsubscribe, delivery failure, disconnect, shutdown, and `broker.revoke_identity(identity)`
release active leases. Closing does not refund opening tokens. Delivery checks ownership
and deadline; failed renewal stops delivery. `broker.resume(...)` reauthorizes and moves
a locally hosted subscription without a second active slot. Shared stores provide fenced
transfer primitives; durable application-state replay after process loss is separate.
