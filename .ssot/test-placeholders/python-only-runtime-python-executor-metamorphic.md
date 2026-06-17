# Python-only runtime: Python executor metamorphic coverage

Planned parity replacement coverage after retiring Rust executor comparison.

Assertions:
- Existing executor metamorphic tests retain Python-only request/result invariants.
- Rust executor entrypoints are removed from the metamorphic matrix.
- Python runtime semantics remain stable for the covered corpus.
