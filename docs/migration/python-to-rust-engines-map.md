# Python → Rust engine migration map

- `pkgs/engines/tigrbl_engine_inmemory/src/tigrbl_engine_inmemory/engine.py` → `crates/tigrbl_rs_engine_inmemory/src/engine.rs`
- `pkgs/engines/tigrbl_engine_inmemory/src/tigrbl_engine_inmemory/session.py` → `crates/tigrbl_rs_engine_inmemory/src/session.rs`
- native SQLite support is introduced in `crates/tigrbl_rs_engine_sqlite`
- native Postgres support is introduced in `crates/tigrbl_rs_engine_postgres`
