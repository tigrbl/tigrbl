# Evidence Index — 0.3.18.dev1

## Purpose

This index is the durable entry point for the current dev-bundle evidence lane model.

## Lane index

| Lane | Primary workflow/job | Gate-result summary |
|---|---|---|
| policy governance | `.github/workflows/policy-governance.yml#validate-policy` | `docs/conformance/dev/0.3.18.dev1/gate-results/policy-governance.md` |
| unit | `.github/workflows/evidence-lanes.yml#evidence-lane[unit]` | `docs/conformance/dev/0.3.18.dev1/gate-results/unit.md` |
| integration | `.github/workflows/evidence-lanes.yml#evidence-lane[integration]` | `docs/conformance/dev/0.3.18.dev1/gate-results/integration.md` |
| spec conformance | `.github/workflows/evidence-lanes.yml#evidence-lane[spec-conformance]` | `docs/conformance/dev/0.3.18.dev1/gate-results/spec-conformance.md` |
| security / negative | `.github/workflows/evidence-lanes.yml#evidence-lane[security-negative]` | `docs/conformance/dev/0.3.18.dev1/gate-results/security-negative.md` |
| docs UI smoke | `.github/workflows/evidence-lanes.yml#evidence-lane[docs-ui-smoke]` | `docs/conformance/dev/0.3.18.dev1/gate-results/docs-ui-smoke.md` |
| CLI smoke | `.github/workflows/evidence-lanes.yml#evidence-lane[cli-smoke]` | `docs/conformance/dev/0.3.18.dev1/gate-results/cli-smoke.md` |
| operator-surface smoke | `.github/workflows/evidence-lanes.yml#evidence-lane[operator-surface-smoke]` | `docs/conformance/dev/0.3.18.dev1/gate-results/operator-surface-smoke.md` |
| server compatibility smoke | `.github/workflows/evidence-lanes.yml#evidence-lane[server-compat-smoke]` | `docs/conformance/dev/0.3.18.dev1/gate-results/server-compat-smoke.md` |
| clean-room package tests | `.github/workflows/evidence-lanes.yml#evidence-lane[clean-room-package]` | `docs/conformance/dev/0.3.18.dev1/gate-results/clean-room-package.md` |
| installed-package smoke | `.github/workflows/gate-d-reproducibility.yml#gate-d-reproducibility` | `docs/conformance/dev/0.3.18.dev1/gate-results/installed-package-smoke.md` |
| docs/build verification | `.github/workflows/gate-d-reproducibility.yml#gate-d-reproducibility` | `docs/conformance/dev/0.3.18.dev1/gate-results/docs-build-verification.md` |

## Claim mapping source

- `docs/conformance/EVIDENCE_REGISTRY.json`


## Gate results

| Gate | Current result | Summary path |
|---|---|---|
| Gate A | passed | `docs/conformance/gates/GATE_A_BOUNDARY_FREEZE.md` |
| Gate B | passed in Gate B surface-closure checkpoint | `docs/conformance/dev/0.3.18.dev1/gate-results/gate-b-surface-closure.md` |
| Gate C | passed in Gate C conformance/security checkpoint | `docs/conformance/dev/0.3.18.dev1/gate-results/gate-c-conformance-security.md` |
| Gate D | passed in Gate D reproducibility checkpoint | `docs/conformance/dev/0.3.18.dev1/gate-results/gate-d-reproducibility.md` |
| Gate E | passed by Gate E promotion checkpoint | `docs/conformance/releases/0.3.18/gate-results/gate-e-promotion.md` |
