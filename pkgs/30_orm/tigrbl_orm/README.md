<div align="center">
<h1>tigrbl-orm</h1>
<img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png" alt="Tigrbl logo" width="140"/>
<p><strong>SQLAlchemy ORM tables, mixins, columns, model helpers, and persistence primitives for Tigrbl applications.</strong></p>
<a href="https://pypi.org/project/tigrbl-orm/"><img src="https://img.shields.io/pypi/v/tigrbl-orm?label=PyPI" alt="PyPI version for tigrbl-orm"/></a>
<a href="https://pypi.org/project/tigrbl-orm/"><img src="https://static.pepy.tech/badge/tigrbl-orm" alt="Downloads for tigrbl-orm"/></a>
<a href="https://discord.gg/K4YTAPapjR"><img src="https://img.shields.io/badge/Discord-Join%20chat-5865F2?logo=discord&logoColor=white" alt="Discord community for tigrbl-orm"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/30_orm/tigrbl_orm/README.md"><img src="https://hits.sh/github.com/tigrbl/tigrbl/blob/master/pkgs/30_orm/tigrbl_orm/README.md.svg?label=hits" alt="Repository hits for tigrbl-orm README"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-3776ab" alt="Python versions 3.10 | 3.11 | 3.12 | 3.13 | 3.14 for tigrbl-orm"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/docs/README.md"><img src="https://img.shields.io/badge/workspace-core-1f6feb" alt="Workspace group for tigrbl-orm"/></a>
</div>

## What is tigrbl-orm?

SQLAlchemy ORM tables, mixins, columns, model helpers, and persistence primitives for Tigrbl applications.

## Why use tigrbl-orm?

Use it when you need this foundational Tigrbl layer directly as a small, focused dependency.

## When should I install tigrbl-orm?

Install it for extension packages, package-local tests, or internals that need this boundary without the whole facade.

## Who is tigrbl-orm for?

Framework maintainers, extension authors, and advanced users composing Tigrbl from split packages.

## Where does tigrbl-orm fit?

`tigrbl-orm` lives at `pkgs/30_orm/tigrbl_orm` and serves a focused layer in the split Tigrbl framework.

## How does tigrbl-orm work?

It owns a narrow layer in the split workspace and is consumed by higher-level packages through explicit dependencies.


## Install

```bash
uv add tigrbl-orm
```

```bash
pip install tigrbl-orm
```

## Surface Coverage

| Surface | Value |
|---|---|
| PyPI package | [`tigrbl-orm`](https://pypi.org/project/tigrbl-orm/) |
| Repository path | [`pkgs/30_orm/tigrbl_orm`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/30_orm/tigrbl_orm) |
| Python import root | `tigrbl_orm` |
| Console scripts | none declared |
| Entry points | none declared |
| Optional extras | none declared |
| Legal files | `LICENSE`, `NOTICE` |
| Supported Python | `3.10 | 3.11 | 3.12 | 3.13 | 3.14` |

## What It Owns

`tigrbl-orm` owns the `foundational framework package` boundary. It should be installed when you need this package's focused responsibility without assuming every other Tigrbl workspace package is present.

Implementation orientation:
- `tigrbl_orm`: orm/

## Public API and Import Surface

- Import roots: `tigrbl_orm`.
- Public symbols: public surface is module-oriented; import the package boundary and inspect submodules as needed.
- Workspace dependencies: none declared.
- External runtime dependencies: `sqlalchemy>=2.0`.

## Usage Examples

### Verify the installed package

```bash
python -m pip show tigrbl-orm
python - <<'PY'
from importlib.metadata import version
print(version("tigrbl-orm"))
PY
```

### Import the package boundary

```python
import importlib

module = importlib.import_module("tigrbl_orm.orm")
print(module.__name__)
```

### Inspect available modules

```python
import importlib
import pkgutil

module = importlib.import_module("tigrbl_orm.orm")
for info in pkgutil.iter_modules(getattr(module, "__path__", [])):
    print(info.name)
```

### Use with the facade when building applications

```bash
uv add tigrbl tigrbl-orm
python - <<'PY'
import tigrbl
print(tigrbl.__name__)
PY
```

## How To Choose This Package

Choose `tigrbl-orm` when the quick-answer table matches your use case. Choose [`tigrbl`](https://pypi.org/project/tigrbl/) instead when you want the full public facade. Choose a lower-level package such as [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-base`](https://pypi.org/project/tigrbl-base/), or [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/) when you are building framework extensions or testing a specific internal boundary.

## Convenient Authoring Path and Best Current Practice (BCP)

`tigrbl-orm` is the SQLAlchemy-facing implementation boundary for Tigrbl table and persistence helpers. Normal application documentation should still lead with the `tigrbl` facade, Tigrbl table/column helpers, and Tigrbl specs.

### Keep ORM usage boundary-owned

- Avoid: Exposing implementation-only ORM helpers as facade-level guidance unless the package boundary is explicit.
- Do: Use this package when implementing or testing ORM helpers, table mixins, persistence primitives, and SQLAlchemy-facing compatibility behavior.
- Why: SQLAlchemy is useful inside the storage boundary, while application users still get the more convenient Tigrbl facade contract.

### Keep specs authoritative before ORM materialization

- Avoid: Duplicating field behavior across ORM declarations and Tigrbl specs.
- Do: Keep ORM behavior aligned with Tigrbl table, column, datatype, storage, IO, and operation specs.
- Why: The spec layer is the reusable source for behavior that must project into storage, validation, runtime, hooks, diagnostics, and docs.

### Do not teach raw ORM declarations as application style

- Do not: Present raw SQLAlchemy `mapped_column(...)` or `Column(...)` as the preferred application authoring surface when Tigrbl column helpers or specs can express the behavior.
- Do: Let Tigrbl specs describe reusable field and operation intent before ORM materialization.
- Why: Raw ORM declarations are only one lowering target and cannot carry the full Tigrbl storage, IO, validation, docs, hook, and runtime contract.

### Do not move application behavior into this boundary

- Do not: Put application route authoring, FastAPI/Starlette route objects, ad-hoc engine construction in handlers, or direct transaction control in this package's public examples.
- Do: Keep application-facing examples on the `tigrbl` facade and keep this README focused on the ORM implementation boundary.
- Why: This keeps routes, engines, transactions, schemas, hooks, diagnostics, and runtime planning owned by the packages that govern those behaviors.

## Related Packages

- [`tigrbl`](https://pypi.org/project/tigrbl/)
- [`tigrbl-core`](https://pypi.org/project/tigrbl-core/)
- [`tigrbl-base`](https://pypi.org/project/tigrbl-base/)
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
- Repository: [pkgs/30_orm/tigrbl_orm](https://github.com/tigrbl/tigrbl/tree/master/pkgs/30_orm/tigrbl_orm).

## Package-local Boundary

This README is the package-local distribution entry point for `tigrbl-orm`. It answers install, usage, API, ownership, and certification-orientation questions for this package. Broader architectural decisions, release status, and cross-package proof chains remain in the repository-level docs and SSOT registry.

## Certification Status

- Package status: governed package in the `tigrbl/tigrbl` workspace.
- Governance source: [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json).
- Release evidence: [publish workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml) validates package builds, tests, GitHub release assets, and PyPI publication for managed packages.
- Local certification guard: `pkgs/97_tests/tigrbl_tests/tests/unit/test_package_badges_and_notices.py` verifies every package README keeps the Discord badge, Apache 2.0 badge, explicit Python-version badge, `LICENSE`, and `NOTICE`.
- Scope note: this README documents the package boundary. Runtime feature support remains governed by `.ssot/` entities and the conformance docs linked below.

## License

Licensed under the Apache License, Version 2.0. See `LICENSE`, `NOTICE`, and the official [Apache 2.0 license text](https://www.apache.org/licenses/LICENSE-2.0).
