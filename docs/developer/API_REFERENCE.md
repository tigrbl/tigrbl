# API and Workspace Reference

## Workspace inventory

### Core packages (15)
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

### Engine packages (22)
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

### App packages (0)
Application packages are owned by independent repositories, not this workspace.

### Rust runtime binding
Tigrbl runtime execution is Python-only. No Rust runtime binding package or
Rust-named compatibility import surface is exposed by this repository.

## Public surfaces currently documented in the supplied checkpoint

- REST
- JSON-RPC surface
- request/response surface
- templating
- middleware protocol
- OpenAPI 3.1 document emission
- Swagger UI
- OpenRPC JSON
- Lens / OpenRPC UI
- generic auth/security plumbing
- Python-only runtime execution
