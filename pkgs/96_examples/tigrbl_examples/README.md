<div align="center">
<h1>tigrbl-examples</h1>
<img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png" alt="Tigrbl logo" width="140"/>
<p><strong>Packaged Tigrbl example modules migrated from the test support package.</strong></p>
<a href="https://pypi.org/project/tigrbl-examples/"><img src="https://img.shields.io/pypi/v/tigrbl-examples?label=PyPI" alt="PyPI version for tigrbl-examples"/></a>
<a href="https://pypi.org/project/tigrbl-examples/"><img src="https://static.pepy.tech/badge/tigrbl-examples" alt="Downloads for tigrbl-examples"/></a>
<a href="https://discord.gg/K4YTAPapjR"><img src="https://img.shields.io/badge/Discord-Join%20chat-5865F2?logo=discord&logoColor=white" alt="Discord community for tigrbl-examples"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/tigrbl_examples/README.md"><img src="https://hits.sh/github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/tigrbl_examples/README.md.svg?label=hits" alt="Repository hits for tigrbl-examples README"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-3776ab" alt="Python versions 3.10 | 3.11 | 3.12 | 3.13 | 3.14 for tigrbl-examples"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/docs/README.md"><img src="https://img.shields.io/badge/workspace-core-1f6feb" alt="Workspace group for tigrbl-examples"/></a>
</div>

## What is tigrbl-examples?

Packaged Tigrbl example modules migrated from the test support package.

## Why use tigrbl-examples?

Use it when examples need a package boundary separate from pytest fixtures and conformance helper utilities.

## When should I install tigrbl-examples?

Install it for runnable example modules, documentation checks, and integration tests that import shared example helpers.

## Who is tigrbl-examples for?

Maintainers, extension authors, and documentation workflows that need importable Tigrbl examples.

## Where does tigrbl-examples fit?

`tigrbl-examples` lives at `pkgs/96_examples/tigrbl_examples` and owns the migrated example module tree previously carried by `tigrbl_tests`.

## How does tigrbl-examples work?

It exposes example modules directly under the `tigrbl_examples` import root so callers import `tigrbl_examples.<module>` without an extra nested examples namespace.

## Install

```bash
uv add tigrbl-examples
```

```bash
pip install tigrbl-examples
```

## Surface Coverage

| Surface | Value |
|---|---|
| PyPI package | [`tigrbl-examples`](https://pypi.org/project/tigrbl-examples/) |
| Repository path | [`pkgs/96_examples/tigrbl_examples`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/96_examples/tigrbl_examples) |
| Python import root | `tigrbl_examples` |
| Console scripts | none declared |
| Entry points | none declared |
| Optional extras | none declared |
| Legal files | `LICENSE`, `NOTICE` |
| Supported Python | `3.10 | 3.11 | 3.12 | 3.13 | 3.14` |

## What It Owns

`tigrbl-examples` owns the `example package` boundary. It does not own conformance assertions, package validation policy, or reusable pytest harness internals.

Implementation orientation:
- `tigrbl_examples`: migrated beginner, intermediate, advanced, and expert example modules plus shared example helpers.

## Public API and Import Surface

- Import roots: `tigrbl_examples`.
- Public symbols: public surface is module-oriented; import the needed example module or helper directly.
- Workspace dependencies: [`tigrbl`](https://pypi.org/project/tigrbl/), [`tigrbl_client`](https://pypi.org/project/tigrbl_client/).
- External runtime dependencies: `httpx>=0.27.0,<0.28`, `pytest>=8.0`, `pytest-asyncio>=0.24.0`, `uvicorn`.

## Usage Examples

### Verify the installed package

```bash
python -m pip show tigrbl-examples
python - <<'PY'
from importlib.metadata import version
print(version("tigrbl-examples"))
PY
```

### Import the package boundary

```python
import tigrbl_examples

print(tigrbl_examples.__name__)
```

### Import shared example helpers

```python
from tigrbl_examples._support import pick_unique_port

print(pick_unique_port())
```

### Run the migrated example tests

```bash
uv run pytest pkgs/96_examples/tigrbl_examples/tigrbl_examples -q
```

## How To Choose This Package

Choose `tigrbl-examples` when you need importable example modules. Choose [`tigrbl_tests`](https://pypi.org/project/tigrbl_tests/) when you need reusable test helpers, fixtures, and conformance assertions.

## Related Packages

- [`tigrbl`](https://pypi.org/project/tigrbl/)
- [`tigrbl_client`](https://pypi.org/project/tigrbl_client/)
- [`tigrbl_tests`](https://pypi.org/project/tigrbl_tests/)

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
- Repository: [pkgs/96_examples/tigrbl_examples](https://github.com/tigrbl/tigrbl/tree/master/pkgs/96_examples/tigrbl_examples).

## Package-local Boundary

This README is the package-local distribution entry point for `tigrbl-examples`. It answers install, usage, API, ownership, and certification-orientation questions for this package. Broader architectural decisions, release status, and cross-package proof chains remain in the repository-level docs and SSOT registry.

## Certification Status

- Package status: governed package in the `tigrbl/tigrbl` workspace.
- Governance source: [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json).
- Release evidence: [publish workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml) validates package builds, tests, GitHub release assets, and PyPI publication for managed packages.
- Local certification guard: `pkgs/97_tests/tigrbl_tests/tests/unit/test_package_badges_and_notices.py` verifies every package README keeps the Discord badge, Apache 2.0 badge, explicit Python-version badge, `LICENSE`, and `NOTICE`.
- Scope note: this README documents the package boundary. Runtime feature support remains governed by `.ssot/` entities and the conformance docs linked below.

## License

Licensed under the Apache License, Version 2.0. See `LICENSE`, `NOTICE`, and the official [Apache 2.0 license text](https://www.apache.org/licenses/LICENSE-2.0).
