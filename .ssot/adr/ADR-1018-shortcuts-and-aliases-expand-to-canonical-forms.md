# ADR-0018 â€” Shortcuts and Aliases Expand to Canonical Forms

- **Status:** Proposed
- **Date:** 2026-04-14
- **Related ADRs:** ADR-0003, ADR-0006, ADR-0007, ADR-0017, ADR-0019

## Context

Tigrbl needs shortcuts and aliases for usability, but shortcuts become dangerous when they express capabilities unavailable through the canonical surface or when they grow into independent feature trees.
This ADR keeps convenience aligned with declarative canon.

## Decision

1. A shortcut or alias is valid only if it expands deterministically into canonical forms.
2. Aliases may reduce boilerplate, but they may not create alias-only semantics.
3. Alias expansion must be inspectable and testable.
4. Aliases should parameterize canonical forms rather than multiply public API families unnecessarily.
5. Aliases that cannot be represented cleanly as canonical expansions must remain internal or be redesigned.
6. Public documentation must show the canonical expansion for every significant alias.

## Consequences

- Usability improves without creating a second layer of semantics.
- Refactoring remains easier because aliases point back to canonical forms.
- Docs and tooling can represent aliases as sugar rather than as separate concepts.
- This ADR directly supports the make/define/derive pattern.

## Rejected alternatives

- Alias-only capabilities.
- Large families of near-duplicate decorator APIs.
- Hidden expansion rules that only runtime code understands.

