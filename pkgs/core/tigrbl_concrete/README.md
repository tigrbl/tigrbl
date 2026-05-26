<div align="center">
<h1>tigrbl-concrete</h1>
<img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png" alt="Tigrbl logo" width="140"/>
<p><strong>Concrete Tigrbl implementations for reusable framework behavior, sessions, routes, responses, and base abstraction adapters.</strong></p>
<a href="https://pypi.org/project/tigrbl-concrete/"><img src="https://img.shields.io/pypi/v/tigrbl-concrete?label=PyPI" alt="PyPI version for tigrbl-concrete"/></a>
<a href="https://pypi.org/project/tigrbl-concrete/"><img src="https://static.pepy.tech/badge/tigrbl-concrete" alt="Downloads for tigrbl-concrete"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_concrete/README.md"><img src="https://hits.sh/github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_concrete/README.md.svg?label=hits" alt="Repository hits for tigrbl-concrete README"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%20to%203.15-3776ab" alt="Python requirement for tigrbl-concrete"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/docs/README.md"><img src="https://img.shields.io/badge/workspace-core-1f6feb" alt="Workspace group for tigrbl-concrete"/></a>
</div>

## Install

```bash
uv add tigrbl-concrete
```

```bash
pip install tigrbl-concrete
```

## What It Owns

`tigrbl-concrete` owns the concrete boundary inside the split Python workspace. Key implementation roots include `tigrbl_concrete` with `_concrete/, _decorators/, _mapping/, ddl/, decorators, engine/`.

## Use It When

Use `tigrbl-concrete` when you want this subsystem directly as a package boundary instead of consuming it only through the top-level `tigrbl` facade.

## Public Surface

- `tigrbl_concrete` exposes `import_module, Any, build_handlers, build_hooks, build_schemas, build_rest_router`.

## Internal Layout

- Workspace path: `pkgs/core/tigrbl_concrete`.
- Package class: `core framework package`.
- Python requirement: `>=3.10,<3.15`.
- `tigrbl_concrete` modules: `_concrete/, _decorators/, _mapping/, ddl/, decorators, engine/, factories/, resolve/, security/, shortcuts/`.

## Dependency Surface

- Workspace package dependencies: [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/), [`tigrbl-base`](https://pypi.org/project/tigrbl-base/), [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-ops-olap`](https://pypi.org/project/tigrbl-ops-olap/), [`tigrbl-ops-oltp`](https://pypi.org/project/tigrbl-ops-oltp/), [`tigrbl-ops-realtime`](https://pypi.org/project/tigrbl-ops-realtime/), [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/), [`tigrbl-typing`](https://pypi.org/project/tigrbl-typing/).
- External runtime dependencies: `orjson`, `pydantic>=2.0`, `sqlalchemy`, `uvicorn`.
- Optional extras: none declared.

## Related Packages

- [`tigrbl`](https://pypi.org/project/tigrbl/)
- [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/)
- [`tigrbl-base`](https://pypi.org/project/tigrbl-base/)
- [`tigrbl-core`](https://pypi.org/project/tigrbl-core/)
- [`tigrbl-ops-olap`](https://pypi.org/project/tigrbl-ops-olap/)
- [`tigrbl-ops-oltp`](https://pypi.org/project/tigrbl-ops-oltp/)
- [`tigrbl-ops-realtime`](https://pypi.org/project/tigrbl-ops-realtime/)
- [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/)

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
