# Optional Rust runtime binding

Tigrbl's Rust concern is limited to the optional runtime binding package.

The binding surface may expose:

- `ExecutionBackend`
- `RustBackendConfig`
- Rust binding availability checks
- FFI boundary event readers and clearers
- callback registration helpers
- `build_rust_kernel`
- `normalize_rust_spec`
- `Runtime(executor_backend="rust")`

The repo does not maintain any broader Rust certification program. Rust work
outside this optional runtime binding package is out of scope for
`tigrbl/tigrbl`.

Tests for this surface should verify that the optional binding can be imported,
compiled, and invoked when present, and that Python callers retain a clear
failure mode when the binding is unavailable.
