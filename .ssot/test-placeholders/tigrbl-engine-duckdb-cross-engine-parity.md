# DuckDB Cross-Engine Parity Test Plan

Planned pytest coverage for the `tigrbl_engine_duckdb` package.

The test should compare DuckDB against the portable SQLite and PostgreSQL engine subset for:

- DDL readiness through governed initialization entrypoints.
- Engine-session lifecycle and common database operations.
- Canonical table operation behavior where the engine advertises compatible capabilities.

The test must stay package-local to Tigrbl engine certification and must not depend on downstream applications.
