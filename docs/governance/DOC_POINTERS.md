# Documentation and Pointer Map

## Canonical top-level reader path

- `README.md`
- `docs/README.md`
- `docs/conformance/CURRENT_TARGET.md`
- `docs/conformance/CURRENT_STATE.md`
- `docs/conformance/NEXT_STEPS.md`
- `docs/governance/DOC_POINTERS.md`
- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `SECURITY.md`

## Canonical docs locations

| Need | Canonical path |
|---|---|
| Target boundary | `docs/governance/TARGET_BOUNDARY.md` |
| Certification rules | `docs/governance/CERTIFICATION_POLICY.md` |
| Claim tiers | `docs/governance/CLAIM_TIERS.md` |
| Current target | `docs/conformance/CURRENT_TARGET.md` |
| Current state | `docs/conformance/CURRENT_STATE.md` |
| Next steps | `docs/conformance/NEXT_STEPS.md` |
| Claim registry | `docs/conformance/CLAIM_REGISTRY.md` |
| Gate model | `docs/conformance/GATE_MODEL.md` |
| ADRs | `docs/adr/` |
| Developer guidance | `docs/developer/` |
| WIP notes | `docs/notes/wip/YYYY/` |
| Archived notes | `docs/notes/archive/YYYY/` |

## Legacy root materials archived during Phase 0

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

## Generated outputs removed from root checkpoint

- `target/` removed from the distributable checkpoint because it is generated build output
