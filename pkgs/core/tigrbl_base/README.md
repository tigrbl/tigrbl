<div align="center">
<h1>tigrbl-base</h1>
<img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png" alt="Tigrbl logo" width="140"/>
<p><strong>Base contract package for Tigrbl apps, routers, tables, sessions, middleware, requests, responses, bindings, and engine interfaces.</strong></p>
<a href="https://pypi.org/project/tigrbl-base/"><img src="https://img.shields.io/pypi/v/tigrbl-base?label=PyPI" alt="PyPI version for tigrbl-base"/></a>
<a href="https://pypi.org/project/tigrbl-base/"><img src="https://static.pepy.tech/badge/tigrbl-base" alt="Downloads for tigrbl-base"/></a>
<a href="https://discord.gg/K4YTAPapjR"><img src="https://img.shields.io/badge/Discord-Join%20chat-5865F2?logo=discord&logoColor=white" alt="Discord community for tigrbl-base"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_base/README.md"><img src="https://hits.sh/github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_base/README.md.svg?label=hits" alt="Repository hits for tigrbl-base README"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-3776ab" alt="Python versions 3.10 | 3.11 | 3.12 | 3.13 | 3.14 for tigrbl-base"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/docs/README.md"><img src="https://img.shields.io/badge/workspace-core-1f6feb" alt="Workspace group for tigrbl-base"/></a>
</div>

## What is tigrbl-base?

Base contract package for Tigrbl apps, routers, tables, sessions, middleware, requests, responses, bindings, and engine interfaces.

## Why use tigrbl-base?

Use it when you need this foundational Tigrbl layer directly as a small, focused dependency.

## When should I install tigrbl-base?

Install it for extension packages, package-local tests, or internals that need this boundary without the whole facade.

## Who is tigrbl-base for?

Framework maintainers, extension authors, and advanced users composing Tigrbl from split packages.

## Where does tigrbl-base fit?

`tigrbl-base` lives at `pkgs/core/tigrbl_base` and serves a focused layer in the split Tigrbl framework.

## How does tigrbl-base work?

It owns a narrow layer in the split workspace and is consumed by higher-level packages through explicit dependencies.

## Certification Status

- Package status: governed package in the `tigrbl/tigrbl` workspace.
- Governance source: [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json).
- Release evidence: [publish workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml) validates package builds, tests, GitHub release assets, and PyPI publication for managed packages.
- Local certification guard: `pkgs/core/tigrbl_tests/tests/unit/test_package_badges_and_notices.py` verifies every package README keeps the Discord badge, Apache 2.0 badge, explicit Python-version badge, `LICENSE`, and `NOTICE`.
- Scope note: this README documents the package boundary. Runtime feature support remains governed by `.ssot/` entities and the conformance docs linked below.

## Install

```bash
uv add tigrbl-base
```

```bash
pip install tigrbl-base
```

## Surface Coverage

| Surface | Value |
|---|---|
| PyPI package | [`tigrbl-base`](https://pypi.org/project/tigrbl-base/) |
| Repository path | [`pkgs/core/tigrbl_base`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_base) |
| Python import root | `tigrbl_base` |
| Console scripts | none declared |
| Entry points | none declared |
| Optional extras | none declared |
| Legal files | `LICENSE`, `NOTICE` |
| Supported Python | `3.10 | 3.11 | 3.12 | 3.13 | 3.14` |

## What It Owns

`tigrbl-base` owns the `foundational framework package` boundary. It should be installed when you need this package's focused responsibility without assuming every other Tigrbl workspace package is present.

Implementation orientation:
- `tigrbl_base`: _base/, column/

## Public API and Import Surface

- Import roots: `tigrbl_base`.
- Public symbols: public surface is module-oriented; import the package boundary and inspect submodules as needed.
- Workspace dependencies: [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/).
- External runtime dependencies: `sqlalchemy>=2.0`, `pydantic>=2.0`.

## Usage Examples

### Verify the installed package

```bash
python -m pip show tigrbl-base
python - <<'PY'
from importlib.metadata import version
print(version("tigrbl-base"))
PY
```

### Import the package boundary

```python
import importlib

module = importlib.import_module("tigrbl_base._base")
print(module.__name__)
```

### Inspect available modules

```python
import importlib
import pkgutil

module = importlib.import_module("tigrbl_base._base")
for info in pkgutil.iter_modules(getattr(module, "__path__", [])):
    print(info.name)
```

### Use with the facade when building applications

```bash
uv add tigrbl tigrbl-base
python - <<'PY'
import tigrbl
print(tigrbl.__name__)
PY
```

## How To Choose This Package

Choose `tigrbl-base` when the quick-answer table matches your use case. Choose [`tigrbl`](https://pypi.org/project/tigrbl/) instead when you want the full public facade. Choose a lower-level package such as [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-base`](https://pypi.org/project/tigrbl-base/), or [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/) when you are building framework extensions or testing a specific internal boundary.

## Related Packages

- [`tigrbl-core`](https://pypi.org/project/tigrbl-core/)
- [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/)
- [`tigrbl`](https://pypi.org/project/tigrbl/)
- [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/)

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
- Repository: [pkgs/core/tigrbl_base](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_base).

## Package-local Boundary

This README is the package-local distribution entry point for `tigrbl-base`. It answers install, usage, API, ownership, and certification-orientation questions for this package. Broader architectural decisions, release status, and cross-package proof chains remain in the repository-level docs and SSOT registry.

## License

Licensed under the Apache License, Version 2.0. See `LICENSE`, `NOTICE`, and the official [Apache 2.0 license text](https://www.apache.org/licenses/LICENSE-2.0).
