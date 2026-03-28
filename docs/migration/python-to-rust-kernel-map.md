# Python → Rust kernel migration map

- `pkgs/core/tigrbl_kernel/tigrbl_kernel/_compile.py` → `crates/tigrbl_rs_kernel/src/compile.rs`
- `pkgs/core/tigrbl_kernel/tigrbl_kernel/_build.py` → `crates/tigrbl_rs_kernel/src/builder.rs`
- `pkgs/core/tigrbl_kernel/tigrbl_kernel/cache.py` → `crates/tigrbl_rs_kernel/src/cache.rs`
- `pkgs/core/tigrbl_kernel/tigrbl_kernel/labels.py` → `crates/tigrbl_rs_kernel/src/labels.rs`
- `pkgs/core/tigrbl_kernel/tigrbl_kernel/trace.py` → `crates/tigrbl_rs_kernel/src/trace.rs`
- `pkgs/core/tigrbl_kernel/tigrbl_kernel/models.py` → `crates/tigrbl_rs_kernel/src/plan/models.rs`
- `pkgs/core/tigrbl_kernel/tigrbl_kernel/opview_compiler.py` → `crates/tigrbl_rs_kernel/src/opview/compiler.rs`
