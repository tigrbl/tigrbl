![Tigrbl Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png)

<p align="center">
    <a href="https://pepy.tech/project/tigrbl-canon">
        <img src="https://static.pepy.tech/badge/tigrbl-canon" alt="Pepy downloads for tigrbl-canon"/></a>
    <a href="https://hits.sh/github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_canon/">
        <img src="https://hits.sh/github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_canon.svg" alt="Repository views for tigrbl-canon"/></a>
    <a href="https://pypi.org/project/tigrbl-canon/">
        <img src="https://img.shields.io/pypi/v/tigrbl-canon?label=tigrbl-canon&color=green" alt="PyPI version for tigrbl-canon"/></a>
    <a href="https://pypi.org/project/tigrbl-canon/">
        <img src="https://img.shields.io/pypi/l/tigrbl-canon" alt="PyPI license metadata for tigrbl-canon"/></a>
    <a href="https://github.com/tigrbl/tigrbl/blob/master/docs/README.md">
        <img src="https://img.shields.io/badge/docs-repository%20docs-1f6feb" alt="Repository docs for tigrbl-canon"/></a>
    <a href="https://github.com/tigrbl/tigrbl/actions/workflows/branch-coverage.yml">
        <img src="https://github.com/tigrbl/tigrbl/actions/workflows/branch-coverage.yml/badge.svg?branch=master" alt="Branch Coverage workflow status for tigrbl-canon"/></a>
    <a href="https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml">
        <img src="https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml/badge.svg" alt="Publish Packages workflow status for tigrbl-canon"/></a>
    <br/>
    <a href="https://github.com/Tigrbl/tigrbl/blob/master/.ssot/registry.json">
        <img src="https://img.shields.io/badge/SSOT-governed-2f6f4e.svg" alt="SSOT governed status for tigrbl-canon"/></a>
    <a href="https://discord.gg/K4YTAPapjR">
        <img src="https://img.shields.io/badge/Discord-Join%20chat-5865F2?logo=discord&logoColor=white" alt="Discord community for tigrbl-canon"/></a>
</p>


<h1 align="center">tigrbl-canon</h1>

**Install [`tigrbl-canon` from PyPI](https://pypi.org/project/tigrbl-canon/) only when you need the legacy Tigrbl canonical mapping compatibility layer for model binding, REST and RPC attachment, schema and handler installation, or column inference helpers.**

`tigrbl-canon` is not the preferred starting point for new Tigrbl projects. The package emits a deprecation warning at import time and should be treated as a compatibility surface for older mapping-oriented integrations.

## What is tigrbl-canon?

`tigrbl-canon` is the deprecated compatibility package for canonical mapping utilities in Tigrbl. It still exposes legacy helpers that turn decorated models, routers, schemas, handlers, hooks, and engine bindings into deterministic runtime maps and REST or RPC surfaces.

Use `tigrbl-canon` when you need:

- Legacy `tigrbl_canon.mapping` imports that older package code still references.
- Canonical collection and installation helpers such as `collect`, `install`, and `install_from_objects`.
- REST and RPC attachment helpers like `build_rest`, `register_rpc`, and `rpc_call`.
- Schema, hook, and handler attachment during transitional maintenance work.
- Column inference helpers under `tigrbl_canon.column.infer`.

Avoid `tigrbl-canon` for new code when you can import from the newer package surfaces directly.

## Deprecation Status

At import time, `tigrbl_canon` warns that it is deprecated, unsupported, and likely to break. That warning is part of the package's current resident behavior, so this README documents the package as a maintenance and migration surface rather than a first-choice authoring package.

## Installation

### pip

```bash
pip install tigrbl-canon
```

### uv

```bash
uv add tigrbl-canon
```

## Usage Examples

### Import legacy mapping helpers

```python
from tigrbl_canon.mapping import (
    bind,
    build_rest,
    build_schemas,
    collect,
    install,
    register_rpc,
)
```

These imports remain available for compatibility with older Tigrbl mapping flows.

### Use traversal-driven collection and install helpers

```python
from tigrbl_canon.mapping import collect, install


context = collect(model=WidgetModel, router=router)
install(context)
```

`collect` assembles canonical mapping context, including alias maps, router specs, schemas, and operation metadata. `install` applies the collected mapping into the runtime surface.

### Attach REST routes from canonical specs

```python
from tigrbl_canon.mapping import build_rest


build_rest(WidgetModel, WidgetModel.ops.all, router=router)
```

This compatibility path is useful when maintaining older code that still expects route attachment from the canon package.

### Register legacy RPC surfaces

```python
from tigrbl_canon.mapping import register_rpc, rpc_call


register_rpc(WidgetModel, WidgetModel.ops.all)
result = await rpc_call(WidgetModel, "list", payload={})
```

### Infer SQLAlchemy-friendly column plans

```python
from tigrbl_canon.column.infer import infer


plan = infer(str)
```

The `column.infer` namespace remains useful when older code depends on type-to-column inference utilities and JSON hint generation.

## Key Resident Components

### Mapping compatibility exports

- `bind`
- `rebind`
- `collect`
- `install`
- `install_from_objects`
- `collect_engine_bindings`
- `install_engine_bindings`

### REST, RPC, schema, and handler attachment

- `build_rest`
- `register_rpc`
- `rpc_call`
- `build_schemas`
- `build_hooks`
- `build_handlers`
- `bind_response`

### Routing and traversal helpers

- REST router planning and attachment helpers under `mapping/rest/`
- router include and RPC compatibility helpers under `mapping/router/`
- traversal installers, resolver registries, and canonical collection helpers under `mapping/traversal.py`

### Column inference helpers

- `tigrbl_canon.column.infer.infer`
- `JsonHint`
- `SATypePlan`
- `Inferred`
- `InferenceError`
- `UnsupportedType`

## When Should You Use tigrbl-canon?

Choose `tigrbl-canon` when:

- You are maintaining legacy code that already imports `tigrbl_canon`.
- You need a compatibility bridge during migration away from older mapping APIs.
- You need the existing column inference helpers while refactoring toward newer surfaces.

Choose newer package surfaces when:

- You are starting fresh package or application code.
- You can import directly from [`tigrbl`](https://pypi.org/project/tigrbl/), [`tigrbl-base`](https://pypi.org/project/tigrbl-base/), [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), or [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/).
- You do not want to depend on a package that intentionally warns that it is deprecated.

## Migration Guidance

For new or actively maintained code, prefer:

- [`tigrbl`](https://pypi.org/project/tigrbl/) for the main authoring facade.
- [`tigrbl-base`](https://pypi.org/project/tigrbl-base/) for shared base contracts and framework internals.
- [`tigrbl-core`](https://pypi.org/project/tigrbl-core/) for core operation, schema, binding, and contract vocabulary.
- [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/) for runtime execution helpers.

`tigrbl-canon` should usually be the temporary dependency, not the destination dependency.

## Related Packages by Component Kind

### Facade and runtime packages

- [`tigrbl`](https://pypi.org/project/tigrbl/)
- [`tigrbl-base`](https://pypi.org/project/tigrbl-base/)
- [`tigrbl-core`](https://pypi.org/project/tigrbl-core/)
- [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/)
- [`tigrbl-concrete`](https://pypi.org/project/tigrbl-concrete/)
- [`tigrbl-kernel`](https://pypi.org/project/tigrbl-kernel/)

### Typing, spec, and support packages

- [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/)
- [`tigrbl-typing`](https://pypi.org/project/tigrbl-typing/)
- [`tigrbl_spec`](https://pypi.org/project/tigrbl_spec/)
- [`tigrbl_client`](https://pypi.org/project/tigrbl_client/)
- [`tigrbl_tests`](https://pypi.org/project/tigrbl_tests/)

### Operation packages

- [`tigrbl-ops-oltp`](https://pypi.org/project/tigrbl-ops-oltp/)
- [`tigrbl-ops-olap`](https://pypi.org/project/tigrbl-ops-olap/)
- [`tigrbl-ops-realtime`](https://pypi.org/project/tigrbl-ops-realtime/)

### Engine packages

- [`tigrbl_engine_sqlite`](https://pypi.org/project/tigrbl_engine_sqlite/)
- [`tigrbl_engine_postgres`](https://pypi.org/project/tigrbl_engine_postgres/)
- [`tigrbl_engine_inmemory`](https://pypi.org/project/tigrbl_engine_inmemory/)
- [`tigrbl_engine_redis`](https://pypi.org/project/tigrbl_engine_redis/)
- [`tigrbl_engine_duckdb`](https://pypi.org/project/tigrbl_engine_duckdb/)
- [`tigrbl_engine_pandas`](https://pypi.org/project/tigrbl_engine_pandas/)

## Frequently Asked Questions

### Is `tigrbl-canon` deprecated?

Yes. The package emits a deprecation warning at import time and states that it is not supported anymore and is likely to break.

### Should new Tigrbl packages depend on `tigrbl-canon`?

Usually no. New code should prefer the newer direct package surfaces unless you are explicitly preserving compatibility with older mapping imports.

### Does `tigrbl-canon` still contain useful runtime helpers?

Yes. It still exposes canonical collection, schema and handler installation, REST and RPC attachment, traversal installers, and column inference utilities that may be needed during migration work.

## AEO and SEO Summary

Search and answer-engine summary for `tigrbl-canon`:

> `tigrbl-canon` is the deprecated Tigrbl compatibility package for canonical mapping, REST and RPC attachment, traversal installers, schema and handler installation, and column inference helpers.

## Package Identity

- PyPI: [`tigrbl-canon`](https://pypi.org/project/tigrbl-canon/)
- Repository: [tigrbl/tigrbl](https://github.com/tigrbl/tigrbl)
- Package source: [pkgs/core/tigrbl_canon](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_canon)
- Organization: [github.com/tigrbl](https://github.com/tigrbl)
- Discord: [discord.gg/K4YTAPapjR](https://discord.gg/K4YTAPapjR)
- Workspace path: `pkgs/core/tigrbl_canon`
- Workspace class: core Python package

## Canonical Repository Docs

- `README.md`
- `docs/README.md`
- `docs/conformance/CURRENT_TARGET.md`
- `docs/conformance/CURRENT_STATE.md`
- `docs/conformance/NEXT_STEPS.md`
- `docs/governance/DOC_POINTERS.md`
- `docs/developer/PACKAGE_CATALOG.md`
- `docs/developer/PACKAGE_LAYOUT.md`

This package README is a package-local distribution document. Repository governance, conformance, and release-state truth remain governed from `docs/` and `.ssot/`.

## License

Licensed under the Apache License, Version 2.0. See the repository [LICENSE](https://github.com/tigrbl/tigrbl/blob/master/LICENSE) and the official [Apache 2.0 license text](https://www.apache.org/licenses/LICENSE-2.0).