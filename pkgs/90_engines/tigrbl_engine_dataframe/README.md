<div align="center">
<h1>tigrbl_engine_dataframe</h1>
<img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png" alt="Tigrbl logo" width="140"/>
<p><strong>DataFrame engine plugin for transactional pandas sessions and in-process Tigrbl analytics workloads.</strong></p>
<a href="https://pypi.org/project/tigrbl_engine_dataframe/"><img src="https://img.shields.io/pypi/v/tigrbl_engine_dataframe?label=PyPI" alt="PyPI version for tigrbl_engine_dataframe"/></a>
<a href="https://pypi.org/project/tigrbl_engine_dataframe/"><img src="https://static.pepy.tech/badge/tigrbl_engine_dataframe" alt="Downloads for tigrbl_engine_dataframe"/></a>
<a href="https://discord.gg/K4YTAPapjR"><img src="https://img.shields.io/badge/Discord-Join%20chat-5865F2?logo=discord&logoColor=white" alt="Discord community for tigrbl_engine_dataframe"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_dataframe/README.md"><img src="https://hits.sh/github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_dataframe/README.md.svg?label=hits" alt="Repository hits for tigrbl_engine_dataframe README"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-3776ab" alt="Python versions 3.10 | 3.11 | 3.12 | 3.13 | 3.14 for tigrbl_engine_dataframe"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/docs/README.md"><img src="https://img.shields.io/badge/workspace-engines-1f6feb" alt="Workspace group for tigrbl_engine_dataframe"/></a>
</div>

## What is tigrbl_engine_dataframe?

DataFrame engine plugin for transactional pandas sessions and in-process Tigrbl analytics workloads.

## Why use tigrbl_engine_dataframe?

Use it when a Tigrbl application needs this backend without installing every engine package.

## When should I install tigrbl_engine_dataframe?

Install it when the storage, analytics, cache, or integration workload named by this package is the intended runtime backend.

## Who is tigrbl_engine_dataframe for?

Application developers, data platform engineers, and operators choosing concrete persistence or data-plane behavior.

## Where does tigrbl_engine_dataframe fit?

`tigrbl_engine_dataframe` lives at `pkgs/90_engines/tigrbl_engine_dataframe` and serves DataFrame-backed tabular workflows.

## How does tigrbl_engine_dataframe work?

It exposes a `tigrbl.engine` entry point and a package `register()` hook so Tigrbl can discover or load the backend at runtime.


## Install

```bash
uv add tigrbl_engine_dataframe
```

```bash
pip install tigrbl_engine_dataframe
```

## Surface Coverage

| Surface | Value |
|---|---|
| PyPI package | [`tigrbl_engine_dataframe`](https://pypi.org/project/tigrbl_engine_dataframe/) |
| Repository path | [`pkgs/90_engines/tigrbl_engine_dataframe`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/90_engines/tigrbl_engine_dataframe) |
| Python import root | `tigrbl_engine_dataframe` |
| Console scripts | none declared |
| Entry points | `tigrbl.engine` |
| Optional extras | none declared |
| Legal files | `LICENSE`, `NOTICE` |
| Supported Python | `3.10 | 3.11 | 3.12 | 3.13 | 3.14` |

## What It Owns

`tigrbl_engine_dataframe` owns the `engine plugin` boundary. It should be installed when you need this package's focused responsibility without assuming every other Tigrbl workspace package is present.

Implementation orientation:
- `tigrbl_engine_dataframe`: df_engine, df_session

## Public API and Import Surface

- Import roots: `tigrbl_engine_dataframe`.
- Public symbols: `DataFrameCatalog`, `TransactionalDataFrameSession`, `dataframe_capabilities`, `dataframe_engine`, `register`.
- Workspace dependencies: [`tigrbl`](https://pypi.org/project/tigrbl/).
- External runtime dependencies: `pandas>=2.0`.

## Usage Examples

### Verify the installed package

```bash
python -m pip show tigrbl_engine_dataframe
python - <<'PY'
from importlib.metadata import version
print(version("tigrbl_engine_dataframe"))
PY
```

### Register the engine plugin explicitly

```python
from tigrbl_engine_dataframe import register

register()
```

### Discover the engine through package metadata

```python
from importlib.metadata import entry_points

for entry_point in entry_points(group="tigrbl.engine"):
    if entry_point.module.startswith("tigrbl_engine_dataframe"):
        plugin_register = entry_point.load()
        plugin_register()
```

### Install alongside the facade

```bash
uv add tigrbl tigrbl_engine_dataframe
pip install tigrbl tigrbl_engine_dataframe
```

## How To Choose This Package

Choose `tigrbl_engine_dataframe` when the quick-answer table matches your use case. Choose [`tigrbl`](https://pypi.org/project/tigrbl/) instead when you want the full public facade. Choose a lower-level package such as [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-base`](https://pypi.org/project/tigrbl-base/), or [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/) when you are building framework extensions or testing a specific internal boundary.

## Related Packages

- [`tigrbl`](https://pypi.org/project/tigrbl/)
- [`tigrbl-core`](https://pypi.org/project/tigrbl-core/)
- [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/)
- [`tigrbl_engine_sqlite`](https://pypi.org/project/tigrbl_engine_sqlite/)
- [`tigrbl_engine_postgres`](https://pypi.org/project/tigrbl_engine_postgres/)
- [`tigrbl_engine_duckdb`](https://pypi.org/project/tigrbl_engine_duckdb/)
- [`tigrbl_engine_pandas`](https://pypi.org/project/tigrbl_engine_pandas/)

## Documentation Links

- [Workspace docs](https://github.com/tigrbl/tigrbl/blob/master/docs/README.md)
- [Package catalog](https://github.com/tigrbl/tigrbl/blob/master/docs/developer/PACKAGE_CATALOG.md)
- [Package layout](https://github.com/tigrbl/tigrbl/blob/master/docs/developer/PACKAGE_LAYOUT.md)
- [Current target](https://github.com/tigrbl/tigrbl/blob/master/docs/conformance/CURRENT_TARGET.md)
- [Current state](https://github.com/tigrbl/tigrbl/blob/master/docs/conformance/CURRENT_STATE.md)
- [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json)
- [Release workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml)

## Support

- Community: [Discord](https://discord.gg/K4YTAPapjR).
- Issues: [GitHub Issues](https://github.com/tigrbl/tigrbl/issues).
- Repository: [pkgs/90_engines/tigrbl_engine_dataframe](https://github.com/tigrbl/tigrbl/tree/master/pkgs/90_engines/tigrbl_engine_dataframe).

## Package-local Boundary

This README is the package-local distribution entry point for `tigrbl_engine_dataframe`. It answers install, usage, API, ownership, and certification-orientation questions for this package. Broader architectural decisions, release status, and cross-package proof chains remain in the repository-level docs and SSOT registry.

## Certification Status

- Package status: governed package in the `tigrbl/tigrbl` workspace.
- Governance source: [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json).
- Release evidence: [publish workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml) validates package builds, tests, GitHub release assets, and PyPI publication for managed packages.
- Local certification guard: `pkgs/97_tests/tigrbl_tests/tests/unit/test_package_badges_and_notices.py` verifies every package README keeps the Discord badge, Apache 2.0 badge, explicit Python-version badge, `LICENSE`, and `NOTICE`.
- Scope note: this README documents the package boundary. Runtime feature support remains governed by `.ssot/` entities and the conformance docs linked below.

## License

Licensed under the Apache License, Version 2.0. See `LICENSE`, `NOTICE`, and the official [Apache 2.0 license text](https://www.apache.org/licenses/LICENSE-2.0).
