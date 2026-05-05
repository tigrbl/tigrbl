![Tigrbl Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png)

<p align="center">
    <a href="https://pypi.org/project/tigrbl_engine_inmemory/">
        <img src="https://img.shields.io/pypi/dm/tigrbl_engine_inmemory" alt="PyPI downloads for tigrbl_engine_inmemory"/></a>
    <a href="https://hits.sh/github.com/tigrbl/tigrbl/tree/master/pkgs/engines/tigrbl_engine_inmemory/">
        <img src="https://hits.sh/github.com/tigrbl/tigrbl/tree/master/pkgs/engines/tigrbl_engine_inmemory.svg" alt="Repository views for tigrbl_engine_inmemory"/></a>
    <a href="https://pypi.org/project/tigrbl_engine_inmemory/">
        <img src="https://img.shields.io/pypi/pyversions/tigrbl_engine_inmemory" alt="Supported Python versions for tigrbl_engine_inmemory"/></a>
    <a href="https://pypi.org/project/tigrbl_engine_inmemory/">
        <img src="https://img.shields.io/pypi/l/tigrbl_engine_inmemory" alt="PyPI license metadata for tigrbl_engine_inmemory"/></a>
    <a href="https://pypi.org/project/tigrbl_engine_inmemory/">
        <img src="https://img.shields.io/pypi/v/tigrbl_engine_inmemory?label=tigrbl_engine_inmemory&color=green" alt="PyPI version for tigrbl_engine_inmemory"/></a>
</p>

---

<h1 align="center">Tigrbl engine-inmemory</h1>

**Install and inspect `tigrbl_engine_inmemory`: [download `tigrbl_engine_inmemory` from PyPI](https://pypi.org/project/tigrbl_engine_inmemory/) or [open the package source](https://github.com/tigrbl/tigrbl/tree/master/pkgs/engines/tigrbl_engine_inmemory).**

tigrbl_engine_inmemory is an in-memory database engine plugin for process-local transactional storage with copy-on-write snapshots for Tigrbl.

`tigrbl_engine_inmemory` is part of the Tigrbl package graph. It documents package-resident classes, concepts, extension points, and execution responsibilities while cross-linking to the facade, core specs, canonical mapping, runtime phases, concrete objects, operation packages, engine plugins, OpenAPI/OpenRPC documentation surfaces, and PyPI distributions that complete the system.

## Engine ownership and database guards

- Process-local transactional snapshots, copy-on-write behavior, test/development storage, and in-memory data guardrails.
- Engine packages document backend-specific connection settings, session construction, transaction behavior, persistence boundaries, and operational guardrails. Transport routing and operation semantics remain in the facade/canon/runtime/ops packages.
- Register this engine through the package entry point or the Tigrbl engine context so API code can select the backend without embedding backend-specific logic in model definitions.

## Package ecosystem cross-links

Every Tigrbl Python package links to its sibling distributions on PyPI so package indexes, search engines, answer engines, dependency scanners, and human readers can move through the installable package graph without falling back to source-tree paths.

Core packages:
- [`tigrbl`](https://pypi.org/project/tigrbl/) - Schema-first ASGI API framework for REST, JSON-RPC, OpenAPI, OpenRPC, SQLAlchemy models, typed validation, lifecycle hooks, and engine plugins.
- [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/) - Runtime atom utilities for Tigrbl planning, dispatch, transport ingress, egress, and high-throughput ASGI execution pipelines.
- [`tigrbl-base`](https://pypi.org/project/tigrbl-base/) - Abstract base interfaces for Tigrbl APIs, engines, providers, sessions, transports, and reusable runtime components.
- [`tigrbl-canon`](https://pypi.org/project/tigrbl-canon/) - Canonical mapping, routing, symbol resolution, and naming utilities for Tigrbl framework packages and generated API surfaces.
- [`tigrbl_client`](https://pypi.org/project/tigrbl_client/) - Typed Python client helpers for calling Tigrbl REST, JSON-RPC, OpenAPI, and generated schema-first API surfaces.
- [`tigrbl-concrete`](https://pypi.org/project/tigrbl-concrete/) - Concrete Tigrbl implementations for reusable framework behavior, sessions, routes, responses, and base abstraction adapters.
- [`tigrbl-core`](https://pypi.org/project/tigrbl-core/) - Core Tigrbl framework specifications, decorators, schemas, hooks, operations, and primitives for schema-first APIs.
- [`tigrbl-kernel`](https://pypi.org/project/tigrbl-kernel/) - Kernel orchestration for composing Tigrbl runtime plans, bindings, operation dispatch, and optimized ASGI execution.
- [`tigrbl-ops-olap`](https://pypi.org/project/tigrbl-ops-olap/) - Analytical OLAP operation boundaries for Tigrbl workloads, query-oriented APIs, and engine integrations.
- [`tigrbl-ops-oltp`](https://pypi.org/project/tigrbl-ops-oltp/) - Transactional OLTP operation handlers for Tigrbl CRUD, bulk, REST, JSON-RPC, and database-backed workloads.
- [`tigrbl-ops-realtime`](https://pypi.org/project/tigrbl-ops-realtime/) - Realtime, streaming, datagram, websocket, and event operation handlers for Tigrbl ASGI runtimes.
- [`tigrbl-orm`](https://pypi.org/project/tigrbl-orm/) - SQLAlchemy ORM tables, mixins, columns, model helpers, and persistence primitives for Tigrbl applications.
- [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/) - Runtime pipeline helpers and execution bridge surfaces for Tigrbl ASGI applications, transports, and operation dispatch.
- [`tigrbl_spec`](https://pypi.org/project/tigrbl_spec/) - Shared Tigrbl interfaces, protocol definitions, compatibility targets, and specification artifacts for framework integration.
- [`tigrbl_tests`](https://pypi.org/project/tigrbl_tests/) - Reusable Tigrbl pytest fixtures, conformance assertions, integration helpers, and package test utilities.
- [`tigrbl-typing`](https://pypi.org/project/tigrbl-typing/) - Typing protocols, aliases, generics, and shared type helpers for Tigrbl framework packages and extensions.

Engine packages:
- [`tigrbl_engine_bigquery`](https://pypi.org/project/tigrbl_engine_bigquery/) - BigQuery engine plugin for Google BigQuery warehouse sessions, analytics workloads, and Tigrbl engine registration.
- [`tigrbl_engine_clickhouse`](https://pypi.org/project/tigrbl_engine_clickhouse/) - ClickHouse engine plugin for analytical database sessions, warehouse workloads, and Tigrbl engine registration.
- [`tigrbl_engine_csv`](https://pypi.org/project/tigrbl_engine_csv/) - CSV engine plugin for file-backed tables, pandas DataFrames, and lightweight Tigrbl data workflows.
- [`tigrbl_engine_dataframe`](https://pypi.org/project/tigrbl_engine_dataframe/) - DataFrame engine plugin for transactional pandas sessions and in-process Tigrbl analytics workloads.
- [`tigrbl_engine_duckdb`](https://pypi.org/project/tigrbl_engine_duckdb/) - DuckDB engine plugin for embedded analytical database sessions, OLAP workloads, and Tigrbl engine registration.
- [`tigrbl_engine_inmemcache`](https://pypi.org/project/tigrbl_engine_inmemcache/) - In-memory cache engine plugin for process-local TTL, LRU, and fast Tigrbl cache workflows.
- [`tigrbl_engine_inmemory`](https://pypi.org/project/tigrbl_engine_inmemory/) (this package) - In-memory database engine plugin for process-local transactional storage, copy-on-write snapshots, and Tigrbl testing.
- [`tigrbl_engine_membloom`](https://pypi.org/project/tigrbl_engine_membloom/) - In-memory Bloom filter engine plugin for membership checks, rotating TTL windows, and Tigrbl API workflows.
- [`tigrbl_engine_memdedupe`](https://pypi.org/project/tigrbl_engine_memdedupe/) - In-memory dedupe engine plugin for idempotency tracking, duplicate suppression, and Tigrbl workflow coordination.
- [`tigrbl_engine_memkv`](https://pypi.org/project/tigrbl_engine_memkv/) - In-memory key-value engine plugin for process-local KV storage, cache workflows, and lightweight Tigrbl services.
- [`tigrbl_engine_memlru`](https://pypi.org/project/tigrbl_engine_memlru/) - In-memory LRU engine plugin for least-recently-used cache behavior and process-local Tigrbl data workflows.
- [`tigrbl_engine_mempubsub`](https://pypi.org/project/tigrbl_engine_mempubsub/) - In-memory pub/sub engine plugin for process-local publish-subscribe channels, events, and Tigrbl realtime workflows.
- [`tigrbl_engine_memqueue`](https://pypi.org/project/tigrbl_engine_memqueue/) - In-memory queue engine plugin for process-local tasks, message workflows, and Tigrbl runtime coordination.
- [`tigrbl_engine_memrate`](https://pypi.org/project/tigrbl_engine_memrate/) - In-memory rate-limit engine plugin for API quotas, counters, windows, and Tigrbl governance workflows.
- [`tigrbl_engine_numpy`](https://pypi.org/project/tigrbl_engine_numpy/) - NumPy engine plugin for array-to-table helpers, analytical workflows, and Tigrbl data integration.
- [`tigrbl_engine_pandas`](https://pypi.org/project/tigrbl_engine_pandas/) - Pandas engine plugin for transactional DataFrame sessions, tabular workflows, and Tigrbl data integration.
- [`tigrbl_engine_pgsqli_wal`](https://pypi.org/project/tigrbl_engine_pgsqli_wal/) - PostgreSQL and SQLite WAL engine plugin for transactional Tigrbl workflows and database-backed engine registration.
- [`tigrbl_engine_postgres`](https://pypi.org/project/tigrbl_engine_postgres/) - PostgreSQL engine plugin for SQLAlchemy sessions, async database workflows, and Tigrbl application persistence.
- [`tigrbl_engine_pyspark`](https://pypi.org/project/tigrbl_engine_pyspark/) - PySpark engine plugin for distributed DataFrame integration, analytics workloads, and Tigrbl data workflows.
- [`tigrbl_engine_redis`](https://pypi.org/project/tigrbl_engine_redis/) - Redis engine plugin for cache, data structures, and Tigrbl engine workflows backed by Redis.
- [`tigrbl_engine_rediscachethrough`](https://pypi.org/project/tigrbl_engine_rediscachethrough/) - Redis cache-through engine plugin for Redis, PostgreSQL, and Tigrbl data-access acceleration workflows.
- [`tigrbl_engine_snowflake`](https://pypi.org/project/tigrbl_engine_snowflake/) - Snowflake engine plugin for warehouse sessions, analytical workloads, and Tigrbl engine registration.
- [`tigrbl_engine_sqlite`](https://pypi.org/project/tigrbl_engine_sqlite/) - SQLite engine plugin for SQLAlchemy sessions, local transactional storage, and Tigrbl application persistence.
- [`tigrbl_engine_xlsx`](https://pypi.org/project/tigrbl_engine_xlsx/) - XLSX engine plugin for Excel workbook-backed tables, worksheet data access, and Tigrbl tabular workflows.

Application packages:
- [`tigrbl_acme_ca`](https://pypi.org/project/tigrbl_acme_ca/) - ACME v2 certificate authority app for Tigrbl tables, certificate automation, TLS workflows, and API surfaces.
- [`tigrbl_spiffe`](https://pypi.org/project/tigrbl_spiffe/) - SPIFFE and SPIRE identity app for Tigrbl with workload identity tables, UDS transport, and HTTP API surfaces.

Source-tree links remain available from each package identity section; this ecosystem section is intentionally PyPI-first for package discovery and installation routing.

## Install

```bash
pip install tigrbl_engine_inmemory
```

## Package discovery

`tigrbl_engine_inmemory` is described for package indexes, search engines, answer engines, and AI coding tools as: In-memory database engine plugin for process-local transactional storage, copy-on-write snapshots, and Tigrbl testing.

Use `tigrbl_engine_inmemory` when you need Tigrbl's schema-first ASGI package graph for REST APIs, JSON-RPC APIs, OpenAPI documentation, OpenRPC documentation, SQLAlchemy-backed models, Pydantic validation, typed operation specs, runtime dispatch, and installable engine or application extensions.

Discovery terms: tigrbl, ASGI, schema-first API framework, REST API, JSON-RPC API, OpenAPI documentation, OpenRPC documentation, SQLAlchemy models, Pydantic validation, typed validation, operation dispatch, engine plugins, api, json-rpc, rest, sqlalchemy, pydantic, engine, plugin, database, inmemory, transactions, snapshot, crud, openapi, openrpc, schema-first.

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
- package path: `https://github.com/tigrbl/tigrbl/tree/master/pkgs/engines/tigrbl_engine_inmemory`
- workspace path: `pkgs/engines/tigrbl_engine_inmemory`
- workspace class: engine package
- implementation layout: `src/tigrbl_engine_inmemory/`

Long-form repository documentation is governed from `docs/`.
