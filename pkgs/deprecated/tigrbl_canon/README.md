<div align="center">
<h1>tigrbl-canon</h1>
<img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png" alt="Tigrbl logo" width="140"/>
<p><strong>Deprecated compatibility package for Tigrbl canonical mapping, router binding, schema attachment, RPC and REST exposure, and column inference utilities.</strong></p>
<a href="https://pypi.org/project/tigrbl-canon/"><img src="https://img.shields.io/pypi/v/tigrbl-canon?label=PyPI" alt="PyPI version for tigrbl-canon"/></a>
<a href="https://pypi.org/project/tigrbl-canon/"><img src="https://static.pepy.tech/badge/tigrbl-canon" alt="Downloads for tigrbl-canon"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/deprecated/tigrbl_canon/README.md"><img src="https://hits.sh/github.com/tigrbl/tigrbl/blob/master/pkgs/deprecated/tigrbl_canon/README.md.svg?label=hits" alt="Repository hits for tigrbl-canon README"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%20to%203.15-3776ab" alt="Python requirement for tigrbl-canon"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/docs/README.md"><img src="https://img.shields.io/badge/workspace-deprecated-6b7280" alt="Workspace group for tigrbl-canon"/></a>
</div>

## Deprecation Status

`tigrbl-canon` is deprecated and kept only as a compatibility package while callers migrate to the maintained `tigrbl` facade and package-specific runtime surfaces.

## Install

```bash
uv add tigrbl-canon
```

```bash
pip install tigrbl-canon
```

## What It Owns

`tigrbl-canon` is a deprecated canon boundary inside the split Python workspace. Key implementation roots include `tigrbl_canon` with `tigrbl_canon/mapping/`.

## Use It When

Avoid new direct use of `tigrbl-canon`. Existing consumers should treat this package as a migration bridge and prefer the top-level `tigrbl` facade or maintained package-specific surfaces.

## Public Surface

- `tigrbl_canon` exposes `_DEPRECATION_MESSAGE`.

## Internal Layout

- Workspace path: `pkgs/deprecated/tigrbl_canon`.
- Package class: `deprecated compatibility package`.
- Python requirement: `>=3.10,<3.15`.
- `tigrbl_canon` modules: `tigrbl_canon/mapping/`.

## Dependency Surface

- Workspace package dependencies: [`tigrbl-ops-oltp`](https://pypi.org/project/tigrbl-ops-oltp/), [`tigrbl-base`](https://pypi.org/project/tigrbl-base/), [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/), [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/), [`tigrbl`](https://pypi.org/project/tigrbl/).
- External runtime dependencies: none declared.
- Optional extras: none declared.

## Related Packages

- [`tigrbl`](https://pypi.org/project/tigrbl/)
- [`tigrbl-ops-oltp`](https://pypi.org/project/tigrbl-ops-oltp/)
- [`tigrbl-base`](https://pypi.org/project/tigrbl-base/)
- [`tigrbl-core`](https://pypi.org/project/tigrbl-core/)
- [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/)
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
