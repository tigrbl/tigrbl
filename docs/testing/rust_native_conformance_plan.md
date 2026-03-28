# Rust-native conformance plan

## Objective

The Rust-native crates must ultimately satisfy the existing Python `tigrbl_tests` contract without changing the public Python authoring model.

## Certification lanes

### Lane 1: Python reference backend
The current Python implementation remains the behavioral oracle.

### Lane 2: Rust pure-native backend
A request enters Python once, crosses into Rust, executes through Rust atoms + Rust kernel + Rust runtime + Rust engine, and returns to Python once for response emission.

### Lane 3: Rust mixed backend
The same Rust pipeline is used, but Python callbacks are allowed at explicit fences only.

## Boundary invariants

- request entry crosses once
- response exit crosses once
- no mid-request Python fallback is allowed unless a Python callback fence is declared
- Python hooks, handlers, atoms, and engines are optimization barriers

## Contract surfaces now present in the repo

- `ExecutionBackend`
- `NativeBackendConfig`
- boundary trace readers and clearers
- `register_native_atom`, `register_native_hook`, `register_native_handler`, `register_native_engine`
- `build_native_kernel`, `build_native_runtime`
- `execution_backend=` on `TigrblApp` and `TigrblRouter`
- `Kernel(backend=...)`

## Test groups in this checkpoint

### Binding / FFI
- `bindings/python/tigrbl_native/tests/test_fallback_boundary_trace.py`
- `pkgs/core/tigrbl_tests/tests/native/ffi/test_native_binding_trace.py`

### Atom surface and callback fence registration
- `pkgs/core/tigrbl_tests/tests/native/atoms/test_native_atoms_public_surface.py`
- `crates/tigrbl_rs_atoms/tests/atom_contract.rs`

### Kernel surface
- `pkgs/core/tigrbl_tests/tests/native/kernel/test_native_kernel_public_surface.py`
- `crates/tigrbl_rs_kernel/tests/kernel_contract.rs`

### Runtime surface
- `pkgs/core/tigrbl_tests/tests/native/runtime/test_native_runtime_public_surface.py`
- `crates/tigrbl_rs_runtime/tests/runtime_contract.rs`

## Still needed for full conformance

- differential snapshots between Python and Rust kernel plans
- route/opview/schema parity tests
- REST/RPC CRUD parity suites against the Rust runtime
- hook lifecycle parity suites against the Rust runtime
- engine resolver parity tests
- error mapping parity tests
- OpenAPI/OpenRPC parity tests
