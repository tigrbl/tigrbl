<div align="center">
<h1>tigrbl-runtime</h1>
<img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png" alt="Tigrbl logo" width="140"/>
<p><strong>Runtime pipeline helpers and execution bridge surfaces for Tigrbl ASGI applications, transports, and operation dispatch.</strong></p>
<a href="https://pypi.org/project/tigrbl-runtime/"><img src="https://img.shields.io/pypi/v/tigrbl-runtime?label=PyPI" alt="PyPI version for tigrbl-runtime"/></a>
<a href="https://pypi.org/project/tigrbl-runtime/"><img src="https://static.pepy.tech/badge/tigrbl-runtime" alt="Downloads for tigrbl-runtime"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_runtime/README.md"><img src="https://hits.sh/github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_runtime/README.md.svg?label=hits" alt="Repository hits for tigrbl-runtime README"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%20to%203.15-3776ab" alt="Python requirement for tigrbl-runtime"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/docs/README.md"><img src="https://img.shields.io/badge/workspace-core-1f6feb" alt="Workspace group for tigrbl-runtime"/></a>
</div>

## Install

```bash
uv add tigrbl-runtime
```

```bash
pip install tigrbl-runtime
```

## What It Owns

`tigrbl-runtime` owns the runtime boundary inside the split Python workspace.
Rust crates and optional Python extension bindings have moved to the private `tigrbl/tigrbl_rs` repository.

## Use It When

Use `tigrbl-runtime` when you want this subsystem directly as a package boundary instead of consuming it only through the top-level `tigrbl` facade.

## Public Surface

- Package-local implementation lives under `pkgs/core/tigrbl_runtime` and is consumed as a distribution boundary rather than a single broad root re-export.

## Internal Layout

- Workspace path: `pkgs/core/tigrbl_runtime`.
- Package class: `core framework package`.
- Python requirement: `>=3.10,<3.15`.

## Dependency Surface

- Workspace package dependencies: [`tigrbl-typing`](https://pypi.org/project/tigrbl-typing/), [`tigrbl-kernel`](https://pypi.org/project/tigrbl-kernel/), [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/), [`tigrbl-base`](https://pypi.org/project/tigrbl-base/), [`tigrbl-core`](https://pypi.org/project/tigrbl-core/).
- External runtime dependencies: `numba>=0.61.2`.
- Optional extras: none in this Python workspace.

## Related Packages

- [`tigrbl`](https://pypi.org/project/tigrbl/)
- [`tigrbl-typing`](https://pypi.org/project/tigrbl-typing/)
- [`tigrbl-kernel`](https://pypi.org/project/tigrbl-kernel/)
- [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/)
- [`tigrbl-base`](https://pypi.org/project/tigrbl-base/)
- [`tigrbl-core`](https://pypi.org/project/tigrbl-core/)

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
