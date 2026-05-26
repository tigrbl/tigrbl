<div align="center">
<h1>tigrbl_rs_runtime</h1>
<img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png" alt="Tigrbl logo" width="140"/>
<p><strong>Rust runtime and executor for compiled Tigrbl kernel plans.</strong></p>
<a href="https://crates.io/crates/tigrbl_rs_runtime"><img src="https://img.shields.io/crates/v/tigrbl_rs_runtime?label=crates.io" alt="crates.io version for tigrbl_rs_runtime"/></a>
<a href="https://crates.io/crates/tigrbl_rs_runtime"><img src="https://img.shields.io/crates/d/tigrbl_rs_runtime" alt="Downloads for tigrbl_rs_runtime"/></a>
<a href="https://docs.rs/tigrbl_rs_runtime"><img src="https://img.shields.io/docsrs/tigrbl_rs_runtime" alt="docs.rs status for tigrbl_rs_runtime"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/crates/tigrbl_rs_runtime/README.md"><img src="https://hits.sh/github.com/tigrbl/tigrbl/blob/master/crates/tigrbl_rs_runtime/README.md.svg?label=hits" alt="Repository hits for tigrbl_rs_runtime README"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="Cargo.toml"><img src="https://img.shields.io/badge/rust-1.81-93450a" alt="Rust requirement for tigrbl_rs_runtime"/></a>
</div>

## Install

```toml
[dependencies]
tigrbl_rs_runtime = "0.4.1"
```

```bash
cargo add tigrbl_rs_runtime
```

## What It Owns

`tigrbl_rs_runtime` owns the Rust-native runtime boundary for the Tigrbl workspace. It keeps this native subsystem separately installable from the Python facade while staying aligned to the shared Tigrbl spec, runtime, and package graph.

## Use It When

Use `tigrbl_rs_runtime` when you are building or embedding Rust-native Tigrbl components and want this subsystem directly instead of consuming it only through Python workspace packages.

## Public Surface

- Re-exported surface: `config::RuntimeConfig`, `handle::runtime_handle::RuntimeHandle`, `parity::{build_transport_trace, TransportTraceEvent}`, `runtime::RustRuntime`.
- Module families: `callback`, `channel`, `config`, `engine`, `executor`, `handle`, `metrics`, `parity`, `request`, `response`, `runtime`, `status`.

## Internal Layout

- Workspace path: `crates/tigrbl_rs_runtime`.
- Crate version line: `0.4.1` from the workspace package table.
- Direct crate dependencies: `tigrbl_rs_atoms`, `tigrbl_rs_engine_inmemory`, `tigrbl_rs_engine_postgres`, `tigrbl_rs_engine_sqlite`, `tigrbl_rs_kernel`, `tigrbl_rs_ops_oltp`, `tigrbl_rs_ports`, `tigrbl_rs_spec`.

## Related Packages

- [`tigrbl`](https://pypi.org/project/tigrbl/)
- [`tigrbl_rs_atoms`](https://crates.io/crates/tigrbl_rs_atoms)
- [`tigrbl_rs_engine_inmemory`](https://crates.io/crates/tigrbl_rs_engine_inmemory)
- [`tigrbl_rs_engine_postgres`](https://crates.io/crates/tigrbl_rs_engine_postgres)
- [`tigrbl_rs_engine_sqlite`](https://crates.io/crates/tigrbl_rs_engine_sqlite)
- [`tigrbl_rs_kernel`](https://crates.io/crates/tigrbl_rs_kernel)
- [`tigrbl_rs_ops_oltp`](https://crates.io/crates/tigrbl_rs_ops_oltp)
- [`tigrbl_rs_ports`](https://crates.io/crates/tigrbl_rs_ports)

## Canonical Repository Docs

- `docs/README.md`
- `docs/conformance/CURRENT_TARGET.md`
- `docs/conformance/CURRENT_STATE.md`
- `docs/conformance/NEXT_STEPS.md`
- `docs/governance/DOC_POINTERS.md`
- `docs/developer/PACKAGE_CATALOG.md`
- `docs/developer/PACKAGE_LAYOUT.md`

## Package-local Boundary

This file is a package-local distribution entry point.
Use this page for crate installation and boundary orientation. Repository governance, conformance state, target status, and release evidence remain governed from `docs/` and `.ssot/`.

## License

Licensed under the Apache License, Version 2.0. See `LICENSE` and the official [Apache 2.0 license text](https://www.apache.org/licenses/LICENSE-2.0).
