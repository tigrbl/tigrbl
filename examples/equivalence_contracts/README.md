# Tigrbl Equivalence Contracts

This local uv project contains runtime code and tests for assertable
equivalence demonstrations. It is not a PyPI package.

Run from the repository root:

```powershell
python tools/ci/validate_equivalence_runtime_contracts.py
```

Or run the local uv project directly:

```powershell
uv run --project examples/equivalence_contracts --group dev python -m pytest -q examples/equivalence_contracts/tests
```

Or run the tests with an already prepared environment:

```powershell
python -m pytest -q examples/equivalence_contracts/tests
```
