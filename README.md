<div align="center">
<h1>Tigrbl Workspace</h1>
<img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png" alt="Tigrbl logo" width="220"/>
<p><strong>Schema-first Python workspace for REST APIs, JSON-RPC APIs, typed contracts, runtime pipelines, engine plugins, and optional Rust runtime bindings.</strong></p>
<a href="https://github.com/tigrbl/tigrbl"><img src="https://img.shields.io/badge/repo-tigrbl%2Ftigrbl-1f6feb" alt="Repository for tigrbl"/></a>
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/branch-coverage.yml"><img src="https://github.com/tigrbl/tigrbl/actions/workflows/branch-coverage.yml/badge.svg?branch=master" alt="Branch coverage workflow"/></a>
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml"><img src="https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml/badge.svg" alt="Publish workflow"/></a>
<a href="https://hits.sh/github.com/tigrbl/tigrbl.svg"><img src="https://hits.sh/github.com/tigrbl/tigrbl.svg" alt="Repository hits for tigrbl"/></a>
<a href="https://github.com/Tigrbl/tigrbl/blob/master/.ssot/registry.json"><img src="https://img.shields.io/badge/SSOT-governed-2f6f4e.svg" alt="SSOT governed workspace"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-3776ab" alt="Python versions 3.10 | 3.11 | 3.12 | 3.13 | 3.14 for Tigrbl workspace"/></a>
<a href="https://discord.gg/K4YTAPapjR"><img src="https://img.shields.io/badge/Discord-Join%20chat-5865F2?logo=discord&logoColor=white" alt="Discord community for tigrbl"/></a>
</div>

![Tigrbl package graph](docs/assets/tigrbl-package-graph.png)

## What This Repository Owns

Tigrbl is a Python workspace for schema-first service authoring and execution. The repository owns the public facade, split framework layers, installable engine plugins, and an optional Rust runtime binding package under `pkgs/core/tigrbl_runtime`. Active workspace manifests currently define Python packages only; Rust concerns in this repo are limited to the optional runtime binding.

## Install and Work on the Workspace

```bash
uv sync --all-extras --dev
```

Most users start with [`tigrbl`](https://pypi.org/project/tigrbl/) for the public Python facade. This root README is the repository and workspace entry point; the PyPI-facing facade package README lives at [`pkgs/core/tigrbl/README.md`](pkgs/core/tigrbl/README.md). Package-level README entry points under `pkgs/` document the boundary, install target, and dependency surface for each distributable.

## Package Families

### Core Python packages

- [`tigrbl`](https://pypi.org/project/tigrbl/)
- [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/)
- [`tigrbl-base`](https://pypi.org/project/tigrbl-base/)
- [`tigrbl-canon`](https://pypi.org/project/tigrbl-canon/)
- [`tigrbl_client`](https://pypi.org/project/tigrbl_client/)
- [`tigrbl-concrete`](https://pypi.org/project/tigrbl-concrete/)
- [`tigrbl-core`](https://pypi.org/project/tigrbl-core/)
- [`tigrbl-kernel`](https://pypi.org/project/tigrbl-kernel/)
- [`tigrbl-ops-olap`](https://pypi.org/project/tigrbl-ops-olap/)
- [`tigrbl-ops-oltp`](https://pypi.org/project/tigrbl-ops-oltp/)
- [`tigrbl-ops-realtime`](https://pypi.org/project/tigrbl-ops-realtime/)
- [`tigrbl-orm`](https://pypi.org/project/tigrbl-orm/)
- [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/)
- [`tigrbl_spec`](https://pypi.org/project/tigrbl_spec/)
- [`tigrbl_tests`](https://pypi.org/project/tigrbl_tests/)
- [`tigrbl-typing`](https://pypi.org/project/tigrbl-typing/)

### Engine packages

- [`tigrbl_engine_bigquery`](https://pypi.org/project/tigrbl_engine_bigquery/)
- [`tigrbl_engine_clickhouse`](https://pypi.org/project/tigrbl_engine_clickhouse/)
- [`tigrbl_engine_csv`](https://pypi.org/project/tigrbl_engine_csv/)
- [`tigrbl_engine_dataframe`](https://pypi.org/project/tigrbl_engine_dataframe/)
- [`tigrbl_engine_duckdb`](https://pypi.org/project/tigrbl_engine_duckdb/)
- [`tigrbl_engine_inmemcache`](https://pypi.org/project/tigrbl_engine_inmemcache/)
- [`tigrbl_engine_inmemory`](https://pypi.org/project/tigrbl_engine_inmemory/)
- [`tigrbl_engine_membloom`](https://pypi.org/project/tigrbl_engine_membloom/)
- [`tigrbl_engine_memdedupe`](https://pypi.org/project/tigrbl_engine_memdedupe/)
- [`tigrbl_engine_memkv`](https://pypi.org/project/tigrbl_engine_memkv/)
- [`tigrbl_engine_memlru`](https://pypi.org/project/tigrbl_engine_memlru/)
- [`tigrbl_engine_mempubsub`](https://pypi.org/project/tigrbl_engine_mempubsub/)
- [`tigrbl_engine_memqueue`](https://pypi.org/project/tigrbl_engine_memqueue/)
- [`tigrbl_engine_memrate`](https://pypi.org/project/tigrbl_engine_memrate/)
- [`tigrbl_engine_numpy`](https://pypi.org/project/tigrbl_engine_numpy/)
- [`tigrbl_engine_pandas`](https://pypi.org/project/tigrbl_engine_pandas/)
- [`tigrbl_engine_pgsqli_wal`](https://pypi.org/project/tigrbl_engine_pgsqli_wal/)
- [`tigrbl_engine_postgres`](https://pypi.org/project/tigrbl_engine_postgres/)
- [`tigrbl_engine_pyspark`](https://pypi.org/project/tigrbl_engine_pyspark/)
- [`tigrbl_engine_redis`](https://pypi.org/project/tigrbl_engine_redis/)
- [`tigrbl_engine_rediscachethrough`](https://pypi.org/project/tigrbl_engine_rediscachethrough/)
- [`tigrbl_engine_snowflake`](https://pypi.org/project/tigrbl_engine_snowflake/)
- [`tigrbl_engine_sqlite`](https://pypi.org/project/tigrbl_engine_sqlite/)
- [`tigrbl_engine_xlsx`](https://pypi.org/project/tigrbl_engine_xlsx/)

### Optional Rust runtime binding

The only Rust-related surface owned by this repository is the optional runtime binding package under `pkgs/core/tigrbl_runtime`.

## How to Choose a Package

- Install [`tigrbl`](https://pypi.org/project/tigrbl/) when you want the public Python authoring surface in one dependency.
- Install split core packages when you want a narrower subsystem boundary such as runtime, ORM, kernel, typing, client, tests, or operation families.
- Install engine packages when you want a backend-specific dependency surface for SQLite, Postgres, Redis, warehouse, tabular, or in-memory workflows.
- Use the independent `tigrbl_acme_ca` and `tigrbl_spiffe` repositories when you want ready-made Tigrbl application boundaries for ACME CA or SPIFFE/SPIRE identity flows.
- There are no active npm package manifests in this workspace at the moment.

## Current Package Line

The active Python package line is `0.4.1`. Repository-governed target status and release evidence are not declared from this README; use the canonical docs below for that authority.

## Canonical Repository Docs

- `docs/README.md`
- `docs/conformance/CURRENT_TARGET.md`
- `docs/conformance/CURRENT_STATE.md`
- `docs/conformance/NEXT_STEPS.md`
- `docs/conformance/NEXT_TARGETS.md`
- `docs/governance/DOC_POINTERS.md`
- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `SECURITY.md`

## Governance Notes

The `.ssot/` tree remains the governed source of truth for entities, package boundaries, and release evidence. Package-local `README.md` files under `pkgs/` and `crates/` are distribution entry points, not authoritative conformance records.

Release evidence is organized under `docs/conformance/releases/`. Active development-line evidence is organized under `docs/conformance/dev/`.

## License

Licensed under the Apache License, Version 2.0. See `LICENSE` and the official [Apache 2.0 license text](https://www.apache.org/licenses/LICENSE-2.0).
