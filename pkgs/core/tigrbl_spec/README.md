<div align="center">
<h1>tigrbl_spec</h1>
<img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png" alt="Tigrbl logo" width="140"/>
<p><strong>Shared Tigrbl interfaces, protocol definitions, compatibility targets, and specification artifacts for framework integration.</strong></p>
<a href="https://pypi.org/project/tigrbl_spec/"><img src="https://img.shields.io/pypi/v/tigrbl_spec?label=PyPI" alt="PyPI version for tigrbl_spec"/></a>
<a href="https://pypi.org/project/tigrbl_spec/"><img src="https://static.pepy.tech/badge/tigrbl_spec" alt="Downloads for tigrbl_spec"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_spec/README.md"><img src="https://hits.sh/github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_spec/README.md.svg?label=hits" alt="Repository hits for tigrbl_spec README"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%20to%203.15-3776ab" alt="Python requirement for tigrbl_spec"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/docs/README.md"><img src="https://img.shields.io/badge/workspace-core-1f6feb" alt="Workspace group for tigrbl_spec"/></a>
</div>

## Install

```bash
uv add tigrbl_spec
```

```bash
pip install tigrbl_spec
```

## What It Owns

`tigrbl_spec` owns the spec boundary inside the split Python workspace.

## Use It When

Use `tigrbl_spec` when you want this subsystem directly as a package boundary instead of consuming it only through the top-level `tigrbl` facade.

## Public Surface

- `tigrbl_spec` exposes `__version__`.

## Internal Layout

- Workspace path: `pkgs/core/tigrbl_spec`.
- Package class: `core framework package`.
- Python requirement: `>=3.10,<3.15`.

## Dependency Surface

- Workspace package dependencies: none declared.
- External runtime dependencies: none declared.
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
