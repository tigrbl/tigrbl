# Python → Rust runtime migration map

- `pkgs/core/tigrbl_runtime/tigrbl_runtime/executors/phase.py` → `crates/tigrbl_rs_runtime/src/executor/phase.rs`
- `pkgs/core/tigrbl_runtime/tigrbl_runtime/executors/packed.py` → `crates/tigrbl_rs_runtime/src/executor/packed.rs`
- `pkgs/core/tigrbl_runtime/tigrbl_runtime/executors/invoke.py` → `crates/tigrbl_rs_runtime/src/executor/invoke.rs`
- `pkgs/core/tigrbl_runtime/tigrbl_runtime/runtime/runtime.py` → `crates/tigrbl_rs_runtime/src/runtime.rs`
- `pkgs/core/tigrbl_runtime/tigrbl_runtime/runtime/response.py` → `crates/tigrbl_rs_runtime/src/response.rs`
- `pkgs/core/tigrbl_runtime/tigrbl_runtime/runtime/status/*` → `crates/tigrbl_rs_runtime/src/status.rs`
