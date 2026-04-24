# Rust conformance plan

## Objective

The Rust crates must ultimately satisfy the existing Python `tigrbl_tests` contract without changing the public Python authoring model.

## Certification lanes

### Lane 1: Python reference backend
The current Python implementation remains the behavioral oracle.

### Lane 2: Rust pure-Rust backend
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
- `RustBackendConfig`
- boundary trace readers and clearers
- `register_rust_atom`, `register_rust_hook`, `register_rust_handler`, `register_rust_engine`
- `build_rust_kernel`, `Runtime(executor_backend="rust")`
- `execution_backend=` on `TigrblApp` and `TigrblRouter`
- `Kernel(backend=...)`

## Test groups in this checkpoint

### Binding / FFI
- `pkgs/core/tigrbl_runtime/tests/test_rust_codec.py`
- `pkgs/core/tigrbl_tests/tests/rust/ffi/test_rust_binding_trace.py`

### Atom surface and callback fence registration
- `pkgs/core/tigrbl_tests/tests/rust/atoms/test_rust_atoms_public_surface.py`
- `crates/tigrbl_rs_atoms/tests/atom_contract.rs`

### Kernel surface
- `pkgs/core/tigrbl_tests/tests/rust/kernel/test_rust_kernel_public_surface.py`
- `crates/tigrbl_rs_kernel/tests/kernel_contract.rs`

### Runtime surface
- `pkgs/core/tigrbl_tests/tests/rust/runtime/test_rust_runtime_public_surface.py`
- `pkgs/core/tigrbl_runtime/tests/test_rust_runtime_demo_curl.py`
- `crates/tigrbl_rs_runtime/tests/runtime_contract.rs`

## Added in Rust parity closure

- differential snapshots between Python and Rust kernel plans via the shared
  parity-contract layer
- route/opview/phase-plan/packed-plan parity tests
- REST, JSON-RPC, SSE, WS/WSS, and WebTransport transport-trace parity tests
- fail-closed validation so Rust claim language is blocked ahead of parity
  evidence

## Still needed for full conformance

- full compiled-backend execution parity against the real Rust extension,
  not just the source-fallback/Rust parity contract
- hook lifecycle parity suites against the real rust runtime
- engine resolver parity tests
- error mapping parity tests against real transport/runtime execution
- OpenAPI/OpenRPC/AsyncAPI parity tests from the live Rust-backed docs path

The Rust backend remains non-claimable until the parity lanes pass as release evidence.
