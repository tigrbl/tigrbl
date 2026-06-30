# Package Catalog

This document is the canonical workspace inventory for Python package locations.
Layer order is governed by `pkgs/LAYERS.toml` and projected in
`docs/developer/PACKAGE_LAYERS.md`.

## Counts

- core Python packages: 17
- engine packages: 24
- application packages: 0
- deprecated packages: 1
- Rust runtime binding packages: 0

## Core Python Packages

- `tigrbl_typing`
- `tigrbl_spec`
- `tigrbl_core`
- `tigrbl_base`
- `tigrbl_orm`
- `tigrbl_atoms`
- `tigrbl_kernel`
- `tigrbl_runtime`
- `tigrbl_ops_olap`
- `tigrbl_ops_oltp`
- `tigrbl_ops_realtime`
- `tigrbl_ops_webtransport`
- `tigrbl_concrete`
- `tigrbl`
- `tigrbl_client`
- `tigrbl_examples`
- `tigrbl_tests`

## Engine Packages

- `tigrbl_engine_bigquery`
- `tigrbl_engine_clickhouse`
- `tigrbl_engine_csv`
- `tigrbl_engine_dataframe`
- `tigrbl_engine_duckdb`
- `tigrbl_engine_inmemcache`
- `tigrbl_engine_inmemory`
- `tigrbl_engine_membloom`
- `tigrbl_engine_memdedupe`
- `tigrbl_engine_memkv`
- `tigrbl_engine_memlru`
- `tigrbl_engine_mempubsub`
- `tigrbl_engine_memqueue`
- `tigrbl_engine_memrate`
- `tigrbl_engine_numpy`
- `tigrbl_engine_pandas`
- `tigrbl_engine_pgsqli_wal`
- `tigrbl_engine_postgres`
- `tigrbl_engine_pyspark`
- `tigrbl_engine_redis`
- `tigrbl_engine_rediscachethrough`
- `tigrbl_engine_snowflake`
- `tigrbl_engine_sqlite`
- `tigrbl_engine_xlsx`

## Application Packages

Application packages are not owned by this workspace. `tigrbl_acme_ca` and
`tigrbl_spiffe` live in independent repositories.

## Deprecated Packages

- `tigrbl_canon`

## Rust Runtime Binding Packages

None. Tigrbl runtime execution is Python-only. Rust-named compatibility modules
are not shipped by this repository.

## Package README Policy

Package-local `README.md` files are retained as distribution entry points only.
Repository-governed documentation lives under `docs/`.
