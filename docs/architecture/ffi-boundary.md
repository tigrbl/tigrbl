# Optional Rust Runtime Binding FFI Boundary

The intended boundary is narrow and explicit:

1. Python authors specs, hooks, handlers, atoms, and engine selections.
2. Python serializes the canonical spec once and crosses FFI at startup when the optional binding is enabled.
3. The optional binding compiles the kernel plan and instantiates its runtime handle.
4. The binding only crosses FFI again when the compiled plan hits an explicitly registered Python callback, hook, handler, engine hook, or atom callback fence.

This document is limited to the optional runtime binding package. It does not define a broader Rust runtime program for this repository.
