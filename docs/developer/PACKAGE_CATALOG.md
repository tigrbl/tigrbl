# Package Catalog

This document is the canonical workspace inventory for Python package locations.

## Counts

- core Python packages: 15
- engine packages: 22
- application packages: 0
- Rust runtime binding packages: 0

## Core Python packages

- `tigrbl`
- `tigrbl_atoms`
- `tigrbl_base`
- `tigrbl_canon`
- `tigrbl_client`
- `tigrbl_concrete`
- `tigrbl_core`
- `tigrbl_kernel`
- `tigrbl_ops_olap`
- `tigrbl_ops_oltp`
- `tigrbl_orm`
- `tigrbl_runtime`
- `tigrbl_spec`
- `tigrbl_tests`
- `tigrbl_typing`

## Engine packages

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
- `tigrbl_engine_pyspark`
- `tigrbl_engine_redis`
- `tigrbl_engine_rediscachethrough`
- `tigrbl_engine_snowflake`
- `tigrbl_engine_xlsx`

## Application packages

Application packages are not owned by this workspace. `tigrbl_acme_ca` and `tigrbl_spiffe` live in independent repositories.

## Rust runtime binding packages

None. Tigrbl runtime execution is Python-only. Rust-named compatibility modules
are not shipped by this repository.

## Package README policy

Package-local `README.md` files are retained as distribution entry points only. Repository-governed documentation lives under `docs/`.
