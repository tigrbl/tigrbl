# ADR-0021 â€” Certification Boundary and Promotion Gates

- **Status:** Proposed
- **Date:** 2026-04-14
- **Related ADRs:** ADR-0007, ADR-0020, ADR-0022, ADR-0023, ADR-0024, ADR-0025

## Context

The architecture and registry bundle already point toward a certification program rather than an informal feature sprint.
If Tigrbl is going to make compatibility, protocol, or parity claims, the claim boundary and release gates need to be explicit.

## Decision

1. Tigrbl defines an explicit certification boundary for public claims.
2. Every claim must map to:
   - declared boundary inclusion;
   - owning code surfaces;
   - tests and evidence;
   - documentation.
3. Release promotion is gate-based. At minimum the gate set covers:
   - public surface freeze;
   - correctness;
   - interop/parity where applicable;
   - performance/operability where applicable;
   - security/abuse where applicable.
4. Claims that lack evidence remain non-certified regardless of implementation status.
5. Boundary expansion is an architectural event and requires explicit review.

## Consequences

- Public claims become governable.
- Feature work and certification work stop being conflated.
- Later interop and parity ADRs get a promotion framework.
- Release automation can treat claims as data rather than prose.

## Rejected alternatives

- Marketing-style feature claims with no evidence model.
- Manual one-off promotion decisions.
- Treating partial implementations as certified support.

