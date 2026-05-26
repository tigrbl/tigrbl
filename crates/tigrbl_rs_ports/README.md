<div align="center">
<h1>tigrbl_rs_ports</h1>
<img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png" alt="Tigrbl logo" width="140"/>
<p><strong>Trait and envelope boundaries for Rust atoms, handlers, engines, and callbacks.</strong></p>
<a href="https://crates.io/crates/tigrbl_rs_ports"><img src="https://img.shields.io/crates/v/tigrbl_rs_ports?label=crates.io" alt="crates.io version for tigrbl_rs_ports"/></a>
<a href="https://crates.io/crates/tigrbl_rs_ports"><img src="https://img.shields.io/crates/d/tigrbl_rs_ports" alt="Downloads for tigrbl_rs_ports"/></a>
<a href="https://docs.rs/tigrbl_rs_ports"><img src="https://img.shields.io/docsrs/tigrbl_rs_ports" alt="docs.rs status for tigrbl_rs_ports"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/crates/tigrbl_rs_ports/README.md"><img src="https://hits.sh/github.com/tigrbl/tigrbl/blob/master/crates/tigrbl_rs_ports/README.md.svg?label=hits" alt="Repository hits for tigrbl_rs_ports README"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="Cargo.toml"><img src="https://img.shields.io/badge/rust-1.81-93450a" alt="Rust requirement for tigrbl_rs_ports"/></a>
</div>

## Install

```toml
[dependencies]
tigrbl_rs_ports = "0.4.1"
```

```bash
cargo add tigrbl_rs_ports
```

## What It Owns

`tigrbl_rs_ports` owns the Rust-native ports boundary for the Tigrbl workspace. It keeps this native subsystem separately installable from the Python facade while staying aligned to the shared Tigrbl spec, runtime, and package graph.

## Use It When

Use `tigrbl_rs_ports` when you are building or embedding Rust-native Tigrbl components and want this subsystem directly instead of consuming it only through Python workspace packages.

## Public Surface

- Re-exported surface: `callbacks::{CallbackKind, CallbackPort, CallbackRef}`, `channel::{ChannelFamily, ChannelPort, ChannelSubevent, OpChannel}`, `engines::EnginePort`, `errors::{PortError, PortResult}`, `handlers::HandlerPort`, `sessions::SessionPort`.
- Module families: `atoms`, `callbacks`, `channel`, `engines`, `errors`, `handlers`, `sessions`, `transactions`, `values`.

## Internal Layout

- Workspace path: `crates/tigrbl_rs_ports`.
- Crate version line: `0.4.1` from the workspace package table.
- Direct crate dependencies: `tigrbl_rs_spec`.

## Related Packages

- [`tigrbl`](https://pypi.org/project/tigrbl/)
- [`tigrbl_rs_spec`](https://crates.io/crates/tigrbl_rs_spec)

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
