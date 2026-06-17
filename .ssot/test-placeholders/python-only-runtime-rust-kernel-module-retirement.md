# Python-only runtime: Rust kernel module retirement

Planned unit coverage for the Python-only runtime retirement boundary.

Assertions:
- `tigrbl_kernel.rust_spec` is removed or emits an explicit deprecation/fail-closed signal.
- `tigrbl_kernel.rust_plan` is removed or emits an explicit deprecation/fail-closed signal.
- `tigrbl_kernel.rust_compile` is removed or emits an explicit deprecation/fail-closed signal.
- No supported public kernel API advertises Rust compiler or plan helpers.
