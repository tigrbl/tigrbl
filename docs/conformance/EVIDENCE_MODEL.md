# Evidence Model

## Purpose

The repository treats certification evidence as a governed product surface rather than an ad hoc collection of audit logs.

## Evidence roots

The current program uses:

- claim rows in `docs/conformance/CLAIM_REGISTRY.md`
- machine-readable claim mapping in `docs/conformance/EVIDENCE_REGISTRY.json`
- a governed promotion-source dev bundle at `docs/conformance/dev/0.3.18.dev1/`
- a governed active next-line dev bundle scaffold at `docs/conformance/dev/0.3.19.dev1/`
- a historical stable scaffold at `docs/conformance/releases/0.3.17/`
- a governed promoted stable-release bundle at `docs/conformance/releases/0.3.18/`
- lane summaries under dev-bundle `gate-results/` directories
- release artifact manifests under the promoted release bundle `artifacts/` directory

## Reproducibility rule

A claim is not Tier 3 certifiable until:

1. the claim row exists in `docs/conformance/CLAIM_REGISTRY.md`
2. the claim row is mapped in `docs/conformance/EVIDENCE_REGISTRY.json`
3. the mapped tests, CI jobs, and artifact paths exist
4. the relevant bundle structure passes validation
5. Gate D and Gate E are passed on the exact chosen build/release

## Lifecycle rule

The repo-owned certification tree now carries a machine-readable claim lifecycle at `certification/claims/lifecycle.yaml`.

Lifecycle states are:

- `draft`
- `mapped`
- `implemented`
- `tested`
- `evidenced`
- `certified`
- `recertify_required`

A public certification claim cannot advance unless it records:

- boundary inclusion
- target mapping
- owning modules
- ADR link
- public contract artifact
- required test classes
- preserved evidence
- release-gate coverage

The current stable release bundle also preserves a certification-bundle artifact at `docs/conformance/releases/0.3.18/artifacts/certification-bundle.json`.

## Current checkpoint status

The frozen release history now records:

- Gate B proof on the frozen current-target surface
- Gate C conformance/security proof for the retained exact claim set
- Gate D reproducibility proof for `0.3.18.dev1`
- Gate E promotion and stable release proof for `0.3.18`

The active next-line dev bundle `0.3.19.dev1` now records only governed handoff and next-target planning evidence. It is not yet a Tier 3 certification bundle.

Within the declared current target boundary, the promoted stable release `0.3.18` retains the governed evidence required for the Tier 3 claim rows in `docs/conformance/CLAIM_REGISTRY.md`.
