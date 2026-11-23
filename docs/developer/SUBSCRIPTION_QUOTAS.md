# Subscription admission

Tigrbl limits logical subscriptions. The server separately limits connections,
protocol sessions, transport streams, and opening rates. Many subscriptions may share
one WebSocket or WebTransport control stream; each broker registration consumes a slot.

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
to the app. Put Redis credentials in the environment variable named by the policy.

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
