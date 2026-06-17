# Python-only runtime: Rust executor rejection

Planned unit coverage for backend selection after Rust parity retirement.

Assertions:
- `Runtime(executor_backend="rust")` is rejected or deprecated with a clear unsupported-runtime error.
- App/runtime configuration no longer treats `EXECUTION_BACKEND = "rust"` as supported.
- Python runtime backend selection remains valid.
