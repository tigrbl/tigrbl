# Removed Rust Runtime FFI Boundary

Tigrbl runtime execution is Python-only.

The former Rust runtime FFI boundary has been removed. This repository does not
ship Rust-named runtime, kernel, atom, handler, engine registration, packaging,
or certification surfaces.
