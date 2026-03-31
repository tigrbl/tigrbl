# Testing Guide

## Current baseline evidence retained from the supplied archive

The archived legacy build-proof package records these baseline validation actions:

- `cargo test --workspace --all-targets`
- selected Python native-surface pytest runs
- a concrete backend surface smoke that was skipped in the supplied container because `sqlalchemy` was not installed

See:

- `docs/conformance/archive/2026/phase0-authority-reset/legacy-rust-native-checkpoint/build_artifacts/rust_native_checkpoint_validation.md`
- `docs/testing/rust_native_conformance_plan.md`

## Guidance for contributors

When changing a public surface:

1. run the relevant Python tests in the affected package(s)
2. run relevant Rust crate tests when touching the native substrate
3. update conformance docs if the current-state or current-target interpretation changes
4. archive new build proof in the governed conformance tree rather than at the repository root
