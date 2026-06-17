# Python-only runtime: benchmark rail

Planned performance-rail coverage for Rust retirement.

Assertions:
- Required benchmark scenarios do not include `tigrbl_rust_executor`.
- Python runtime and CPython/native-C hot-path rails remain governed where applicable.
- Reports fail if they present Rust executor comparison as a required core release gate.
