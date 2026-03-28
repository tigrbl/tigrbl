# Current state of the Tigrbl Rust-native checkpoint

## Summary

This checkpoint keeps the original Python packages intact and adds an additive Rust-native substrate plus Python-facing backend shims.

The repository now includes:

- additive Rust crates under `crates/tigrbl_rs_*`
- additive Python bindings under `bindings/python/tigrbl_native`
- Python-facing backend selection and trace surfaces
- crate-level Rust contract tests for `tigrbl_rs_atoms`, `tigrbl_rs_kernel`, `tigrbl_rs_runtime`, and `tigrbl_rs_spec`
- Python contract tests under `pkgs/core/tigrbl_tests/tests/native/`
- a pure-Python `_native.py` fallback that keeps the binding surface importable from source and exposes FFI boundary tracing for tests

## Implemented in this checkpoint

### Public operator surfaces

- `tigrbl_native.ExecutionBackend`
- `tigrbl_native.NativeBackendConfig`
- `tigrbl_native.coerce_execution_backend(...)`
- `tigrbl_native.wants_native_backend(...)`
- `tigrbl_native.ffi_boundary_events()`
- `tigrbl_native.clear_ffi_boundary_events()`
- `tigrbl_atoms.register_native_atom(...)`
- `tigrbl_atoms.register_native_hook(...)`
- `tigrbl_atoms.register_native_callback(...)`
- `tigrbl_ops_oltp.register_native_handler(...)`
- `tigrbl_kernel.build_native_kernel(...)`
- `tigrbl_kernel.normalize_native_spec(...)`
- `tigrbl_runtime.build_native_runtime(...)`
- `tigrbl_runtime.native_boundary_events()`
- `tigrbl_runtime.clear_native_boundary_events()`
- `tigrbl_engine_inmemory.register_native_engine(...)`
- `TigrblApp(..., execution_backend=...)`
- `TigrblRouter(..., execution_backend=...)`
- `Kernel(backend=...)`

### Test scaffolding added

- `bindings/python/tigrbl_native/tests/test_fallback_boundary_trace.py`
- `pkgs/core/tigrbl_tests/tests/native/ffi/...`
- `pkgs/core/tigrbl_tests/tests/native/atoms/...`
- `pkgs/core/tigrbl_tests/tests/native/kernel/...`
- `pkgs/core/tigrbl_tests/tests/native/runtime/...`
- `pkgs/core/tigrbl_concrete/tests/test_execution_backend_surface.py`
- crate-level Rust tests under `crates/*/tests/`

### Rust-spec contract improvements

- `tigrbl_rs_spec::AppSpec` now carries `title`, `version`, `tables`, `jsonrpc_prefix`, and `system_prefix`
- `tigrbl_rs_spec::OpKind` now includes bulk variants and exposes `as_str()` / `is_bulk()`
- `tigrbl_rs_spec::HookPhase` now models transaction, handler, commit, response, and rollback phases
- `tigrbl_rs_atoms::AtomPhase` now exposes `ALL` / `all()`
- `tigrbl_rs_atoms::AtomRegistry` now exposes `try_register(...)`

## Still provisional

This checkpoint does **not** claim that the Rust-native backend now passes the full `tigrbl_tests` suite. The new code provides:

- public surface scaffolding
- boundary trace scaffolding
- additive contract tests
- spec and enum expansions that move the Rust crates closer to the Python contract

The Rust backend is still a partial backend substrate. Full parity work remains in:

- spec lowering fidelity
- packed kernel compilation parity
- hook lifecycle parity
- REST/RPC transport parity
- engine/session/transaction parity
- runtime result normalization parity
- Python callback fence execution inside the real Rust executor

## Recommended next milestones

1. Replace the pure-Python `_native.py` fallback with a real PyO3 extension module while keeping the same public API.
2. Extend `tigrbl_rs_spec` to match the Python `AppSpec`, `TableSpec`, `ColumnSpec`, `OpSpec`, `FieldSpec`, `IOSpec`, and binding contracts.
3. Make `tigrbl_rs_kernel` compile real route/opview/phase plans and snapshot them against the Python kernel.
4. Make `tigrbl_rs_runtime` execute compiled plans against the native engines and differential-test it against the Python runtime.
5. Turn the new native test tree into a lane within CI alongside the existing Python reference backend.
