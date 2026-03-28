# Rust-native checkpoint validation

## Commands executed

### Rust workspace
`cargo test --workspace --all-targets`

Result: passed.

See: `build_artifacts/cargo_test_workspace_after_checkpoint.log`

### Python native surface tests
`python -m pytest -q bindings/python/tigrbl_native/tests/test_fallback_boundary_trace.py pkgs/core/tigrbl_tests/tests/native/ffi/test_native_binding_trace.py pkgs/core/tigrbl_tests/tests/native/atoms/test_native_atoms_public_surface.py pkgs/core/tigrbl_tests/tests/native/kernel/test_native_kernel_public_surface.py pkgs/core/tigrbl_tests/tests/native/runtime/test_native_runtime_public_surface.py --noconftest`

Result: 5 passed.

See: `build_artifacts/pytest_native_surface.log`

### Concrete backend surface smoke
`python -m pytest -q pkgs/core/tigrbl_concrete/tests/test_execution_backend_surface.py`

Result: skipped in this container because `sqlalchemy` is not installed.

See: `build_artifacts/pytest_execution_backend_surface.log`

## Interpretation

This checkpoint validates the additive backend surfaces, boundary-trace scaffolding, and Rust crate contract tests.
It does **not** prove full `tigrbl_tests` parity for the Rust-native backend yet.
For the current state and the remaining gaps, read `CURRENT_STATE.md` and `docs/testing/rust_native_conformance_plan.md`.
