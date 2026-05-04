![Tigrbl Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png)

<p align="center">
    <a href="https://pypi.org/project/tigrbl_spiffe/">
        <img src="https://img.shields.io/pypi/dm/tigrbl_spiffe" alt="PyPI downloads for tigrbl_spiffe"/></a>
    <a href="https://hits.sh/github.com/tigrbl/tigrbl/tree/master/pkgs/apps/tigrbl_spiffe/">
        <img src="https://hits.sh/github.com/tigrbl/tigrbl/tree/master/pkgs/apps/tigrbl_spiffe.svg" alt="Repository views for tigrbl_spiffe"/></a>
    <a href="https://pypi.org/project/tigrbl_spiffe/">
        <img src="https://img.shields.io/pypi/pyversions/tigrbl_spiffe" alt="Supported Python versions for tigrbl_spiffe"/></a>
    <a href="https://pypi.org/project/tigrbl_spiffe/">
        <img src="https://img.shields.io/pypi/l/tigrbl_spiffe" alt="PyPI license metadata for tigrbl_spiffe"/></a>
    <a href="https://pypi.org/project/tigrbl_spiffe/">
        <img src="https://img.shields.io/pypi/v/tigrbl_spiffe?label=tigrbl_spiffe&color=green" alt="PyPI version for tigrbl_spiffe"/></a>
</p>

---

# Tigrbl spiffe

**Install and inspect `tigrbl_spiffe`: [download `tigrbl_spiffe` from PyPI](https://pypi.org/project/tigrbl_spiffe/) or [open the package source](https://github.com/tigrbl/tigrbl/tree/master/pkgs/apps/tigrbl_spiffe).**

tigrbl_spiffe is a SPIFFE application package for SPIFFE and SPIRE identity surfaces for Tigrbl with table-centric UDS and HTTP transports.

`tigrbl_spiffe` is part of the Tigrbl package graph. It documents package-resident classes, concepts, extension points, and execution responsibilities while cross-linking to the facade, core specs, canonical mapping, runtime phases, concrete objects, operation packages, engine plugins, and Rust crates that complete the system.

## Application package ownership

- SPIFFE/SPIRE identity surfaces, workload identity tables, UDS/HTTP transport context, and security automation package context.
- Application packages document domain-specific tables and operations while linking back to Tigrbl facade, concrete security objects, specs, runtime, and engines for the underlying API mechanics.

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

```bash
pip install tigrbl_spiffe
```

## Package discovery

Search and AI discovery terms for `tigrbl_spiffe` include: tigrbl, ASGI, REST, JSON-RPC, SQLAlchemy, Pydantic, asgi, api, json-rpc, rest, sqlalchemy, pydantic, identity, security, spiffe, spire.

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
- package path: `https://github.com/tigrbl/tigrbl/tree/master/pkgs/apps/tigrbl_spiffe`
- workspace path: `pkgs/apps/tigrbl_spiffe`
- workspace class: application package
- implementation layout: `src/tigrbl_spiffe/`

Long-form repository documentation is governed from `docs/`.
