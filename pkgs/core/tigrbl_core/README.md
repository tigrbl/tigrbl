<div align="center">
<h1>tigrbl-core</h1>
<img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png" alt="Tigrbl logo" width="140"/>
<p><strong>Core Tigrbl framework specifications, decorators, schemas, hooks, operations, and primitives for schema-first APIs.</strong></p>
<a href="https://pypi.org/project/tigrbl-core/"><img src="https://img.shields.io/pypi/v/tigrbl-core?label=PyPI" alt="PyPI version for tigrbl-core"/></a>
<a href="https://pypi.org/project/tigrbl-core/"><img src="https://static.pepy.tech/badge/tigrbl-core" alt="Downloads for tigrbl-core"/></a>
<a href="https://discord.gg/K4YTAPapjR"><img src="https://img.shields.io/badge/Discord-Join%20chat-5865F2?logo=discord&logoColor=white" alt="Discord community for tigrbl-core"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_core/README.md"><img src="https://hits.sh/github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_core/README.md.svg?label=hits" alt="Repository hits for tigrbl-core README"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%2C%203.11%2C%203.12%2C%203.13%2C%203.14-3776ab" alt="Python versions 3.10 | 3.11 | 3.12 | 3.13 | 3.14 for tigrbl-core"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/docs/README.md"><img src="https://img.shields.io/badge/workspace-core-1f6feb" alt="Workspace group for tigrbl-core"/></a>
</div>

## What is tigrbl-core?

Core Tigrbl framework specifications, decorators, schemas, hooks, operations, and primitives for schema-first APIs.

## Why use tigrbl-core?

Use it when you need this foundational Tigrbl layer directly as a small, focused dependency.

## When should I install tigrbl-core?

Install it for extension packages, package-local tests, or internals that need this boundary without the whole facade.

## Who is tigrbl-core for?

Framework maintainers, extension authors, and advanced users composing Tigrbl from split packages.

## Where does tigrbl-core fit?

`tigrbl-core` lives at `pkgs/core/tigrbl_core` and serves a focused layer in the split Tigrbl framework.

## How does tigrbl-core work?

It owns a narrow layer in the split workspace and is consumed by higher-level packages through explicit dependencies.

## Certification Status

- Package status: governed package in the `tigrbl/tigrbl` workspace.
- Governance source: [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json).
- Release evidence: [publish workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml) validates package builds, tests, GitHub release assets, and PyPI publication for managed packages.
- Local certification guard: `pkgs/core/tigrbl_tests/tests/unit/test_package_badges_and_notices.py` verifies every package README keeps the Discord badge, Apache 2.0 badge, explicit Python-version badge, `LICENSE`, and `NOTICE`.
- Scope note: this README documents the package boundary. Runtime feature support remains governed by `.ssot/` entities and the conformance docs linked below.

## Install

```bash
uv add tigrbl-core
```

```bash
pip install tigrbl-core
```

## Surface Coverage

| Surface | Value |
|---|---|
| PyPI package | [`tigrbl-core`](https://pypi.org/project/tigrbl-core/) |
| Repository path | [`pkgs/core/tigrbl_core`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_core) |
| Python import root | `tigrbl_core` |
| Console scripts | none declared |
| Entry points | none declared |
| Optional extras | none declared |
| Legal files | `LICENSE`, `NOTICE` |
| Supported Python | `3.10, 3.11, 3.12, 3.13, 3.14` |

## What It Owns

`tigrbl-core` owns the `foundational framework package` boundary. It should be installed when you need this package's focused responsibility without assuming every other Tigrbl workspace package is present.

Implementation orientation:
- `tigrbl_core`: _spec/, canonical_json, config/, core/, op/, schema/

Package catalog:
- `tigrbl_core/_spec/`: typed, serializable specifications for aliases, apps, bindings, columns, data types, docs, engines, fields, hooks, IO, middleware, operations, paths, requests, responses, routers, schemas, sessions, storage, tables, and table registries.
- `tigrbl_core/config/`: constants, defaults, resolver logic, and engine traversal helpers used when app, router, table, column, op, and request layers are merged.
- `tigrbl_core/op/`: canonical operation names, operation collection, and operation typing helpers.
- `tigrbl_core/schema/`: dynamic schema construction, schema cache helpers, extras handling, list-parameter support, schema JSON helpers, and `get_schema` access.
- `tigrbl_core/canonical_json.py`: deterministic JSON output used by docs, registry-like payloads, tests, and conformance artifacts.

## Public API and Import Surface

- Import roots: `tigrbl_core`.
- Public symbols: public surface is module-oriented; import the package boundary and inspect submodules as needed.
- Workspace dependencies: [`tigrbl-typing`](https://pypi.org/project/tigrbl-typing/).
- External runtime dependencies: `pydantic>=2.10,<3`, `pyyaml`, `tomli-w`, `tomli>=2.0.1; python_version < '3.11'`.

## Specification Model

The core package is the contract layer. It defines the vocabulary consumed by base abstractions, concrete adapters, atoms, kernel planning, runtime routing, docs generation, and the public facade. Most application code should not construct these specs manually; application code should normally use facade decorators and shortcuts. Extension packages use the specs when they need deterministic, testable configuration objects.

| Spec family | What it describes |
|---|---|
| `AppSpec`, `RouterSpec`, `TableSpec` | Container-level framework configuration and inheritance points. |
| `ColumnSpec`, `FieldSpec`, data type specs | Field semantics, validation, storage, schema projection, and data-type lowering. |
| `OpSpec` and op utilities | Operation name, alias, arity, binding, handler, schema, hook, response, and runtime intent. |
| `HookSpec` and hook types | Hook targets, phases, predicates, ordering, and callable registration shape. |
| `SchemaSpec`, `RequestSpec`, `ResponseSpec`, `IoSpec` | Input/output envelope behavior, request extraction, response shaping, and Pydantic model generation. |
| `BindingSpec` | REST, JSON-RPC, stream, SSE, WebSocket, WSS, and WebTransport binding metadata. |
| `EngineSpec`, `SessionSpec`, `StorageSpec` | Engine/provider/session/storage configuration without importing concrete engine implementations. |
| `DocsSpec`, `PathSpec`, `MiddlewareSpec` | Documentation projection, route paths, and middleware configuration. |

## Operation Semantics

`tigrbl_core.op.canonical.DEFAULT_CANON_VERBS` is the default CRUD set:

```text
create, read, update, replace, delete, list, clear
```

Tables can change canonical wiring through mode/include/exclude attributes or a `should_wire_canonical(op)` helper. Core only decides whether an operation is part of the desired specification. Concrete packages and operation packs supply the actual handlers and routing behavior.

Use this package when you need to inspect or build operation specs before runtime compilation. Use `tigrbl` when you simply want a working app surface.

## Binding and Transport Semantics

`BindingSpec` keeps four concerns distinct:

- protocol or binding kind, such as HTTP REST, HTTP JSON-RPC, HTTP stream, SSE, WebSocket, WSS, or WebTransport;
- exchange shape, such as request/response, server stream, bidirectional stream, client stream, server stream, session, or datagram;
- framing, such as JSON, JSON-RPC, SSE, WebSocket text, stream framing, or WebTransport outer framing;
- runtime lane metadata, especially for WebTransport session, stream, and datagram behavior.

This separation is deliberate. Extension authors should not collapse protocol support into a single string or infer framing from the transport name. Invalid combinations should remain explicit validation failures so runtime behavior is fail-closed.

## Configuration Precedence

Core resolvers use this precedence pattern:

```text
request override > operation spec > column spec > table spec > router spec > app spec > defaults
```

The most specific layer wins. Keep default policy broad, then narrow behavior by table, column, and operation. Avoid hidden mutation of spec objects after a runtime plan has been compiled; build a fresh spec or invalidate the relevant cache when behavior truly changes.

## Schema Construction

Schema helpers build operation-specific request and response models from table metadata, column specs, request/response extras, list-parameter rules, and op-level configuration. `get_schema(...)` is the stable way to retrieve the generated model for a table operation and direction. Prefer it over hand-writing duplicate Pydantic envelopes when data belongs to a Tigrbl operation.

Best practices for schema work:
- Keep storage fields, wire fields, and virtual extras separate.
- Put reusable schema behavior in table or column specs; reserve op specs for operation-specific differences.
- Use canonical JSON helpers when writing deterministic docs or evidence artifacts.
- Treat generated schemas as projections of the specs, not as the source of truth.

## Extension Guidance

- Depend on `tigrbl-core` when you need spec classes, op collection, schema generation, or config resolution without concrete app/router/runtime imports.
- Keep specs serializable and deterministic. Do not attach live database sessions, request objects, or transport handles to core specs.
- Validate protocol and binding assumptions in core or kernel-facing tests before adding runtime behavior.
- Keep application-facing convenience APIs in `tigrbl` or `tigrbl-concrete`; keep cross-package contracts here.

Authoring BCP for this boundary:
- Do treat `ColumnSpec`, `FieldSpec`, `OpSpec`, `HookSpec`, `SchemaSpec`, `BindingSpec`, `EngineSpec`, `SessionSpec`, and related specs as the contract vocabulary that other Tigrbl packages consume.
- Do keep specs independent of FastAPI, Starlette, SQLAlchemy sessions, live request objects, and transport handles.
- Do not move application route authoring, direct database calls, concrete engine creation, or runtime dispatch side effects into `tigrbl-core`.
- Avoid duplicating spec fields in helper classes or generated schemas. Specs should remain the source that schema, docs, kernel, runtime, base, concrete, and facade layers project from.

## Usage Examples

### Verify the installed package

```bash
python -m pip show tigrbl-core
python - <<'PY'
from importlib.metadata import version
print(version("tigrbl-core"))
PY
```

### Import the package boundary

```python
import importlib

module = importlib.import_module("tigrbl_core._spec")
print(module.__name__)
```

### Inspect available modules

```python
import importlib
import pkgutil

module = importlib.import_module("tigrbl_core._spec")
for info in pkgutil.iter_modules(getattr(module, "__path__", [])):
    print(info.name)
```

### Use with the facade when building applications

```bash
uv add tigrbl tigrbl-core
python - <<'PY'
import tigrbl
print(tigrbl.__name__)
PY
```

## How To Choose This Package

Choose `tigrbl-core` when the quick-answer table matches your use case. Choose [`tigrbl`](https://pypi.org/project/tigrbl/) instead when you want the full public facade. Choose a lower-level package such as [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-base`](https://pypi.org/project/tigrbl-base/), or [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/) when you are building framework extensions or testing a specific internal boundary.

## Related Packages

- [`tigrbl-typing`](https://pypi.org/project/tigrbl-typing/)
- [`tigrbl`](https://pypi.org/project/tigrbl/)
- [`tigrbl-base`](https://pypi.org/project/tigrbl-base/)
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
- Repository: [pkgs/core/tigrbl_core](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_core).

## Package-local Boundary

This file is a package-local distribution entry point. This README is the package-local distribution entry point for `tigrbl-core`. It answers install, usage, API, ownership, and certification-orientation questions for this package. Broader architectural decisions, release status, and cross-package proof chains remain in the repository-level docs and SSOT registry.

## License

Licensed under the Apache License, Version 2.0. See `LICENSE`, `NOTICE`, and the official [Apache 2.0 license text](https://www.apache.org/licenses/LICENSE-2.0).
