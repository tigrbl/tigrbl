# Gate E: Promotion

## Objective

Promote an exact dev build to a stable release with synchronized evidence, claims, and frozen release artifacts.

## Status

Passed in the Gate E promotion checkpoint.

## Exact promotion identity

- chosen dev build: `0.3.18.dev1`
- promoted stable release: `0.3.18`
- source dev bundle: `docs/conformance/dev/0.3.18.dev1/`
- stable release bundle: `docs/conformance/releases/0.3.18/`
- promoted facade package metadata path: `pkgs/core/tigrbl/pyproject.toml`

## What Gate E proves now

- the promotion gate is verified against the exact chosen dev build `0.3.18.dev1`
- the stable release bundle `0.3.18` is frozen and synchronized
- the facade package version is promoted from `0.3.18.dev1` to `0.3.18`
- release notes, claims, evidence index, current-target snapshot, gate results, and artifact manifests agree on the promoted release identity
- README and governed documentation pointers now point to the new current stable release bundle
- the current-boundary Tier 3 claim rows are now available for the promoted release and remain bounded by `docs/governance/TARGET_BOUNDARY.md`

## Primary proof surfaces

- `tools/ci/validate_gate_e_promotion.py`
- `tools/ci/tests/test_gate_e_promotion.py`
- `.github/workflows/gate-e-promotion.yml`
- `docs/conformance/releases/0.3.18/RELEASE_NOTES.md`
- `docs/conformance/releases/0.3.18/CLAIMS.md`
- `docs/conformance/releases/0.3.18/EVIDENCE_INDEX.md`
- `docs/conformance/releases/0.3.18/CURRENT_TARGET_SNAPSHOT.md`
- `docs/conformance/releases/0.3.18/gate-results/gate-e-promotion.md`
- `docs/conformance/releases/0.3.18/artifacts/artifact-manifest.json`
- `docs/conformance/audit/2026/p13-gate-e/README.md`

## Certification wording unlocked by this gate

Within the declared current target boundary only, the promoted release may now be described as:

- certifiably fully featured
- certifiably fully RFC/spec/standard compliant
