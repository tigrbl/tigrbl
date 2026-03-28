# Tigrbl UV Workspace

This workspace was extracted from `swarmauri-sdk-master.zip` and reorganized so that:
- core packages live under `pkgs/core`
- engine packages live under `pkgs/engines`
- remaining Tigrbl packages live directly under `pkgs`

The root `pyproject.toml` is configured for a uv workspace with packaging disabled.


## Rust-native additive workspace

This workspace now also contains an additive Rust-native substrate:

- `crates/` contains the Rust-native libraries for spec, ports, atoms, OLTP ops, kernel, runtime, and native engines.
- `bindings/python/tigrbl_native/` contains the Python-to-Rust bridge used to compile a spec once and hand off to the native runtime.
- the original Python packages under `pkgs/` remain intact and are not replaced.
