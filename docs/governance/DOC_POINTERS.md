# Documentation and Pointer Map

## SSOT-First Reader Path

- `README.md`
- `.ssot/registry.json`
- `.ssot/adr/ADR-1060-docs-ci-non-authoritative-projections.yaml`
- `.ssot/specs/SPEC-1002-docs-ci-projection-authority-contract.yaml`
- `reports/current_state/2026-04-07-phase0-certification-freeze.md`
- `reports/certification_state/2026-04-07-registry-reclassification.md`
- `.ssot/reports/current_state/2026-04-09-phase5-tigrcorn-operator-surface.md`
- `.ssot/reports/certification_state/2026-04-09-phase5-tigrcorn-operator-surface.md`
- `.ssot/reports/current_state/2026-04-09-phase6-tigrcorn-hardening.md`
- `.ssot/reports/certification_state/2026-04-09-phase6-tigrcorn-hardening.md`
- `.ssot/reports/current_state/2026-04-09-phase7-claims-evidence-promotion.md`
- `.ssot/reports/certification_state/2026-04-09-phase7-claims-evidence-promotion.md`
- `docs/README.md`
- `docs/conformance/CURRENT_TARGET.md`
- `docs/conformance/CURRENT_STATE.md`
- `docs/conformance/NEXT_TARGETS.md`
- `docs/conformance/IMPLEMENTATION_MAP.md`
- `docs/conformance/NEXT_STEPS.md`
- `docs/conformance/dev/0.3.19.dev1/EVIDENCE_INDEX.md`
- `docs/conformance/releases/0.3.18/EVIDENCE_INDEX.md`
- `docs/governance/DOC_POINTERS.md`
- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `SECURITY.md`

## Projection Locations

Machine authority lives in `.ssot/registry.json`, `.ssot/adr/`, and `.ssot/specs/`. Documentation under `docs/` and validation tooling under `tools/ci/` are non-authoritative projection and validation surfaces. Certification YAML files under `certification/` are derived projections unless a row below explicitly says otherwise.

| Need | Canonical path |
|---|---|
| Certification authority | `.ssot/registry.json` |
| Next-target authority | `.ssot/registry.json` |
| Current claims | `.ssot/registry.json` |
| Target claims | `.ssot/registry.json` |
| Blocked claims | `.ssot/registry.json` |
| Claim lifecycle registry | `.ssot/registry.json` |
| Evidenced claims | `.ssot/registry.json` |
| Certification evidence schema | `certification/evidence/schema.json` |
| Current release certification profile | `certification/profiles/current_release.yaml` |
| Active dev-line certification profile | `certification/profiles/active_next_target.yaml` |
| Root ADR index | `.ssot/adr/ADR-1027-adr-index.yaml` |
| Certification truth-model ADR | `.ssot/adr/ADR-1026-certification-truth-model.yaml` |
| Certification truth-model spec | `.ssot/specs/SPEC-2002-certification-truth-model.yaml` |
| Docs and CI projection ADR | `.ssot/adr/ADR-1060-docs-ci-non-authoritative-projections.yaml` |
| Docs and CI projection contract | `.ssot/specs/SPEC-1002-docs-ci-projection-authority-contract.yaml` |
| Current-state report | `reports/current_state/2026-04-07-phase0-certification-freeze.md` |
| Certification-state report | `reports/certification_state/2026-04-07-registry-reclassification.md` |
| Declared-surface current-state report | `.ssot/reports/current_state/2026-04-07-phase1-declarative-surface.md` |
| Declared-surface certification-state report | `.ssot/reports/certification_state/2026-04-07-phase1-declarative-surface.md` |
| Rust parity current-state report | `.ssot/reports/current_state/2026-04-09-phase4-native-parity.md` |
| Rust parity certification-state report | `.ssot/reports/certification_state/2026-04-09-phase4-native-parity.md` |
| Tigrcorn operator-surface current-state report | `.ssot/reports/current_state/2026-04-09-phase5-tigrcorn-operator-surface.md` |
| Tigrcorn operator-surface certification-state report | `.ssot/reports/certification_state/2026-04-09-phase5-tigrcorn-operator-surface.md` |
| Tigrcorn hardening current-state report | `.ssot/reports/current_state/2026-04-09-phase6-tigrcorn-hardening.md` |
| Tigrcorn hardening certification-state report | `.ssot/reports/certification_state/2026-04-09-phase6-tigrcorn-hardening.md` |
| Claim-lifecycle current-state report | `.ssot/reports/current_state/2026-04-09-phase7-claims-evidence-promotion.md` |
| Claim-lifecycle certification-state report | `.ssot/reports/certification_state/2026-04-09-phase7-claims-evidence-promotion.md` |
| Target boundary | `docs/governance/TARGET_BOUNDARY.md` |
| Certification rules | `docs/governance/CERTIFICATION_POLICY.md` |
| Claim tiers | `docs/governance/CLAIM_TIERS.md` |
| Release policy | `docs/governance/RELEASE_POLICY.md` |
| Path-length policy | `docs/governance/PATH_LENGTH_POLICY.md` |
| Package structure policy | `docs/governance/PACKAGE_STRUCTURE_POLICY.md` |
| Current target | `docs/conformance/CURRENT_TARGET.md` |
| Current state | `docs/conformance/CURRENT_STATE.md` |
| Next targets | `docs/conformance/NEXT_TARGETS.md` |
| RFC security evidence map | `docs/conformance/RFC_SECURITY_EVIDENCE_MAP.md` |
| Evidence model | `docs/conformance/EVIDENCE_MODEL.md` |
| Evidence registry | `docs/conformance/EVIDENCE_REGISTRY.json` |
| Per-target implementation map | `docs/conformance/IMPLEMENTATION_MAP.md` |
| Next steps | `docs/conformance/NEXT_STEPS.md` |
| Claim registry | `docs/conformance/CLAIM_REGISTRY.md` |
| Gate model | `docs/conformance/GATE_MODEL.md` |
| Gate A freeze description | `docs/conformance/gates/GATE_A_BOUNDARY_FREEZE.md` |
| Gate A freeze manifest | `docs/conformance/gates/GATE_A_BOUNDARY_FREEZE_MANIFEST.json` |
| Gate A freeze marker | `docs/conformance/gates/TARGET_FREEZE_CURRENT_CYCLE.json` |
| Feature module audit evidence | `docs/conformance/audit/2026/phase3-current-state/` |
| Gate A boundary-freeze audit evidence | `docs/conformance/audit/2026/phase4-boundary-freeze/` |
| Spec/docs audit evidence | `docs/conformance/audit/2026/phase5-oas-jsonschema-jsonrpc-openrpc-closure/` |
| RFC/security audit evidence | `docs/conformance/audit/2026/p6-rfc-sec/` |
| Operator-surface audit evidence | `docs/conformance/audit/2026/phase7-operator-surface/` |
| CLI audit evidence | `docs/conformance/audit/2026/p8-cli/` |
| Evidence-model audit evidence | `docs/conformance/audit/2026/p9-evidence/` |
| Gate B audit evidence | `docs/conformance/audit/2026/p10-gate-b/` |
| Gate C audit evidence | `docs/conformance/audit/2026/p11-gate-c/` |
| Gate D audit evidence | `docs/conformance/audit/2026/p12-gate-d/` |
| Gate E audit evidence | `docs/conformance/audit/2026/p13-gate-e/` |
| Post-promotion handoff audit evidence | `docs/conformance/audit/2026/post-promotion-handoff/` |
| Active dev bundle | `docs/conformance/dev/0.3.19.dev1/` |
| Promotion-source dev bundle | `docs/conformance/dev/0.3.18.dev1/` |
| Current stable release bundle | `docs/conformance/releases/0.3.18/` |
| Historical stable release scaffold | `docs/conformance/releases/0.3.17/` |
| Package catalog | `docs/developer/PACKAGE_CATALOG.md` |
| Package layout | `docs/developer/PACKAGE_LAYOUT.md` |
| CI validation | `docs/developer/CI_VALIDATION.md` |
| CLI reference | `docs/developer/CLI_REFERENCE.md` |
| Tigrcorn example configs | `docs/developer/examples/tigrcorn/` |
| Tigrcorn operator profiles | `docs/developer/operator/profiles/` |
| Operator reference index | `docs/developer/operator/README.md` |
| Path-length validator | `tools/ci/validate_path_lengths.py` |
| CLI smoke workflow | `.github/workflows/cli-smoke.yml` |
| Evidence-lane workflow | `.github/workflows/evidence-lanes.yml` |
| Evidence-registry validator | `tools/ci/validate_evidence_registry.py` |
| Evidence-bundle validator | `tools/ci/validate_evidence_bundles.py` |
| Gate B surface-closure validator | `tools/ci/validate_gate_b_surface_closure.py` |
| Rust parity validator | `tools/ci/validate_phase4_rust_parity.py` |
| Tigrcorn operator-surface validator | `tools/ci/validate_phase5_tigrcorn_operator_surface.py` |
| Tigrcorn hardening validator | `tools/ci/validate_phase6_tigrcorn_hardening.py` |
| Claim-lifecycle validator | `tools/ci/validate_phase7_claim_lifecycle.py` |
| Gate B surface-closure workflow | `.github/workflows/gate-b-surface-closure.yml` |
| Gate C conformance/security validator | `tools/ci/validate_gate_c_conformance_security.py` |
| Gate C conformance/security workflow | `.github/workflows/gate-c-conformance-security.yml` |
| Gate D reproducibility validator | `tools/ci/validate_gate_d_reproducibility.py` |
| Gate D reproducibility workflow | `.github/workflows/gate-d-reproducibility.yml` |
| Gate E promotion validator | `tools/ci/validate_gate_e_promotion.py` |
| Gate E promotion workflow | `.github/workflows/gate-e-promotion.yml` |
| Post-promotion handoff validator | `tools/ci/validate_post_promotion_handoff.py` |
| Post-promotion handoff workflow | `.github/workflows/post-promotion-handoff.yml` |
| Release-note entry point | `docs/release-notes/README.md` |
| ADRs | `.ssot/adr/` |
| Developer guidance | `docs/developer/` |
| WIP notes | `docs/notes/wip/YYYY/` |
| Archived notes | `docs/notes/archive/YYYY/` |

## Authority-reset archive retained for traceability

| Previous root path | Archived path |
|---|---|
| `BUILD_PROOF.md` | `docs/conformance/archive/2026/phase0-authority-reset/legacy-rust-native-checkpoint/BUILD_PROOF.md` |
| `CURRENT_STATE.md` | `docs/conformance/archive/2026/phase0-authority-reset/legacy-rust-native-checkpoint/CURRENT_STATE.md` |
| `build_artifacts` | `docs/conformance/archive/2026/phase0-authority-reset/legacy-rust-native-checkpoint/build_artifacts` |
| `build_artifacts_manifest.txt` | `docs/conformance/archive/2026/phase0-authority-reset/legacy-rust-native-checkpoint/build_artifacts_manifest.txt` |
| `cargo_build_workspace_debug.log` | `docs/conformance/archive/2026/phase0-authority-reset/legacy-rust-native-checkpoint/cargo_build_workspace_debug.log` |
| `cargo_build_workspace_release.log` | `docs/conformance/archive/2026/phase0-authority-reset/legacy-rust-native-checkpoint/cargo_build_workspace_release.log` |
| `cargo_metadata.json` | `docs/conformance/archive/2026/phase0-authority-reset/legacy-rust-native-checkpoint/cargo_metadata.json` |
| `cargo_test_workspace.log` | `docs/conformance/archive/2026/phase0-authority-reset/legacy-rust-native-checkpoint/cargo_test_workspace.log` |
| `rust_tool_versions.txt` | `docs/conformance/archive/2026/phase0-authority-reset/legacy-rust-native-checkpoint/rust_tool_versions.txt` |
| `rustup_source_attempt.log` | `docs/conformance/archive/2026/phase0-authority-reset/legacy-rust-native-checkpoint/rustup_source_attempt.log` |

## Runtime/kernel transport archive retained for traceability

- `docs/notes/archive/2026/p2-struct-norm/`

## Post-promotion handoff archive retained for traceability

- `docs/notes/archive/2026/post-promotion-handoff/`

## Generated outputs removed from governed checkpoints

- `target/`
- `build/`
- `dist/`
