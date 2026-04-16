# ADR-0013 â€” Default Canonical OLTP Ops

- **Status:** Proposed
- **Date:** 2026-04-14
- **Related ADRs:** ADR-0008, ADR-0012, ADR-0014, ADR-0015, ADR-0016

## Context

Tigrbl needs a frozen baseline of canonical OLTP operations so that specs, bindings, handler atoms, engines, docs, and parity work all have the same semantic target.
The architecture pack already points to several missing canonical handler atoms; this ADR defines the baseline canon.

## Decision

1. The default canonical OLTP operation set is frozen as:
   - `create`
   - `read`
   - `list`
   - `update`
   - `replace`
   - `merge`
   - `delete`
   - `clear`
   - `bulk_create`
   - `bulk_update`
   - `bulk_replace`
   - `bulk_merge`
   - `bulk_delete`
   - `count`
   - `exists`
2. These operations are canonical framework verbs, not app-specific custom verbs.
3. Each canonical operation requires:
   - spec-level representation;
   - canonical handler atom;
   - engine capability mapping;
   - docs projection behavior;
   - binding parity where applicable.
4. OLAP and realtime verbs are not part of the default OLTP canon and must be governed separately.
5. Custom operations remain valid, but they do not redefine the meaning of canonical OLTP verbs.

## Consequences

- Core semantics stop drifting between bindings and engines.
- Missing canonical handlers become clearly in-scope implementation work.
- REST and JSON-RPC parity becomes tractable because both target the same canon.
- The canon stays compact instead of absorbing every useful verb in the system.

## Rejected alternatives

- Leaving the canonical OLTP set informal.
- Treating count/exists as optional conveniences.
- Mixing OLTP, OLAP, and realtime verbs into one undifferentiated default canon.

