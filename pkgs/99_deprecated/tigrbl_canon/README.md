<div align="center">
<h1>tigrbl-canon</h1>
<img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png" alt="Tigrbl logo" width="140"/>
<p><strong>Deprecated legacy compatibility package for Tigrbl canonical mapping, router binding, schema attachment, RPC and REST exposure, and column inference utilities.</strong></p>
<a href="https://pypi.org/project/tigrbl-canon/"><img src="https://img.shields.io/pypi/v/tigrbl-canon?label=PyPI" alt="PyPI version for tigrbl-canon"/></a>
<a href="https://pypi.org/project/tigrbl-canon/"><img src="https://static.pepy.tech/badge/tigrbl-canon" alt="Downloads for tigrbl-canon"/></a>
<a href="https://discord.gg/K4YTAPapjR"><img src="https://img.shields.io/badge/Discord-Join%20chat-5865F2?logo=discord&logoColor=white" alt="Discord community for tigrbl-canon"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/99_deprecated/tigrbl_canon/README.md"><img src="https://hits.sh/github.com/tigrbl/tigrbl/blob/master/pkgs/99_deprecated/tigrbl_canon/README.md.svg?label=hits" alt="Repository hits for tigrbl-canon README"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-3776ab" alt="Python versions 3.10 | 3.11 | 3.12 | 3.13 | 3.14 for tigrbl-canon"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/docs/README.md"><img src="https://img.shields.io/badge/workspace-deprecated-6b7280" alt="Workspace group for tigrbl-canon"/></a>
</div>

## What is tigrbl-canon?

Deprecated legacy compatibility package for Tigrbl canonical mapping, router binding, schema attachment, RPC and REST exposure, and column inference utilities. New code should not add this package; it exists only to carry older `tigrbl_canon` import paths during migrations.

## Why use tigrbl-canon?

Use it only when maintaining older integrations that still import the historical canonical package boundary. Do not use it for new Tigrbl applications or extensions.

## When should I install tigrbl-canon?

Install it only for compatibility migrations that still require `tigrbl_canon` imports. Prefer the current split packages for new work.

## Who is tigrbl-canon for?

Maintainers carrying legacy Tigrbl integrations forward.

## Where does tigrbl-canon fit?

`tigrbl-canon` lives at `pkgs/99_deprecated/tigrbl_canon` and serves legacy compatibility while migrating to current split packages. It is not part of the active facade dependency path.

## How does tigrbl-canon work?

It depends on current split packages and keeps historical import paths available while newer package boundaries own active behavior. It must not depend on the `tigrbl` facade package.


## Install

```bash
uv add tigrbl-canon
```

```bash
pip install tigrbl-canon
```

## Surface Coverage

| Surface | Value |
|---|---|
| PyPI package | [`tigrbl-canon`](https://pypi.org/project/tigrbl-canon/) |
| Repository path | [`pkgs/99_deprecated/tigrbl_canon`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/99_deprecated/tigrbl_canon) |
| Python import root | `tigrbl_canon` |
| Console scripts | none declared |
| Entry points | none declared |
| Optional extras | none declared |
| Legal files | `LICENSE`, `NOTICE` |
| Supported Python | `3.10 | 3.11 | 3.12 | 3.13 | 3.14` |

## What It Owns

`tigrbl-canon` owns the `deprecated legacy compatibility package` boundary. It should be installed only when an older integration still needs the historical `tigrbl_canon` import root during migration.

Implementation orientation:
- `tigrbl_canon`: column/, mapping/

## Public API and Import Surface

- Import roots: `tigrbl_canon`.
- Public symbols: `_DEPRECATION_MESSAGE`.
- Workspace dependencies: [`tigrbl-ops-oltp`](https://pypi.org/project/tigrbl-ops-oltp/), [`tigrbl-base`](https://pypi.org/project/tigrbl-base/), [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/), [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/).
- External runtime dependencies: none declared.

## Usage Examples

### Verify the installed package

```bash
python -m pip show tigrbl-canon
python - <<'PY'
from importlib.metadata import version
print(version("tigrbl-canon"))
PY
```

### Import the compatibility boundary

```python
import tigrbl_canon

print(tigrbl_canon.__name__)
```

### Prefer current split packages for new code

```bash
uv add tigrbl-core tigrbl-base tigrbl-runtime
```

### Audit remaining legacy imports

```bash
rg "tigrbl_canon|tigrbl-canon" .
```

## How To Choose This Package

Choose `tigrbl-canon` only when an existing integration still imports `tigrbl_canon` and cannot migrate immediately. Choose lower-level packages such as [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-base`](https://pypi.org/project/tigrbl-base/), or [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/) when building framework extensions or testing a specific internal boundary.

## Related Packages

- [`tigrbl-ops-oltp`](https://pypi.org/project/tigrbl-ops-oltp/)
- [`tigrbl-base`](https://pypi.org/project/tigrbl-base/)
- [`tigrbl-core`](https://pypi.org/project/tigrbl-core/)
- [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/)
- [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/)

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
- Repository: [pkgs/99_deprecated/tigrbl_canon](https://github.com/tigrbl/tigrbl/tree/master/pkgs/99_deprecated/tigrbl_canon).

## Package-local Boundary

This README is the package-local distribution entry point for `tigrbl-canon`. It answers install, usage, API, ownership, and certification-orientation questions for this package. Broader architectural decisions, release status, and cross-package proof chains remain in the repository-level docs and SSOT registry.

## Certification Status

- Package status: deprecated, inactive compatibility package in the `tigrbl/tigrbl` workspace.
- Governance source: [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json).
- Release evidence: [publish workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml) validates package builds, tests, GitHub release assets, and PyPI publication for managed packages.
- Local certification guard: `pkgs/97_tests/tigrbl_tests/tests/unit/test_package_badges_and_notices.py` verifies every package README keeps the Discord badge, Apache 2.0 badge, explicit Python-version badge, `LICENSE`, and `NOTICE`.
- Scope note: this README documents the package boundary. Runtime feature support remains governed by `.ssot/` entities and the conformance docs linked below.

## License

Licensed under the Apache License, Version 2.0. See `LICENSE`, `NOTICE`, and the official [Apache 2.0 license text](https://www.apache.org/licenses/LICENSE-2.0).
