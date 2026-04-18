# Endpoint-Keyed JSON-RPC Bindings

Date: 2026-04-18
Kind: repo-local

## Intent

This document defines endpoint-keyed JSON-RPC binding identity for multiplexed ingress surfaces.

## Canonical model

- `HttpJsonRpcBindingSpec` includes `endpoint`
- `endpoint` identifies the logical multiplexed ingress surface for the binding
- the default endpoint value comes from a governed `tigrbl_core` constant
- app/router `mount_jsonrpc(...)` maps endpoint identity to concrete ingress paths
- kernel compilation resolves JSON-RPC ops by endpoint plus `rpc_method`

## Traceability

- ADRs:
  - `.ssot/adr/ADR-1046-endpoint-keyed-multiplexed-transport-bindings.md`
