<div align="center">
<h1>tigrbl-ops-olap</h1>
<img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png" alt="Tigrbl logo" width="140"/>
<p><strong>Analytical OLAP operation boundaries for Tigrbl workloads, query-oriented APIs, and engine integrations.</strong></p>
<a href="https://pypi.org/project/tigrbl-ops-olap/"><img src="https://img.shields.io/pypi/v/tigrbl-ops-olap?label=PyPI" alt="PyPI version for tigrbl-ops-olap"/></a>
<a href="https://pypi.org/project/tigrbl-ops-olap/"><img src="https://static.pepy.tech/badge/tigrbl-ops-olap" alt="Downloads for tigrbl-ops-olap"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_ops_olap/README.md"><img src="https://hits.sh/github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_ops_olap/README.md.svg?label=hits" alt="Repository hits for tigrbl-ops-olap README"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%20to%203.15-3776ab" alt="Python requirement for tigrbl-ops-olap"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/docs/README.md"><img src="https://img.shields.io/badge/workspace-core-1f6feb" alt="Workspace group for tigrbl-ops-olap"/></a>
</div>

## Install

```bash
uv add tigrbl-ops-olap
```

```bash
pip install tigrbl-ops-olap
```

## What It Owns

`tigrbl-ops-olap` owns the ops olap boundary inside the split Python workspace. Key implementation roots include `tigrbl_ops_olap` with `ops`.

## Use It When

Use `tigrbl-ops-olap` when you want this subsystem directly as a package boundary instead of consuming it only through the top-level `tigrbl` facade.

## Public Surface

- `tigrbl_ops_olap` exposes `aggregate, group_by`.

## Internal Layout

- Workspace path: `pkgs/core/tigrbl_ops_olap`.
- Package class: `core framework package`.
- Python requirement: `>=3.10,<3.15`.
- `tigrbl_ops_olap` modules: `ops`.

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
