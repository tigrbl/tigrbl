# Rust engine architecture

Rust engines remain behind engine/session/transaction ports.

- `tigrbl_rs_engine_sqlite` is the lightweight embedded SQL engine.
- `tigrbl_rs_engine_postgres` is the remote transactional SQL engine.
- `tigrbl_rs_engine_inmemory` provides process-local row-store and column-store strategies for dict-like and dataframe-like execution.

Engines own their own session lifecycle, transaction lifecycle, DDL/query codecs, reflection, and datatype lowerers. They do not own route compilation, phase algebra, or Python authoring APIs.
