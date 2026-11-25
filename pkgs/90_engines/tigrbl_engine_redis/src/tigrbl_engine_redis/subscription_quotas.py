"""Optional Redis quota provider; one atomic namespace transaction per operation."""

from __future__ import annotations
import json
import time
from uuid import uuid4
from tigrbl_ops_realtime.quotas import (
    SubscriptionAdmissionError,
    SubscriptionLease,
    quota_keys,
)


_TRANSACTION = r"""
local raw=redis.call('GET',KEYS[1])
local state=raw and cjson.decode(raw) or {leases={},buckets={}}
local t=redis.call('TIME');local now=tonumber(t[1])+tonumber(t[2])/1000000
local op=ARGV[1];local arg=cjson.decode(ARGV[2]);local ttl=tonumber(ARGV[3])
local count=0
for id,row in pairs(state.leases) do
 if row.expires<=now then state.leases[id]=nil else count=count+1 end
end
local buckets=0
for key,row in pairs(state.buckets) do
 if row.tokens+(now-row.updated)*row.rate>=row.burst then state.buckets[key]=nil else buckets=buckets+1 end
end
local result={ok=true}
if op=='acquire' then
 if count+buckets+3>arg.max_entries then return cjson.encode({error='subscription_admission_unavailable'}) end
 local updates={}
 for _,scope in ipairs({'user','tenant'}) do
  local rate=arg.rates[scope]
  if rate then
   local key=scope..':'..arg.keys[scope];local row=state.buckets[key]
   local tokens=row and math.min(rate.burst,row.tokens+math.max(0,now-row.updated)*rate.rate) or rate.burst
   if tokens<1 then return cjson.encode({error='subscription_rate_exceeded',scope=scope,retry_after=(1-tokens)/rate.rate}) end
   updates[key]={tokens=tokens-1,updated=now,rate=rate.rate,burst=rate.burst}
  end
 end
 for key,row in pairs(updates) do state.buckets[key]=row end
 for _,scope in ipairs({'user','tenant','operation'}) do
  local limit=arg.limits[scope]
  if limit then
   local active=0
   for _,row in pairs(state.leases) do if row.keys[scope]==arg.keys[scope] then active=active+1 end end
   if active>=limit then result={error='subscription_quota_exceeded',scope=scope,limit=limit};break end
  end
 end
 if not result.error then state.leases[arg.id]={generation=arg.generation,keys=arg.keys,expires=now+ttl} end
else
 local row=state.leases[arg.id]
 local owned=row and row.generation==arg.generation
 if op=='release' then
  if owned then state.leases[arg.id]=nil end
 elseif op=='owns' then result.owned=not not owned
 elseif not owned then result={error='subscription_admission_unavailable'}
 elseif op=='renew' then row.expires=now+ttl
 elseif op=='transfer' or op=='resume' then
  if op=='resume' then
   for _,scope in ipairs({'user','tenant','operation'}) do
    if row.keys[scope]~=arg.keys[scope] then return cjson.encode({error='subscription_identity_required'}) end
   end
   local updates={}
   for _,scope in ipairs({'user','tenant'}) do
    local rate=arg.rates[scope]
    if rate then
     local key=scope..':'..arg.keys[scope];local bucket=state.buckets[key]
     local tokens=bucket and math.min(rate.burst,bucket.tokens+math.max(0,now-bucket.updated)*rate.rate) or rate.burst
     if tokens<1 then return cjson.encode({error='subscription_rate_exceeded',scope=scope,retry_after=(1-tokens)/rate.rate}) end
     updates[key]={tokens=tokens-1,updated=now,rate=rate.rate,burst=rate.burst}
    end
   end
   for key,bucket in pairs(updates) do state.buckets[key]=bucket end
  end
  row.generation=arg.next_generation;row.expires=now+ttl
 else return redis.error_reply('invalid quota operation') end
end
-- Never expire a namespace while it has live leases or outstanding bucket debt.
local retention=ttl
for _,row in pairs(state.buckets) do retention=math.max(retention,(row.burst-row.tokens)/row.rate+1) end
redis.call('SET',KEYS[1],cjson.encode(state),'PX',math.ceil(retention*1000)+1000)
return cjson.encode(result)
"""


class RedisSubscriptionQuotaStore:
    scope = "deployment"

    def __init__(
        self,
        policy,
        *,
        client=None,
        url: str | None = None,
        namespace: str = "tigrbl:subscriptions",
        clock=time.monotonic,
    ):
        if (client is None) == (url is None) or url == "":
            raise ValueError("supply exactly one Redis client or URL")
        if not isinstance(namespace, str) or not namespace or len(namespace) > 128:
            raise ValueError("subscription namespace must be a bounded nonempty string")

        self.policy, self.clock = policy, clock
        self.key = "{" + namespace + "}:quota-state"
        self._owns_client = client is None
        if client is None:
            from redis.asyncio import Redis

            client = Redis.from_url(url, socket_connect_timeout=1, socket_timeout=1)
        self.client = client

    async def aclose(self) -> None:
        if self._owns_client:
            await self.client.aclose()

    async def _call(self, op, arg):
        try:
            value = await self.client.eval(
                _TRANSACTION,
                1,
                self.key,
                op,
                json.dumps(arg),
                self.policy.lease_ttl_seconds,
            )
            result = json.loads(value)
        except Exception as exc:
            raise SubscriptionAdmissionError(
                "subscription_admission_unavailable"
            ) from exc
        if "error" in result:
            raise SubscriptionAdmissionError(
                result["error"],
                result.get("scope", "service"),
                retry_after=result.get("retry_after"),
                limit=result.get("limit"),
            )
        return result

    def _deadline(self, start):
        return start + self.policy.lease_ttl_seconds * 0.9

    async def acquire(self, identity, operation, *, operation_limit=None):
        policy = self.policy
        start = self.clock()
        arg = {
            "keys": quota_keys(identity, operation),
            "id": uuid4().hex,
            "generation": uuid4().hex,
            "limits": {},
            "rates": {},
            "max_entries": policy.max_tracking_entries,
        }
        for scope in ("user", "tenant"):
            limit = getattr(policy, "max_active_per_" + scope)
            if limit is not None:
                arg["limits"][scope] = limit
            rate = getattr(policy, "open_rate_per_" + scope)
            if rate is not None:
                arg["rates"][scope] = {
                    "rate": rate,
                    "burst": getattr(policy, "open_burst_per_" + scope),
                }
        if operation_limit is not None:
            arg["limits"]["operation"] = operation_limit
        await self._call("acquire", arg)
        return SubscriptionLease(
            self, arg["id"], arg["generation"], self._deadline(start)
        )

    async def renew(self, lease_id, generation):
        start = self.clock()
        await self._call("renew", {"id": lease_id, "generation": generation})
        return self._deadline(start)

    async def release(self, lease_id, generation):
        await self._call("release", {"id": lease_id, "generation": generation})

    async def owns(self, lease):
        return (
            await self._call("owns", {"id": lease.id, "generation": lease.generation})
        )["owned"]

    async def transfer(self, lease_id, generation):
        start = self.clock()
        next_generation = uuid4().hex
        await self._call(
            "transfer",
            {
                "id": lease_id,
                "generation": generation,
                "next_generation": next_generation,
            },
        )
        return SubscriptionLease(self, lease_id, next_generation, self._deadline(start))

    async def resume(self, lease_id, generation, identity, operation):
        start = self.clock()
        next_generation = uuid4().hex
        rates = {}
        for scope in ("user", "tenant"):
            rate = getattr(self.policy, "open_rate_per_" + scope)
            if rate is not None:
                rates[scope] = {
                    "rate": rate,
                    "burst": getattr(self.policy, "open_burst_per_" + scope),
                }
        await self._call(
            "resume",
            {
                "id": lease_id,
                "generation": generation,
                "next_generation": next_generation,
                "keys": quota_keys(identity, operation),
                "rates": rates,
            },
        )
        return SubscriptionLease(self, lease_id, next_generation, self._deadline(start))
