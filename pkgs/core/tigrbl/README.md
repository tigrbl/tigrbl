<div align="center">
<h1>tigrbl</h1>
<img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png" alt="Tigrbl logo" width="140"/>
<p><strong>Schema-first ASGI framework for REST and JSON-RPC APIs with OpenAPI, OpenRPC, SQLAlchemy, typed validation, hooks, and engine plugins.</strong></p>
<a href="https://pypi.org/project/tigrbl/"><img src="https://img.shields.io/pypi/v/tigrbl?label=PyPI" alt="PyPI version for tigrbl"/></a>
<a href="https://pypi.org/project/tigrbl/"><img src="https://static.pepy.tech/badge/tigrbl" alt="Downloads for tigrbl"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl/README.md"><img src="https://hits.sh/github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl/README.md.svg?label=hits" alt="Repository hits for tigrbl README"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%20to%203.15-3776ab" alt="Python requirement for tigrbl"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/docs/README.md"><img src="https://img.shields.io/badge/workspace-core-1f6feb" alt="Workspace group for tigrbl"/></a>
</div>

## Install

```bash
uv add tigrbl
```

```bash
pip install tigrbl
```

Optional extras declared in `pyproject.toml`:

```bash
pip install "tigrbl[postgres, servers, templates, tests]"
```

## What It Owns

`tigrbl` owns the public facade boundary for the Python workspace, re-exporting the author-facing app, router, ORM, decorator, security, and CLI surfaces while delegating resident behavior to split packages. Key implementation roots include `examples` with `swarmauri_tigrbl_bridge, swarmauri_tigrbl_bridge_smooth`; `tigrbl` with `__main__, canonical_json, cli, config/, ddl/, decorators/`.

## Use It When

Use `tigrbl` when you want the public Python authoring surface in one install target: app composition, schema-first routing, REST and JSON-RPC projection, docs generation, and CLI workflow.

## Public Surface

- `tigrbl` exposes `import_module, extend_path, APIKey, Alias, App, BackgroundTask, Binding, BindingRegistry`.
- Console scripts: `tigrbl`.

## Internal Layout

- Workspace path: `pkgs/core/tigrbl`.
- Package class: `facade package`.
- Python requirement: `>=3.10,<3.15`.
- `examples` modules: `swarmauri_tigrbl_bridge, swarmauri_tigrbl_bridge_smooth`.
- `tigrbl` modules: `__main__, canonical_json, cli, config/, ddl/, decorators/, engine/, factories/, hook/, middlewares/`.

## Dependency Surface

- Workspace package dependencies: [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-base`](https://pypi.org/project/tigrbl-base/), [`tigrbl-concrete`](https://pypi.org/project/tigrbl-concrete/), [`tigrbl-canon`](https://pypi.org/project/tigrbl-canon/), [`tigrbl-orm`](https://pypi.org/project/tigrbl-orm/), [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/), [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/), [`tigrbl-kernel`](https://pypi.org/project/tigrbl-kernel/), [`tigrbl-ops-oltp`](https://pypi.org/project/tigrbl-ops-oltp/).
- External runtime dependencies: `pydantic>=2.0.0`, `sqlalchemy>=2.0`, `aiosqlite>=0.19.0`, `httpx>=0.27.0`, `greenlet>=3.2.3`, `uvicorn`.
- Optional extras: `rust`, `postgres`, `servers`, `templates`, `tests`.

## Related Packages

- [`tigrbl-core`](https://pypi.org/project/tigrbl-core/)
- [`tigrbl-base`](https://pypi.org/project/tigrbl-base/)
- [`tigrbl-concrete`](https://pypi.org/project/tigrbl-concrete/)
- [`tigrbl-canon`](https://pypi.org/project/tigrbl-canon/)
- [`tigrbl-orm`](https://pypi.org/project/tigrbl-orm/)
- [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/)
- [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/)
- [`tigrbl-kernel`](https://pypi.org/project/tigrbl-kernel/)

## Canonical Repository Docs

- `docs/README.md`
- `docs/conformance/CURRENT_TARGET.md`
- `docs/conformance/CURRENT_STATE.md`
- `docs/conformance/NEXT_STEPS.md`
- `docs/governance/DOC_POINTERS.md`
- `docs/developer/PACKAGE_CATALOG.md`
- `docs/developer/PACKAGE_LAYOUT.md`

## Package-local Boundary

This file is a package-local distribution entry point.
Use this page for package installation and boundary orientation. Repository governance, conformance state, target status, and release evidence remain governed from `docs/` and `.ssot/`.

## License

Licensed under the Apache License, Version 2.0. See `LICENSE` and the official [Apache 2.0 license text](https://www.apache.org/licenses/LICENSE-2.0).
