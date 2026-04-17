# ADR-1031: AppSpec, Harness, and Uvicorn Projections Preserve Canonical Outcomes

- **Status:** Proposed
- **Date:** 2026-04-16
- **Related ADRs:** ADR-0005, ADR-0006, ADR-0014, ADR-0015, ADR-0016, ADR-0022, ADR-0023, ADR-0024, ADR-0025

## Context

The current failing slice in `pkgs/core/tigrbl_tests/tests` shows that AppSpec-driven assembly, imperative harness assembly, kernel bootstrap, and Uvicorn-backed REST / JSON-RPC execution are drifting apart. The failures are not isolated smoke regressions; they indicate that multiple construction paths are no longer preserving the same compiled semantic outcome.

The active architecture already commits Tigrbl to one semantic op model, one compiled-plan substrate, and REST / JSON-RPC parity. This ADR tightens those commitments for AppSpec materialization, harness execution, engine resolution, and Uvicorn-backed end-to-end execution.

## Decision

1. AppSpec materialization and imperative app/router assembly must compile to the same canonical kernel-plan shape for the same declared semantic surface.
2. Kernel bootstrap and plan priming are idempotent compilation steps. Re-priming may reuse cached artifacts, but it may not alter semantic routing, opview identity, or transport-visible behavior.
3. Harness paths are conformance entrypoints, not alternate runtimes. Test harness execution must consume the same compiled plan and projection rules as production Uvicorn-backed execution.
4. Uvicorn-backed REST and JSON-RPC execution must project one canonical operation result. Transport adapters may shape envelopes, headers, and status codes, but they may not invent divergent success or failure semantics.
5. JSON-RPC requests that carry an `id` must return a JSON-RPC response body. `204 No Content` is reserved for notification semantics and may not be emitted for ordinary request / response RPC calls.
6. Engine resolver precedence, multi-table resolution, router-prefix application, and mounted RPC-prefix behavior must be decided before transport projection and then shared by both REST and JSON-RPC paths.
7. Multi-table and multi-router Uvicorn scenarios are treated as first-class conformance lanes because they exercise the same canonical resolver and projection contract under realistic mounting and prefix behavior.

## Consequences

- AppSpec, harness, and imperative assembly failures are treated as compiled-plan parity regressions rather than as isolated transport bugs.
- Uvicorn end-to-end tests become governance evidence for runtime projection correctness, especially where REST and JSON-RPC are expected to agree.
- Engine resolver and multi-table routing behavior must remain transport-agnostic up to the final projection step.
- Empty-body RPC responses for ordinary request / response execution become explicitly out of contract.

## Rejected alternatives

- Treating AppSpec or harness execution as a looser, test-only approximation of the runtime contract.
- Allowing Uvicorn-backed JSON-RPC execution to return transport-level success without a JSON-RPC response body for ordinary calls.
- Letting engine resolver precedence or mounted-prefix behavior diverge between REST and JSON-RPC entrypaths.
