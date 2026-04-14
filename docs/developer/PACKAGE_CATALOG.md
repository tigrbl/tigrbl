# Package Catalog

This document is the canonical workspace inventory for package and crate locations.

## Counts

- core Python packages: 15
- engine packages: 22
- application packages: 6
- Rust crates: 9
- hybrid Python/Rust packages under `pkgs/`: 1

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

- `tigrbl_acme_ca`
- `tigrbl_api_cron`
- `tigrbl_api_hpks`
- `tigrbl_billing`
- `tigrbl_kms`
- `tigrbl_spiffe`

## Rust crates

- `tigrbl_rs_atoms`
- `tigrbl_rs_engine_inmemory`
- `tigrbl_rs_engine_postgres`
- `tigrbl_rs_engine_sqlite`
- `tigrbl_rs_kernel`
- `tigrbl_rs_ops_oltp`
- `tigrbl_rs_ports`
- `tigrbl_rs_runtime`
- `tigrbl_rs_spec`

## Hybrid Python/Rust packages

- `pkgs/core/tigrbl_runtime`

## Package README policy

Package-local `README.md` files are retained as distribution entry points only. Repository-governed documentation lives under `docs/`.
