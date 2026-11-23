"""Authenticated logical-subscription admission, independent of transport streams."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass, fields
from typing import Protocol
import hashlib
import inspect
import math
import threading
import time
from uuid import uuid4


class SubscriptionAdmissionError(RuntimeError):
    def __init__(self, code, scope="service", *, retry_after=None, limit=None):
        self.code, self.scope, self.retry_after, self.limit = (
            code,
            scope,
            retry_after,
            limit,
        )
        self.status_code = 503 if code == "subscription_admission_unavailable" else 429
        if code == "subscription_identity_required":
            self.status_code = 403
        super().__init__(code)

    def detail(self):
        result = {"code": self.code, "scope": self.scope}
        if self.limit is not None:
            result["limit"] = self.limit
        if self.retry_after is not None:
            result["retry_after"] = self.retry_after
        return result


@dataclass(frozen=True)
class SubscriptionIdentity:
    issuer: str
    principal: str
    tenant: str

    def __post_init__(self):
        for value in (self.issuer, self.principal, self.tenant):
            if not isinstance(value, str) or not value.strip() or len(value) > 512:
                raise ValueError(
                    "verified subscription identity must contain bounded nonempty strings"
                )


@dataclass(frozen=True)
class SubscriptionPolicy:
    max_active_per_user: int | None = None
    max_active_per_tenant: int | None = None
    open_rate_per_user: float | None = None
    open_burst_per_user: int | None = None
    open_rate_per_tenant: float | None = None
    open_burst_per_tenant: int | None = None
    lease_ttl_seconds: float = 60
    lease_renewal_seconds: float = 20
    scope: str | None = None
    max_tracking_entries: int = 4096

    def __post_init__(self):
        for field in fields(self):
            name = field.name
            value = getattr(self, name)
            if value is None or name == "scope":
                continue
            integer = name.startswith("max_") or "_burst_" in name
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or value <= 0
                or (integer and not isinstance(value, int))
            ):
                raise ValueError(
                    f"subscriptions.{name} must be a finite positive "
                    + ("integer" if integer else "number")
                )
        for scope in ("user", "tenant"):
            if (getattr(self, "open_rate_per_" + scope) is None) != (
                getattr(self, "open_burst_per_" + scope) is None
            ):
                raise ValueError(
                    f"subscription {scope} opening rate and burst must be supplied together"
                )
        if self.lease_renewal_seconds >= self.lease_ttl_seconds / 2:
            raise ValueError(
                "subscription lease renewal must be less than half the TTL"
            )
        if self.scope not in {None, "process", "deployment"}:
            raise ValueError("invalid subscription scope")

    @property
    def enabled(self):
        return any(
            getattr(self, n) is not None
            for n in (
                "max_active_per_user",
                "max_active_per_tenant",
                "open_rate_per_user",
                "open_rate_per_tenant",
            )
        )

    @property
    def effective_scope(self):
        return self.scope or "process"


def _digest(value):
    import json

    return hashlib.sha256(json.dumps(value, separators=(",", ":")).encode()).hexdigest()


def quota_keys(identity, operation):
    return {
        "user": _digest((identity.issuer, identity.principal)),
        "tenant": _digest((identity.issuer, identity.tenant)),
        "operation": _digest((identity.issuer, identity.principal, operation)),
    }


class SubscriptionQuotaStore(Protocol):
    """Atomic quota and owner-generation operations required by admission."""

    policy: SubscriptionPolicy
    scope: str
    clock: Callable[[], float]

    async def acquire(
        self,
        identity: SubscriptionIdentity,
        operation: str,
        *,
        operation_limit: int | None = None,
    ) -> SubscriptionLease: ...
    async def renew(self, lease_id: str, generation: str) -> float: ...
    async def release(self, lease_id: str, generation: str) -> None: ...
    async def owns(self, lease: SubscriptionLease) -> bool: ...
    async def resume(
        self,
        lease_id: str,
        generation: str,
        identity: SubscriptionIdentity,
        operation: str,
    ) -> SubscriptionLease: ...


@dataclass
class SubscriptionLease:
    store: SubscriptionQuotaStore
    id: str
    generation: str
    deadline: float
    released: bool = False

    async def renew(self):
        self.deadline = await self.store.renew(self.id, self.generation)

    async def release(self):
        if not self.released:
            await self.store.release(self.id, self.generation)
            self.released = True

    def valid(self):
        return not self.released and self.store.clock() < self.deadline


class LocalSubscriptionQuotaStore:
    scope = "process"

    def __init__(self, policy, *, clock=time.monotonic):
        self.policy, self.clock = policy, clock
        self.lock = threading.RLock()
        self.leases = {}
        self.buckets = {}

    def _expire(self, now):
        for key, row in list(self.leases.items()):
            if row["expires"] <= now:
                self.leases.pop(key, None)
        for key, (tokens, updated, rate, burst) in list(self.buckets.items()):
            if min(burst, tokens + max(0, now - updated) * rate) >= burst:
                self.buckets.pop(key, None)

    async def acquire(self, identity, operation, *, operation_limit=None):
        keys = quota_keys(identity, operation)
        now = self.clock()
        policy = self.policy
        with self.lock:
            self._expire(now)
            if len(self.leases) + len(self.buckets) + 3 > policy.max_tracking_entries:
                raise SubscriptionAdmissionError("subscription_admission_unavailable")
            updates = {}
            for scope in ("user", "tenant"):
                rate = getattr(policy, "open_rate_per_" + scope)
                if rate is None:
                    continue
                burst = getattr(policy, "open_burst_per_" + scope)
                key = (scope, keys[scope])
                row = self.buckets.get(key)
                tokens = (
                    burst
                    if row is None
                    else min(burst, row[0] + max(0, now - row[1]) * rate)
                )
                if tokens < 1:
                    raise SubscriptionAdmissionError(
                        "subscription_rate_exceeded",
                        scope,
                        retry_after=(1 - tokens) / rate,
                    )
                updates[key] = (tokens - 1, now, rate, burst)
            self.buckets.update(updates)
            for scope, limit in [
                ("user", policy.max_active_per_user),
                ("tenant", policy.max_active_per_tenant),
                ("operation", operation_limit),
            ]:
                if (
                    limit is not None
                    and sum(
                        row["keys"][scope] == keys[scope]
                        for row in self.leases.values()
                    )
                    >= limit
                ):
                    raise SubscriptionAdmissionError(
                        "subscription_quota_exceeded", scope, limit=limit
                    )
            lease_id, generation = uuid4().hex, uuid4().hex
            deadline = now + policy.lease_ttl_seconds
            self.leases[lease_id] = {
                "generation": generation,
                "keys": keys,
                "expires": deadline,
            }
            return SubscriptionLease(self, lease_id, generation, deadline)

    async def renew(self, lease_id, generation):
        with self.lock:
            now = self.clock()
            self._expire(now)
            row = self.leases.get(lease_id)
            if row is None or row["generation"] != generation:
                raise SubscriptionAdmissionError("subscription_admission_unavailable")
            row["expires"] = now + self.policy.lease_ttl_seconds
            return row["expires"]

    async def release(self, lease_id, generation):
        with self.lock:
            row = self.leases.get(lease_id)
            if row and row["generation"] == generation:
                self.leases.pop(lease_id, None)

    async def transfer(self, lease_id, generation):
        """Authenticated callers must reauthorize before atomically fencing the old owner."""
        with self.lock:
            now = self.clock()
            self._expire(now)
            row = self.leases.get(lease_id)
            if row is None or row["generation"] != generation:
                raise SubscriptionAdmissionError("subscription_admission_unavailable")
            row["generation"] = uuid4().hex
            row["expires"] = now + self.policy.lease_ttl_seconds
            return SubscriptionLease(self, lease_id, row["generation"], row["expires"])

    async def owns(self, lease):
        with self.lock:
            row = self.leases.get(lease.id)
            return bool(
                row
                and row["generation"] == lease.generation
                and row["expires"] > self.clock()
            )

    async def resume(self, lease_id, generation, identity, operation):
        with self.lock:
            now = self.clock()
            self._expire(now)
            row = self.leases.get(lease_id)
            keys = quota_keys(identity, operation)
            if row is None or row["generation"] != generation or row["keys"] != keys:
                raise SubscriptionAdmissionError("subscription_admission_unavailable")
            updates = {}
            for scope in ("user", "tenant"):
                rate = getattr(self.policy, "open_rate_per_" + scope)
                if rate is None:
                    continue
                burst = getattr(self.policy, "open_burst_per_" + scope)
                key = (scope, keys[scope])
                bucket = self.buckets.get(key)
                tokens = (
                    burst
                    if bucket is None
                    else min(burst, bucket[0] + max(0, now - bucket[1]) * rate)
                )
                if tokens < 1:
                    raise SubscriptionAdmissionError(
                        "subscription_rate_exceeded",
                        scope,
                        retry_after=(1 - tokens) / rate,
                    )
                updates[key] = (tokens - 1, now, rate, burst)
            self.buckets.update(updates)
            return await self.transfer(lease_id, generation)


class SubscriptionAdmission:
    def __init__(
        self,
        policy,
        identity_resolver,
        *,
        store: SubscriptionQuotaStore | None = None,
        operation_limits=None,
    ):
        if not callable(identity_resolver):
            raise ValueError("subscription quotas require a trusted identity resolver")
        self.policy, self.identity_resolver = policy, identity_resolver
        if store is None:
            if policy.effective_scope != "process":
                raise ValueError(
                    "deployment subscription scope requires an injected quota store"
                )
            store = LocalSubscriptionQuotaStore(policy)
        if store.scope != policy.effective_scope:
            raise ValueError("quota provider scope does not match policy")
        if store.policy != policy:
            raise ValueError("quota provider policy does not match admission policy")
        self.store = store
        self.operation_limits = dict(operation_limits or {})
        for limit in self.operation_limits.values():
            if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
                raise ValueError(
                    "operation subscription caps must be positive integers"
                )

    async def identity(self, ctx):
        identity = self.identity_resolver(ctx)
        if inspect.isawaitable(identity):
            identity = await identity
        if not isinstance(identity, SubscriptionIdentity):
            raise SubscriptionAdmissionError(
                "subscription_identity_required", "identity"
            )
        return identity

    async def acquire(self, ctx, operation):
        identity = await self.identity(ctx)
        lease = await self.store.acquire(
            identity, operation, operation_limit=self.operation_limits.get(operation)
        )
        lease.identity = identity
        return lease

    async def resume(self, ctx, lease, operation):
        identity = await self.identity(ctx)
        if identity != getattr(lease, "identity", None):
            raise SubscriptionAdmissionError(
                "subscription_identity_required", "identity"
            )
        # Resume attempts consume the same opening-rate budgets without taking
        # another active slot. The store atomically fences the prior generation.
        replacement = await self.store.resume(
            lease.id, lease.generation, identity, operation
        )
        replacement.identity = identity
        return replacement

    def snapshot(self):
        return {
            "policy": asdict(self.policy),
            "scope": self.store.scope,
            "owner": "tigrbl",
            "enforced": True,
        }


async def fence_delivery(lease):
    if not lease.valid() or not await lease.store.owns(lease):
        raise SubscriptionAdmissionError("subscription_admission_unavailable")


__all__ = [
    "SubscriptionPolicy",
    "SubscriptionIdentity",
    "SubscriptionAdmission",
    "SubscriptionAdmissionError",
    "LocalSubscriptionQuotaStore",
    "SubscriptionQuotaStore",
    "SubscriptionLease",
    "quota_keys",
]
