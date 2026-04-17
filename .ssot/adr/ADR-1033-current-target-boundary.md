# ADR-1033: Current target boundary

﻿
Accepted.

## Context

The repository needs an explicit line between framework-owned semantics and server/runtime-owned transport behavior.

## Decision

Treat application/API/auth semantics and framework-owned docs/operator surfaces as in-boundary. Treat HTTP/2, HTTP/3, QUIC, HPACK, QPACK, and server-side TLS termination as outside the current framework boundary.

## Consequences

Certification claims must be scoped to the documented boundary only.
