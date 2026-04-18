# ADR-1046 - Endpoint-Keyed Multiplexed Transport Bindings

- **Status:** Accepted
- **Date:** 2026-04-18
- **Related ADRs:** ADR-1006, ADR-1007, ADR-1014, ADR-1023

## Context

JSON-RPC is multiplexed: many operations share one concrete ingress such as `/rpc`. The binding model already treats transport support as op-centric metadata, but JSON-RPC currently lacks a first-class endpoint identity that can distinguish multiple mounted multiplexed surfaces without hard-coding concrete paths into every operation binding.

## Decision

1. Multiplexed transport bindings use a logical endpoint identity in addition to the protocol binding key.
2. `HttpJsonRpcBindingSpec` gains an `endpoint` field whose default value is the governed default endpoint constant from `tigrbl_core`.
3. Concrete mounts such as `mount_jsonrpc(prefix="/rpc", endpoint=...)` map endpoint identity to a concrete ingress path.
4. Stream, SSE, and websocket bindings remain path-based unless they later need multiplexed endpoint identity.
5. Endpoint defaults and default endpoint mappings are owned by `tigrbl_core` and exposed as uppercase double-underscore constants.

## Consequences

- JSON-RPC can support many mounted ingress surfaces without leaving the op-centric binding model
- endpoint routing stays declarative and kernel-visible
- concrete router/app mounts remain thin ingress adapters instead of becoming bespoke dispatchers

## Rejected alternatives

- encoding concrete `/rpc` paths directly into every JSON-RPC op binding
- letting app/router-local JSON-RPC handlers perform their own method lookup
- introducing a transport-specific route registry for multiplexed RPC ingress
