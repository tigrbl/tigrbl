# ADR-1004: ADR-0004 — Specification Merge Precedence

# ADR-0004 — Specification Merge Precedence

- **Status:** Proposed
- **Date:** 2026-04-14
- **Related ADRs:** ADR-0003, ADR-0006, ADR-0010, ADR-0011, ADR-0016, ADR-0017, ADR-0018, ADR-0019

## Context

Tigrbl composes behavior from defaults, package-level configuration, app-level declarations, decorators, and operation-local overrides.
Without an explicit merge lattice, 'spec-first' becomes ambiguous and different code paths can resolve the same declared intent differently.

## Decision

1. Specification merging is precedence-based and deterministic.
2. Precedence order is frozen as:
   a. framework hard defaults;
   b. package/module defaults;
   c. app/model defaults;
   d. decorator-declared values;
   e. operation-local explicit overrides;
   f. operator/environment overrides, but only for fields declared overridable.
3. Scalar fields resolve by highest-precedence non-unset value.
4. Mapping fields shallow-merge by key unless the field explicitly declares deep-merge semantics.
5. Sequence fields follow field-class rules:
   - `security_deps` and `deps`: concatenate in precedence order, then de-duplicate by stable identity;
   - `bindings`: concatenate in precedence order, then canonicalize and de-duplicate by normalized binding identity;
   - hooks/selectors: concatenate in precedence order, then preserve stable ordering.
6. Destructive clearing of inherited collections requires an explicit reset form; omission does not imply deletion.
7. Mutually exclusive values that cannot be reconciled fail closed and produce a specification error rather than a silent merge.

## Consequences

- Every code path resolves specifications the same way.
- Inheritance becomes predictable across apps, models, and operations.
- Binding and dependency lists remain composable without becoming order-random.
- Errors surface at spec resolution time instead of at runtime.
- This ADR provides the resolution lattice needed by decorator expansion and kernel compilation.

## Rejected alternatives

- Ad hoc field-by-field merge logic implemented independently in decorators, runtime, and compiler.
- Silent last-writer-wins for all fields.
- Implicit destructive clears based on omission.
