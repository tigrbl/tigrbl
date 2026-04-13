# Phase 7 Claims, Evidence, and Certification Promotion Checkpoint

Date: 2026-04-09
Scope: certification lifecycle and release-promotion governance
Checkpoint type: claim lifecycle, preserved evidence, and certification-bundle promotion

## What changed

The repo now carries a machine-readable claim lifecycle registry at `certification/claims/lifecycle.yaml`.

That lifecycle records:

- `draft`
- `mapped`
- `implemented`
- `tested`
- `evidenced`
- `certified`
- `recertify_required`

The lifecycle registry is applied to every public certification claim in the repo-owned certification tree, and advancement is blocked unless the claim records boundary inclusion, target mapping, owning modules, ADR link, public contract artifact, required test classes, preserved evidence, and release-gate coverage.

The promoted stable release `0.3.18` also now carries a signed certification bundle scaffold at `docs/conformance/releases/0.3.18/artifacts/certification-bundle.json` with preserved references for source archive digest, built artifacts, spec artifacts, target manifest, claims report, evidence manifest, ADR index, interop references, performance references, and provenance records.

## Release decision mapping

The certification bundle now records the explicit release-decision mapping:

- Gate A: surface freeze
- Gate B: correctness
- Gate C: interop
- Gate D: performance/operability
- Gate E: security/abuse

## Current truth

Stable `0.3.18` remains the only certifiable release boundary in this repository.

The active `0.3.19.dev1` line is still not certifiably fully featured.

The active `0.3.19.dev1` line is still not certifiably fully RFC compliant.
