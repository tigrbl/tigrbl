# ADR-0016 — Kernel Plan Compilation, Packing, Fusion, and Compaction

- **Status:** Proposed
- **Date:** 2026-04-14
- **Related ADRs:** ADR-0002, ADR-0003, ADR-0004, ADR-0008, ADR-0009, ADR-0011, ADR-0012, ADR-0015, ADR-0020, ADR-0023, ADR-0024, ADR-0025

## Context

The architecture pack already treats Tigrbl as a compiled-plan system rather than a purely interpreted request dispatcher.
This ADR freezes that direction early because it shapes specs, atoms, phases, performance, and future runtime normalization.

## Decision

1. Tigrbl compiles canonical specs into static kernel plans.
2. The compiled plan model includes:
   - route/program selection;
   - phase-owned segment lists;
   - atom injection;
   - barrier-aware fusion;
   - interning and packing of repeated structures.
3. The kernel should compile once and reuse hot plans rather than rebuilding chains per invocation.
4. Fusion is allowed only across legal, side-effect-compatible atoms; transaction, handler, guard, and transport barriers remain explicit.
5. Deforestation is a first-class optimization goal: avoid transient envelopes and per-invocation structural allocation where a packed plan or scratch-slot representation suffices.
6. Plan shape is an architectural contract and must be mirrored in any parity backend.

## Consequences

- Specs become meaningful as compiler inputs rather than just metadata.
- Performance work stays aligned with semantics and legality.
- The repo gets a consistent story for packing, segmentization, and optimization.
- Later runtime ADRs can consume a stable compiled-plan substrate instead of inventing a second execution model.

## Rejected alternatives

- Purely interpreted per-invocation chain assembly.
- Transport-specific dispatch pipelines with no common compiled substrate.
- Unbounded atom proliferation without packing/fusion rules.
