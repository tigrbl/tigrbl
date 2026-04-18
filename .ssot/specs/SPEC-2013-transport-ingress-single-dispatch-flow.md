# Transport Ingress Single Dispatch Flow

Date: 2026-04-18
Kind: repo-local

## Intent

This document defines the next-target transport ingress flow for the transport-dispatch track.

## Canonical flow

- concrete app/router transport surfaces may receive HTTP, JSON-RPC, stream, SSE, and websocket ingress
- those concrete surfaces normalize transport input into the gateway envelope and attached context metadata
- runtime compiles or loads the `KernelPlan` and invokes the configured executor
- the executor ships the envelope and context through the compiled plan
- the `KernelPlan` and atoms perform lookup, matching, binding resolution, parse/reduce/effect behavior, and response selection

## Non-goals

- app-local HTTP route matching
- router-local JSON-RPC method dispatch
- executor-owned transport lookup

## Traceability

- ADRs:
  - `.ssot/adr/ADR-1045-transport-dispatch-track-boundary-and-sequencing.md`
  - `.ssot/adr/ADR-1047-kernelplan-owned-transport-dispatch.md`
