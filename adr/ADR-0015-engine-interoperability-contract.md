# ADR-0015 — Engine Interoperability Contract

- **Status:** Proposed
- **Date:** 2026-04-14
- **Related ADRs:** ADR-0002, ADR-0012, ADR-0013, ADR-0014, ADR-0016

## Context

Tigrbl needs a stable contract between canonical operations and engine implementations.
Without an explicit contract, canonical ops either become engine-specific or silently depend on capabilities that only some engines provide.

## Decision

1. Engines integrate with Tigrbl through an explicit capability contract.
2. The initial contract is centered on canonical OLTP semantics and includes capability declaration for:
   - identity/addressing;
   - reads and writes;
   - predicates/filters;
   - sorting and pagination where applicable;
   - bulk semantics;
   - merge/replace semantics;
   - transaction support;
   - consistency/locking behavior where relevant.
3. Canonical operations compile against declared capabilities, not engine-specific APIs.
4. Unsupported capability requests fail explicitly rather than degrading silently.
5. Engine adapters must document capability differences and error behavior.
6. Later engine classes may extend this contract, but they may not redefine the meaning of canonical OLTP operations.

## Consequences

- Engines become swappable at the semantic boundary rather than only at the storage-client boundary.
- Plan compilation can specialize against declared capability sets.
- Engine-specific logic stays in adapters instead of leaking into handlers and bindings.
- Tests can target engine conformance rather than per-engine folklore.

## Rejected alternatives

- Letting handlers call engine-specific APIs directly as the primary integration style.
- Implicitly assuming every engine supports the full canonical contract.
- Encoding engine behavior into bindings or transport adapters.
