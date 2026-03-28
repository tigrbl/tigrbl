# Rust-native crate boundaries

The Rust-native substrate is additive. Python packages remain the authoring and compatibility surface, while native crates own compile-time and execution-time hot paths.

## Primary crates

- `tigrbl_rs_spec`: canonical native IR, datatype semantics, physical storage hints, request/response envelopes.
- `tigrbl_rs_ports`: dependency-breaking traits for atoms, handlers, engines, sessions, transactions, and callbacks.
- `tigrbl_rs_atoms`: phase algebra, atom registry, native atom catalog, and sys handler atoms.
- `tigrbl_rs_ops_oltp`: CRUD and bulk verb semantics, native built-in handlers, normalization, defaults, and patch/merge shaping.
- `tigrbl_rs_kernel`: compile pipeline, packed plan model, routing/opview lowering, and optimizer passes.
- `tigrbl_rs_runtime`: native executor, callback fences, engine resolution, transaction lifecycle, and runtime handles.
- `tigrbl_rs_engine_sqlite`, `tigrbl_rs_engine_postgres`, `tigrbl_rs_engine_inmemory`: native engine/session/tx implementations and engine-specific lowering.

## Boundary rules

- atoms do not own CRUD semantics or engine I/O;
- OLTP ops do not own phase algebra or runtime orchestration;
- kernel compiles and optimizes plans but does not execute live requests;
- runtime executes compiled plans but does not author spec or redefine CRUD semantics;
- engine crates do not know transport routing or Python binding details;
- `bindings/python/tigrbl_native` is glue only and must not become a logic sink.
