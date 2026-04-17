# ADR-1032: Status, Auth, and Error Projections Derive from Canonical Outcomes

- **Status:** Proposed
- **Date:** 2026-04-16
- **Related ADRs:** ADR-0011, ADR-0013, ADR-0014, ADR-0015, ADR-0016, ADR-0023, ADR-0025

## Context

The currently failing `tigrbl_tests` slice also shows drift in anonymous-access handling, REST create status codes, authn / authorization behavior, error parity, validation parity, and response-structure expectations. These failures all point to the same problem: transport-facing success and failure projections are no longer being derived consistently from one canonical semantic outcome.

Tigrbl already commits to protocol parity and compiled semantic ownership. This ADR makes the projection rules explicit for create outcomes, anonymous access, validation failures, authorization failures, and response-envelope structure.

## Decision

1. Canonical operation outcomes are transport-neutral until the final projection step. REST status codes, JSON-RPC envelopes, and error shapes must be derived from that shared result.
2. Canonical create success projects to REST `201 Created` unless an explicit operation contract states otherwise.
3. Anonymous-access eligibility is resolved from canonical dependency and security metadata before transport projection. Runtime behavior and generated documentation must reflect the same allow-anon decision.
4. Validation, authorization, and handler failures must map to one canonical error classification before REST or JSON-RPC shaping occurs.
5. REST and JSON-RPC error parity tests are contract tests. A failure in one transport path implies a semantic projection defect unless explicitly documented otherwise.
6. Response-structure tests for error envelopes are blocking conformance checks because malformed envelopes break client behavior even when transport-level status codes appear successful.
7. Success responses may not silently downgrade to transport-only success states that erase semantic information needed by clients, including create metadata and RPC result payloads.

## Consequences

- Create endpoints that return `200 OK` where the contract expects `201 Created` are treated as semantic projection drift.
- Anonymous-access and authn failures must be debugged against canonical security metadata first, not against route-local shortcuts.
- Error parity and response-structure mismatches become transport-projection defects with shared ownership across REST and JSON-RPC execution paths.
- Documentation and runtime behavior must stay aligned on anon-access and error-shape expectations.

## Rejected alternatives

- Treating REST status codes as handler-local choices independent of canonical semantic outcomes.
- Allowing anonymous-access behavior to diverge from documented security metadata.
- Accepting different validation or authorization semantics between REST and JSON-RPC for the same canonical operation.
