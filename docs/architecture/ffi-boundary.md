# Deprecated Rust Runtime FFI Boundary

Tigrbl runtime execution is Python-only.

The former Rust runtime FFI boundary is deprecated. Compatibility imports remain
only to produce explicit deprecation warnings and failure modes for callers that
still reference Rust-named helpers. They must not be used as execution,
planning, registration, packaging, or certification surfaces.
