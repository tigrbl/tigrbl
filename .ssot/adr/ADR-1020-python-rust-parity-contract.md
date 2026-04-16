# ADR-0020 â€” Python / Rust Parity Contract

- **Status:** Proposed
- **Date:** 2026-04-14
- **Related ADRs:** ADR-0002, ADR-0003, ADR-0016, ADR-0021, ADR-0022, ADR-0023, ADR-0024, ADR-0025

## Context

The architecture pack treats Rust as a real mirror target for specs, atoms, kernel, runtime, and ops, not as an ornamental acceleration layer.
That only works if parity is defined as a contract with evidence requirements.

## Decision

1. Python and Rust implementations target semantic parity, not vague feature similarity.
2. Parity scope includes:
   - spec representation and normalization;
   - canonical operation semantics;
   - atom vocabulary where mirrored;
   - compiled plan shape where mirrored;
   - binding behavior where mirrored;
   - runtime-visible results and error behavior where mirrored.
3. Claims of Rust/native support are forbidden until parity evidence exists.
4. Differential tests, snapshot artifacts, and plan-shape comparisons are required for parity claims.
5. Temporary gaps are allowed only if they are explicitly documented as non-parity surfaces.

## Consequences

- Native acceleration work stays honest.
- Public claims about backend availability become evidence-based.
- The repo avoids permanent semantic drift between Python and Rust.
- Later certification work gets a measurable parity target instead of a narrative claim.

## Rejected alternatives

- Calling Rust 'supported' because crates exist.
- Best-effort mirroring with no differential evidence.
- Treating semantic mismatches as acceptable implementation detail.

