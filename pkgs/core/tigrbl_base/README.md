<div align="center">
<h1>tigrbl-base</h1>
<img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png" alt="Tigrbl logo" width="140"/>
<p><strong>Base contract package for Tigrbl apps, routers, tables, sessions, middleware, requests, responses, bindings, and engine interfaces.</strong></p>
<a href="https://pypi.org/project/tigrbl-base/"><img src="https://img.shields.io/pypi/v/tigrbl-base?label=PyPI" alt="PyPI version for tigrbl-base"/></a>
<a href="https://pypi.org/project/tigrbl-base/"><img src="https://static.pepy.tech/badge/tigrbl-base" alt="Downloads for tigrbl-base"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_base/README.md"><img src="https://hits.sh/github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_base/README.md.svg?label=hits" alt="Repository hits for tigrbl-base README"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%20to%203.15-3776ab" alt="Python requirement for tigrbl-base"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/docs/README.md"><img src="https://img.shields.io/badge/workspace-core-1f6feb" alt="Workspace group for tigrbl-base"/></a>
</div>

## Install

```bash
uv add tigrbl-base
```

```bash
pip install tigrbl-base
```

## What It Owns

`tigrbl-base` owns the base boundary inside the split Python workspace.

## Use It When

Use `tigrbl-base` when you want this subsystem directly as a package boundary instead of consuming it only through the top-level `tigrbl` facade.

## Public Surface

- Package-local implementation lives under `pkgs/core/tigrbl_base` and is consumed as a distribution boundary rather than a single broad root re-export.

## Internal Layout

- Workspace path: `pkgs/core/tigrbl_base`.
- Package class: `core framework package`.
- Python requirement: `>=3.10,<3.15`.

## Dependency Surface

- Workspace package dependencies: [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/).
- External runtime dependencies: `sqlalchemy>=2.0`, `pydantic>=2.0`.
- Optional extras: none declared.

## Related Packages

- [`tigrbl`](https://pypi.org/project/tigrbl/)
- [`tigrbl-core`](https://pypi.org/project/tigrbl-core/)
- [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/)

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
