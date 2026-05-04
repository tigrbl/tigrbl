![Tigrbl Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png)

<p align="center">
    <a href="https://pypi.org/project/tigrbl-core/">
        <img src="https://img.shields.io/pypi/dm/tigrbl-core" alt="PyPI downloads for tigrbl-core"/></a>
    <a href="https://hits.sh/github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_core/">
        <img src="https://hits.sh/github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_core.svg" alt="Repository views for tigrbl-core"/></a>
    <a href="https://pypi.org/project/tigrbl-core/">
        <img src="https://img.shields.io/pypi/pyversions/tigrbl-core" alt="Supported Python versions for tigrbl-core"/></a>
    <a href="https://pypi.org/project/tigrbl-core/">
        <img src="https://img.shields.io/pypi/l/tigrbl-core" alt="PyPI license metadata for tigrbl-core"/></a>
    <a href="https://pypi.org/project/tigrbl-core/">
        <img src="https://img.shields.io/pypi/v/tigrbl-core?label=tigrbl-core&color=green" alt="PyPI version for tigrbl-core"/></a>
</p>

---

# Tigrbl core

**Author durable specs: [inspect `tigrbl_core` spec classes](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_core/tigrbl_core/_spec).**

tigrbl-core is a core framework package for core specifications, decorators, schemas, hooks, and primitives for the Tigrbl framework.

`tigrbl-core` is part of the Tigrbl package graph. It documents package-resident classes, concepts, extension points, and execution responsibilities while cross-linking to the facade, core specs, canonical mapping, runtime phases, concrete objects, operation packages, engine plugins, and Rust crates that complete the system.

## Resident concepts

- `tigrbl_core` owns typed specification primitives: `AppSpec`, `TableSpec`, `OpSpec`, `HookSpec`, `EngineSpec`, `BindingSpec`, `RequestSpec`, `ResponseSpec`, schema specs, storage specs, middleware specs, and semantic datatype contracts.
- This is where operation metadata, `secdeps`, dependency-bearing op specifications, REST/JSON-RPC binding specs, schema generation contracts, and OpenAPI/OpenRPC-compatible type surfaces should be documented.
- Use this package when you need the portable model of what an operation, hook, engine, table, binding, request, or response means before it is mapped into concrete runtime objects.

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
pip install tigrbl-core
```

## Package discovery

Search and AI discovery terms for `tigrbl-core` include: tigrbl, ASGI, REST, JSON-RPC, SQLAlchemy, Pydantic, asgi, api, json-rpc, rest, sqlalchemy, pydantic, core, decorators, schema, hooks.

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
- package path: `https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_core`
- workspace path: `pkgs/core/tigrbl_core`
- workspace class: core Python package
- implementation layout: `tigrbl_core/`

Long-form repository documentation is governed from `docs/`.
