# Package Layers

`pkgs/LAYERS.toml` is the machine-readable package layer index. This document is
the human-readable projection for repository maintainers.

The index is dependency-oriented, not a physical move plan. Package directories
remain under `pkgs/core`, `pkgs/engines`, and `pkgs/deprecated`; layer membership
records their intended ownership and dependency order.

## Dependency Rule

Packages may depend on packages in a lower-numbered layer or the same layer.
Higher-layer dependencies are allowed only when listed in `pkgs/LAYERS.toml` as
explicit dependency exceptions with a reason.

## Layers

| Layer | Title | Packages |
|---:|---|---|
| 00 | Typing | `tigrbl_typing` |
| 01 | Spec | `tigrbl_spec` |
| 10 | Core | `tigrbl_core` |
| 20 | Base | `tigrbl_base` |
| 30 | ORM | `tigrbl_orm` |
| 40 | Atoms | `tigrbl_atoms` |
| 45 | Kernel | `tigrbl_kernel` |
| 50 | Runtime | `tigrbl_runtime` |
| 60 | Operations | `tigrbl_ops_olap`, `tigrbl_ops_oltp`, `tigrbl_ops_realtime`, `tigrbl_ops_webtransport` |
| 70 | Concrete | `tigrbl_concrete` |
| 80 | Facade | `tigrbl` |
| 90 | Engines | `tigrbl_engine_bigquery`, `tigrbl_engine_clickhouse`, `tigrbl_engine_csv`, `tigrbl_engine_dataframe`, `tigrbl_engine_duckdb`, `tigrbl_engine_inmemcache`, `tigrbl_engine_inmemory`, `tigrbl_engine_membloom`, `tigrbl_engine_memdedupe`, `tigrbl_engine_memkv`, `tigrbl_engine_memlru`, `tigrbl_engine_mempubsub`, `tigrbl_engine_memqueue`, `tigrbl_engine_memrate`, `tigrbl_engine_numpy`, `tigrbl_engine_pandas`, `tigrbl_engine_pgsqli_wal`, `tigrbl_engine_postgres`, `tigrbl_engine_pyspark`, `tigrbl_engine_redis`, `tigrbl_engine_rediscachethrough`, `tigrbl_engine_snowflake`, `tigrbl_engine_sqlite`, `tigrbl_engine_xlsx` |
| 95 | Tooling | `tigrbl_client`, `tigrbl_examples`, `tigrbl_tests` |
| 99 | Deprecated | `tigrbl_canon` |

## Current Exceptions

The layer index intentionally records current dependency inversions instead of
hiding them. New inversions should not be added casually; either move the
dependency to a lower layer, move the package to the correct layer, or add a
short-lived exception with an owner-facing reason.

Current exceptions:

- `tigrbl -> tigrbl_canon`
- `tigrbl_base -> tigrbl_atoms`
- `tigrbl_atoms -> tigrbl_ops_olap`
- `tigrbl_atoms -> tigrbl_ops_oltp`
- `tigrbl_atoms -> tigrbl_ops_realtime`
- `tigrbl_atoms -> tigrbl_ops_webtransport`

## Maintenance

When adding, removing, or moving a package:

1. Update `pkgs/LAYERS.toml`.
2. Update this document and `docs/developer/PACKAGE_CATALOG.md`.
3. Run `uv run pytest pkgs/core/tigrbl_tests/tests/unit/test_package_layers.py -q`.
