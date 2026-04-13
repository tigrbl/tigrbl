# Phase 2 package-structure normalization archive

This archive preserves package-local Markdown files and duplicate nested package roots that were removed or replaced during **Phase 2 — package-structure and policy hardening**.

## Actions recorded here

- package-local long-form Markdown files were archived under `shadow-md/`
- package root `README.md` files were replaced with governed pointer stubs after their original contents were archived
- duplicate nested engine package roots were archived under `dupe-pkg-roots/` and removed from the active workspace tree

## Removed nested duplicate package roots

- `pkgs/engines/tigrbl_engine_pandas/tigrbl_engine_pandas`
- `pkgs/engines/tigrbl_engine_redis/tigrbl_engine_redis`
- `pkgs/engines/tigrbl_engine_snowflake/tigrbl_engine_snowflake`

Use the governed docs tree under `docs/` for authoritative repository documentation.
