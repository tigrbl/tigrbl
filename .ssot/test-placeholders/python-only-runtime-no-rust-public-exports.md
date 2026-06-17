# Python-only runtime: no supported Rust public surface

Planned export-surface coverage for Rust retirement.

Assertions:
- Public facade exports do not advertise Rust runtime helpers as supported APIs.
- `tigrbl_atoms` and `tigrbl_runtime` do not expose Rust callback, atom, trace, or runtime helpers as supported public core APIs.
- Any temporary compatibility shim is visibly deprecated and not treated as supported public surface.
