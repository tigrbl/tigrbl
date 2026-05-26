<div align="center">
<h1>tigrbl_client</h1>
<img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png" alt="Tigrbl logo" width="140"/>
<p><strong>Typed Python client for Tigrbl REST and JSON-RPC APIs with sync and async calls, nested resource helpers, and optional Pydantic validation.</strong></p>
<a href="https://pypi.org/project/tigrbl_client/"><img src="https://img.shields.io/pypi/v/tigrbl_client?label=PyPI" alt="PyPI version for tigrbl_client"/></a>
<a href="https://pypi.org/project/tigrbl_client/"><img src="https://static.pepy.tech/badge/tigrbl_client" alt="Downloads for tigrbl_client"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_client/README.md"><img src="https://hits.sh/github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_client/README.md.svg?label=hits" alt="Repository hits for tigrbl_client README"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%20to%203.15-3776ab" alt="Python requirement for tigrbl_client"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/docs/README.md"><img src="https://img.shields.io/badge/workspace-core-1f6feb" alt="Workspace group for tigrbl_client"/></a>
</div>

## Install

```bash
uv add tigrbl_client
```

```bash
pip install tigrbl_client
```

## What It Owns

`tigrbl_client` owns the client boundary inside the split Python workspace. Key implementation roots include `tigrbl_client` with `_crud, _nested_crud, _rpc`.

## Use It When

Use `tigrbl_client` when you need a typed Python client for Tigrbl REST and JSON-RPC APIs without bringing in the full server-side framework surface.

## Public Surface

- `tigrbl_client` exposes `TypeVar, RPCMixin, _Schema, CRUDMixin, NestedCRUDMixin, TigrblClient`.

## Internal Layout

- Workspace path: `pkgs/core/tigrbl_client`.
- Package class: `core framework package`.
- Python requirement: `>=3.10,<3.15`.
- `tigrbl_client` modules: `_crud, _nested_crud, _rpc`.

## Dependency Surface

- Workspace package dependencies: none declared.
- External runtime dependencies: `fastapi>=0.100.0`, `pydantic>=2.0.0`.
- Optional extras: none declared.

## Related Packages

- [`tigrbl`](https://pypi.org/project/tigrbl/)

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
