<div align="center">
<h1>tigrbl-base</h1>
<img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png" alt="Tigrbl logo" width="140"/>
<p><strong>Base contract package for Tigrbl apps, routers, tables, sessions, middleware, requests, responses, bindings, and engine interfaces.</strong></p>
<a href="https://pypi.org/project/tigrbl-base/"><img src="https://img.shields.io/pypi/v/tigrbl-base?label=PyPI" alt="PyPI version for tigrbl-base"/></a>
<a href="https://pypi.org/project/tigrbl-base/"><img src="https://static.pepy.tech/badge/tigrbl-base" alt="Downloads for tigrbl-base"/></a>
<a href="https://discord.gg/K4YTAPapjR"><img src="https://img.shields.io/badge/Discord-Join%20chat-5865F2?logo=discord&logoColor=white" alt="Discord community for tigrbl-base"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/20_base/tigrbl_base/README.md"><img src="https://hits.sh/github.com/tigrbl/tigrbl/blob/master/pkgs/20_base/tigrbl_base/README.md.svg?label=hits" alt="Repository hits for tigrbl-base README"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%2C%203.11%2C%203.12%2C%203.13%2C%203.14-3776ab" alt="Python versions 3.10 | 3.11 | 3.12 | 3.13 | 3.14 for tigrbl-base"/></a>
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

`tigrbl-base` lives at `pkgs/20_base/tigrbl_base` and serves a focused layer in the split Tigrbl framework.

## How does tigrbl-base work?

It owns a narrow layer in the split workspace and is consumed by higher-level packages through explicit dependencies.


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
| Repository path | [`pkgs/20_base/tigrbl_base`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/20_base/tigrbl_base) |
| Python import root | `tigrbl_base` |
| Console scripts | none declared |
| Entry points | none declared |
| Optional extras | none declared |
| Legal files | `LICENSE`, `NOTICE` |
| Supported Python | `3.10, 3.11, 3.12, 3.13, 3.14` |

## What It Owns

`tigrbl-base` owns the `foundational framework package` boundary. It should be installed when you need this package's focused responsibility without assuming every other Tigrbl workspace package is present.

Implementation orientation:
- `tigrbl_base`: _base/, column/

Package catalog:
- `_base/_app_base.py`, `_router_base.py`, and `_table_base.py`: abstract app, router, and table behavior used by concrete framework classes.
- `_base/_op_base.py`, `_binding_base.py`, `_rest_map.py`, and `_rpc_map.py`: operation, binding, REST mapping, and JSON-RPC mapping contracts.
- `_base/_schema_base.py`, `_request_base.py`, `_response_base.py`, `_headers_base.py`, and `_middleware_base.py`: request/response/schema/header/middleware abstractions.
- `_base/_engine_base.py`, `_engine_provider_base.py`, `_session_abc.py`, `_session_base.py`, and `_storage.py`: engine, provider, session, and storage interfaces.
- `_base/_column_base.py`, `_table_registry_base.py`, `_alias_base.py`, `_hook_base.py`, `_security_base.py`, and `_datatype_lowering.py`: table metadata, aliasing, hook/security contracts, and data-type lowering hooks.
- `_base/_assembly.py` and `_mapping_access.py`: assembly and mapping helpers for concrete implementations.
- `column/infer`: column inference planning, JSON hint handling, type interpretation, and utility helpers.

## Public API and Import Surface

- Import roots: `tigrbl_base`.
- Public symbols: public surface is module-oriented; import the package boundary and inspect submodules as needed.
- Workspace dependencies: [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/).
- External runtime dependencies: `sqlalchemy>=2.0`, `pydantic>=2.0`.

## Abstraction Semantics

`tigrbl-base` is the abstract contract layer between core specs and concrete implementations. It is useful when you need interface behavior without importing the facade or concrete ASGI/application classes.

The package answers questions such as:

- What must an app/router/table expose for assembly?
- How do REST and JSON-RPC maps represent operation bindings?
- What does a request, response, middleware, hook, session, engine provider, or storage adapter need to provide?
- How should column metadata be inferred before a concrete table class lowers it into ORM/schema/runtime behavior?

It should not own route registration side effects, transport IO, database engine construction, or runtime execution. Those belong in `tigrbl-concrete`, engine packages, kernel/runtime packages, or the facade.

## Base Contracts by Area

| Area | Base responsibility |
|---|---|
| App/router/table | Provide shared assembly, inclusion, registration, and metadata contracts. |
| Operations and bindings | Represent operation maps, REST maps, RPC maps, alias behavior, and binding access. |
| Schema and IO | Provide base shape for request/response/schema objects without deciding concrete rendering. |
| Engine/session/storage | Define provider/session/storage contracts so concrete engines can plug in consistently. |
| Hooks/security/middleware | Provide registration and interface surfaces for lifecycle customization and request policy. |
| Columns | Infer and lower type information while keeping spec-level intent separate from concrete ORM wiring. |

## Column Inference

`tigrbl_base.column.infer` supports the framework's schema-first and table-first workflows. It helps interpret Python typing, JSON hints, planning metadata, and column options before concrete packages lower them into SQLAlchemy/Pydantic/runtime representations.

Best practices for column inference:
- Keep inference deterministic; the same type hints and config should produce the same plan.
- Keep storage intent separate from wire-schema intent.
- Preserve explicit user configuration over inferred defaults.
- Add tests for ambiguous type handling instead of silently guessing.

## Extension Guidance

- Depend on `tigrbl-base` when you are writing concrete adapters, engine adapters, or framework tests that need abstract contracts.
- Do not import `tigrbl` facade classes here; base should remain lower than the public facade.
- Keep methods small and contract-oriented. Put operational side effects in concrete implementations or atoms.
- Treat base classes as compatibility surfaces. Renaming or tightening a method affects all concrete packages.
- Prefer composition with `tigrbl-core` specs rather than duplicating spec fields in base classes.

Authoring BCP for this boundary:
- Do use `tigrbl-base` for abstract app/router/table/session/request/response/binding/security/middleware/storage contracts and column inference behavior.
- Do keep column inference deterministic and spec-driven before concrete packages lower intent into ORM, schema, runtime, or docs behavior.
- Do not make `tigrbl-base` the public application import path for normal service code.
- Do not put route registration side effects, direct database transaction calls, concrete engine construction, FastAPI/Starlette route objects, or runtime execution into this package.
- Avoid treating SQLAlchemy materialization as the source of truth here. Base may prepare and validate metadata, but reusable field behavior should remain represented by Tigrbl specs.

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
- [Next steps](https://github.com/tigrbl/tigrbl/blob/master/docs/conformance/NEXT_STEPS.md)
- [Documentation pointers](https://github.com/tigrbl/tigrbl/blob/master/docs/governance/DOC_POINTERS.md)
- [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json)
- [Release workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml)

## Support

- Community: [Discord](https://discord.gg/K4YTAPapjR).
- Issues: [GitHub Issues](https://github.com/tigrbl/tigrbl/issues).
- Repository: [pkgs/20_base/tigrbl_base](https://github.com/tigrbl/tigrbl/tree/master/pkgs/20_base/tigrbl_base).

## Package-local Boundary

This file is a package-local distribution entry point. This README is the package-local distribution entry point for `tigrbl-base`. It answers install, usage, API, ownership, and certification-orientation questions for this package. Broader architectural decisions, release status, and cross-package proof chains remain in the repository-level docs and SSOT registry.

## Certification Status

- Package status: governed package in the `tigrbl/tigrbl` workspace.
- Governance source: [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json).
- Release evidence: [publish workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml) validates package builds, tests, GitHub release assets, and PyPI publication for managed packages.
- Local certification guard: `pkgs/97_tests/tigrbl_tests/tests/unit/test_package_badges_and_notices.py` verifies every package README keeps the Discord badge, Apache 2.0 badge, explicit Python-version badge, `LICENSE`, and `NOTICE`.
- Scope note: this README documents the package boundary. Runtime feature support remains governed by `.ssot/` entities and the conformance docs linked below.

## License

Licensed under the Apache License, Version 2.0. See `LICENSE`, `NOTICE`, and the official [Apache 2.0 license text](https://www.apache.org/licenses/LICENSE-2.0).
