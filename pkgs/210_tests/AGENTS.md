# Tigrbl test layer

- [`tigrbl_tests/tests/unit/`](tigrbl_tests/tests/unit/) holds framework unit tests. [`tigrbl_tests/tests/i9n/`](tigrbl_tests/tests/i9n/) holds integration tests that exercise components together.
- The [shared suite](tigrbl_tests/tests/) also groups tests by area, including architecture, protocol, security, parity, and performance. Extend the closest existing suite for shared behavior.
- [`tigrbl_tests/v4/tests/spec/`](tigrbl_tests/v4/tests/spec/) holds v4 spec contract tests. [`tigrbl_tests/benchmarks/`](tigrbl_tests/benchmarks/) holds benchmark tooling.
- For behavior owned by one workspace package, look in that package’s `tests/` directory. The [root test guide](../../tests/AGENTS.md) points to planned contracts, SSOT scaffolding, and tooling suites.

Run the main shared suite from the repository root:

```bash
uv run pytest pkgs/210_tests/tigrbl_tests/tests -q
```
