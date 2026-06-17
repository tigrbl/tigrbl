# Deprecated Rust Runtime Binding

Tigrbl runtime execution is Python-only.

Tests for Rust-named surfaces should assert deprecation behavior:

- availability checks return `False`;
- `Runtime(executor_backend="rust")` raises;
- `rust_handle()` and `execute_rust()` raise;
- Rust kernel/spec helpers raise;
- Rust atom, handler, and engine registration helpers raise.

Do not add tests that require a Rust compiler, Cargo workspace, native extension,
PyO3, maturin, or crates.io publication.
