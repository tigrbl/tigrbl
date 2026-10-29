# Tigrbl Equivalence Contracts

This local uv project contains runtime code and tests for assertable
equivalence demonstrations. It is not a PyPI package.

Run from the repository root:

```powershell
python tools/ci/validate_equivalence_runtime_contracts.py
```

Or run the local uv project directly:

```powershell
uv run --project pkgs/96_examples/equivalence_contracts --group dev python -m pytest -q pkgs/96_examples/equivalence_contracts/tests
```

Or run the tests with an already prepared environment:

```powershell
python -m pytest -q pkgs/96_examples/equivalence_contracts/tests
```


## What is tigrbl-equivalence-contracts?

Local runtime demonstrations for certifiable Tigrbl equivalence claims.

## Why use tigrbl-equivalence-contracts?

Use this project for local runtime demonstrations for certifiable Tigrbl equivalence claims.

## When should I install tigrbl-equivalence-contracts?

Use it when your application or development task needs the surface described below.
Examples and experimental projects should be run from this checkout.

## Who is tigrbl-equivalence-contracts for?

Tigrbl maintainers and application developers working with this project’s APIs.

## Where does tigrbl-equivalence-contracts fit?

Source: `pkgs/96_examples/equivalence_contracts` in the Tigrbl workspace.

## How does tigrbl-equivalence-contracts work?

Contract declarations and Tigrbl, FastAPI, and Flask comparison implementations. The examples and implementation above describe the configuration and execution flow.

## Certification Status

No independent release qualification is claimed by this README. Inspect current
repository test results and the applicable release gates before deployment.

## Install

From the repository root:

```console
uv sync --project pkgs/96_examples/equivalence_contracts
```

## Surface Coverage

| Surface | Value |
| --- | --- |
| Project | `tigrbl-equivalence-contracts` |
| Python requirement | `>=3.10,<3.15` |
| Python range | 3.10 \| 3.11 \| 3.12 \| 3.13 \| 3.14 |
| Source/import surface | `tigrbl_equivalence_contracts` |

Supported Python versions: 3.10 | 3.11 | 3.12 | 3.13 | 3.14.

## What It Owns

Local runtime demonstrations for certifiable Tigrbl equivalence claims.

## Public API and Import Surface

Contract declarations and Tigrbl, FastAPI, and Flask comparison implementations. See the project source and existing examples above for supported call signatures.

## Usage Examples

The walkthrough above is retained. The entry surface can be loaded with:

```python
import tigrbl_equivalence_contracts
```

## How To Choose This Package

Choose this project when its stated surface matches your task. Examples and
experimental integrations do not imply production support for every transport.

## Related Packages

See [the workspace package catalog](https://github.com/tigrbl/tigrbl/tree/master/pkgs)
and the dependencies in [pyproject.toml](pyproject.toml).

## Documentation Links

- [Tigrbl documentation](https://github.com/tigrbl/tigrbl/tree/master/docs)
- [Project source](https://github.com/tigrbl/tigrbl/tree/master/pkgs/96_examples/equivalence_contracts)

## Support

Report reproducible issues at [GitHub](https://github.com/tigrbl/tigrbl/issues)
or discuss usage on [Discord](https://discord.gg/K4YTAPapjR).

## License

[Apache 2.0](LICENSE). See [NOTICE](NOTICE) for attribution.

![License](https://img.shields.io/badge/license-Apache%202.0-525252)
