# ADR-0008 â€” Atom Catalog and Atom Legality

- **Status:** Proposed
- **Date:** 2026-04-14
- **Related ADRs:** ADR-0009, ADR-0010, ADR-0011, ADR-0012, ADR-0013, ADR-0016, ADR-0023, ADR-0024, ADR-0025

## Context

The kernel and runtime architecture already depend on a stable atom vocabulary. The registry pack and architecture notes enumerate structural atoms, handler atoms, and transport-related additions.
Without an ADR, atom growth can become ad hoc, undermining compilation, fusion, and reasoning.

## Decision

1. The atom catalog is a first-class architectural registry.
2. Atoms are the smallest named execution units that the kernel may compile, order, fuse, or guard.
3. Atoms are categorized by domain, at minimum:
   - ingress/dispatch;
   - dependency/guard;
   - handler;
   - persistence/transaction;
   - egress/transport;
   - error/rollback.
4. Every public or canonical atom must have:
   - stable name;
   - owning package;
   - declared phase legality;
   - barrier/fusibility classification;
   - test coverage.
5. New atoms may not be added solely as convenience shims if an existing atom or fused segment is the correct fit.
6. Transport growth must prefer small structural extensions over protocol-specific atom explosions.
7. Canonical handler atoms for default operations are part of the atom registry, not informal implementation details.

## Consequences

- Plan compilation has a stable target vocabulary.
- Fusion decisions can rely on explicit atom categories and barriers.
- Registry drift becomes visible.
- Missing canonical atoms become governance issues rather than latent bugs.

## Rejected alternatives

- Ad hoc unnamed execution steps.
- Runtime-only special cases with no atom representation.
- Protocol-specific atom trees for every transport surface.

