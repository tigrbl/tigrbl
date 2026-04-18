# Binding-Driven REST and JSON-RPC Materialization

Date: 2026-04-18
Kind: repo-local

## Intent

This document defines how REST and JSON-RPC ingress surfaces materialize from op-centric binding declarations on the active transport-dispatch track.

## Materialization rules

- `HttpRestBindingSpec` is the sole source for REST method/path materialization
- `HttpJsonRpcBindingSpec` is the sole source for JSON-RPC ingress eligibility
- concrete app/router mounts install ingress adapters, not semantic dispatchers
- concrete materialization does not replace or bypass kernel-owned lookup and matching
- parity between REST and JSON-RPC is preserved at the semantic layer rather than by duplicating route logic

## Traceability

- ADRs:
  - `.ssot/adr/ADR-1046-endpoint-keyed-multiplexed-transport-bindings.md`
  - `.ssot/adr/ADR-1047-kernelplan-owned-transport-dispatch.md`
