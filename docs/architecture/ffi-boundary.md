# Python ↔ Rust FFI boundary

The intended boundary is narrow and explicit:

1. Python authors specs, hooks, handlers, atoms, and engine selections.
2. Python serializes the canonical spec once and crosses FFI at startup.
3. Rust compiles the kernel plan, instantiates the rust runtime, and serves requests.
4. Rust only crosses FFI again when the compiled plan hits an explicitly registered Python callback, hook, handler, engine hook, or atom callback fence.

This keeps the steady-state request path on Rust whenever the plan is composed entirely of Rust atoms, handlers, and engines.
