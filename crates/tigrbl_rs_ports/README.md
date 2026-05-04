![Tigrbl Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png)

<p align="center">
    <a href="https://crates.io/crates/tigrbl_rs_ports">
        <img src="https://img.shields.io/crates/d/tigrbl_rs_ports" alt="crates.io downloads for tigrbl_rs_ports"/></a>
    <a href="https://crates.io/crates/tigrbl_rs_ports">
        <img src="https://img.shields.io/crates/v/tigrbl_rs_ports?label=tigrbl_rs_ports&color=green" alt="crates.io version for tigrbl_rs_ports"/></a>
    <a href="https://docs.rs/tigrbl_rs_ports">
        <img src="https://img.shields.io/docsrs/tigrbl_rs_ports" alt="docs.rs documentation for tigrbl_rs_ports"/></a>
    <a href="https://crates.io/crates/tigrbl_rs_ports">
        <img src="https://img.shields.io/crates/l/tigrbl_rs_ports" alt="crates.io license metadata for tigrbl_rs_ports"/></a>
    <a href="https://hits.sh/github.com/tigrbl/tigrbl/tree/master/crates/tigrbl_rs_ports/">
        <img src="https://hits.sh/github.com/tigrbl/tigrbl/tree/master/crates/tigrbl_rs_ports.svg" alt="Repository views for tigrbl_rs_ports"/></a>
</p>

---

# tigrbl_rs_ports

**Use `tigrbl_rs_ports` in Rust: [open the crate on crates.io](https://crates.io/crates/tigrbl_rs_ports) or [inspect the crate source](https://github.com/tigrbl/tigrbl/tree/master/crates/tigrbl_rs_ports).**

Trait and envelope boundaries for Rust atoms, handlers, engines, and callbacks.

`tigrbl_rs_ports` is part of the Tigrbl Rust package graph. It documents crate-resident runtime, kernel, atom, port, operation, or engine behavior while cross-linking to the Python facade and sibling Rust crates.

## Crate ownership

- dependency-breaking traits for engines, sessions, transactions, handlers, callbacks, and runtime ports.
- Rust crates keep native execution contracts separate from Python authoring APIs while preserving compatibility with the Tigrbl specification and runtime model.

## Package ecosystem cross-links

Core cross-links:
- [`tigrbl`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl) - Facade package
- [`tigrbl_core`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_core) - Spec and primitive contracts
- [`tigrbl_canon`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_canon) - Canonical mapping and operation resolution
- [`tigrbl_runtime`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_runtime) - Phase lifecycle and execution runtime
- [`tigrbl_concrete`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_concrete) - Native objects, transports, hooks, deps, and secdeps
- [`tigrbl_ops_oltp`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_ops_oltp) - CRUD and transactional operation handlers
- [`tigrbl_ops_olap`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_ops_olap) - Analytical operation boundary
- [`tigrbl_ops_realtime`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_ops_realtime) - Stream, transfer, datagram, and realtime ops
- [`tigrbl_tests`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_tests) - Examples, benchmark, parity, and package test surfaces
Engine cross-links:
- [`tigrbl_engine_sqlite`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/engines/tigrbl_engine_sqlite) - SQLite local transactional engine
- [`tigrbl_engine_postgres`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/engines/tigrbl_engine_postgres) - PostgreSQL SQLAlchemy engine
- [`tigrbl_engine_inmemory`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/engines/tigrbl_engine_inmemory) - Process-local transactional in-memory engine
- [`tigrbl_engine_redis`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/engines/tigrbl_engine_redis) - Redis cache/database engine
- [`tigrbl_engine_duckdb`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/engines/tigrbl_engine_duckdb) - DuckDB analytical engine
- [`tigrbl_engine_pandas`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/engines/tigrbl_engine_pandas) - pandas DataFrame engine
- [`tigrbl_engine_pgsqli_wal`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/engines/tigrbl_engine_pgsqli_wal) - PostgreSQL and SQLite WAL engine
Rust cross-links:
- [`tigrbl_rs_spec`](https://github.com/tigrbl/tigrbl/tree/master/crates/tigrbl_rs_spec) - Rust IR and AppSpec model
- [`tigrbl_rs_atoms`](https://github.com/tigrbl/tigrbl/tree/master/crates/tigrbl_rs_atoms) - Rust atom catalog and phase algebra
- [`tigrbl_rs_kernel`](https://github.com/tigrbl/tigrbl/tree/master/crates/tigrbl_rs_kernel) - Rust compiler and plan optimizer
- [`tigrbl_rs_runtime`](https://github.com/tigrbl/tigrbl/tree/master/crates/tigrbl_rs_runtime) - Rust executor and callback fences
- [`tigrbl_rs_ports`](https://github.com/tigrbl/tigrbl/tree/master/crates/tigrbl_rs_ports) - Engine, session, transaction, callback, and handler ports

## Install

```toml
[dependencies]
tigrbl_rs_ports = "0.4.0-dev.2"
```

## Package discovery

Search and AI discovery terms for `tigrbl_rs_ports` include: Tigrbl, Rust, crate, runtime, kernel, atoms, ports, engines, operations, REST, JSON-RPC, schema-first APIs.

## Package-local entry point

This file is a package-local distribution entry point.
It is not the authoritative location for repository governance, current target status, current state reporting, certification claims, or release evidence.

## Canonical repository docs

- `README.md`
- `docs/README.md`
- `docs/conformance/CURRENT_TARGET.md`
- `docs/conformance/CURRENT_STATE.md`
- `docs/conformance/NEXT_STEPS.md`
- `docs/governance/DOC_POINTERS.md`
- `docs/developer/PACKAGE_CATALOG.md`
- `docs/developer/PACKAGE_LAYOUT.md`

## Package identity

- canonical repository: `https://github.com/tigrbl/tigrbl`
- organization: `https://github.com/tigrbl`
- social: `https://discord.gg/K4YTAPapjR`
- crate path: `https://github.com/tigrbl/tigrbl/tree/master/crates/tigrbl_rs_ports`
- workspace path: `crates/tigrbl_rs_ports`
- workspace class: Rust crate
- implementation layout: `src/`

Long-form repository documentation is governed from `docs/`.
