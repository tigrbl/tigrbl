# Core Default Endpoint Mappings

Date: 2026-04-18
Kind: repo-local

## Intent

This document defines the authority and naming rules for default endpoint mappings used by multiplexed transport bindings.

## Rules

- default endpoint identities and default endpoint mapping values live in `tigrbl_core`
- exported constants use uppercase names with double-underscore prefix and suffix
- JSON-RPC bindings and concrete mounts source their default endpoint from the same core constant
- default endpoint mappings are declarative inputs to binding materialization and kernel compilation

## Traceability

- ADRs:
  - `.ssot/adr/ADR-1046-endpoint-keyed-multiplexed-transport-bindings.md`
