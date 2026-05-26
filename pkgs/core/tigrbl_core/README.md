<div align="center">
<h1>tigrbl-core</h1>
<img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png" alt="Tigrbl logo" width="140"/>
<p><strong>Core Tigrbl framework specifications, decorators, schemas, hooks, operations, and primitives for schema-first APIs.</strong></p>
<a href="https://pypi.org/project/tigrbl-core/"><img src="https://img.shields.io/pypi/v/tigrbl-core?label=PyPI" alt="PyPI version for tigrbl-core"/></a>
<a href="https://pypi.org/project/tigrbl-core/"><img src="https://static.pepy.tech/badge/tigrbl-core" alt="Downloads for tigrbl-core"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_core/README.md"><img src="https://hits.sh/github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_core/README.md.svg?label=hits" alt="Repository hits for tigrbl-core README"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%20to%203.15-3776ab" alt="Python requirement for tigrbl-core"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/docs/README.md"><img src="https://img.shields.io/badge/workspace-core-1f6feb" alt="Workspace group for tigrbl-core"/></a>
</div>

## Install

```bash
uv add tigrbl-core
```

```bash
pip install tigrbl-core
```

## What It Owns

`tigrbl-core` owns the core boundary inside the split Python workspace. Key implementation roots include `tigrbl_core` with `_spec/, canonical_json, config/, core/, op/, schema/`.

## Use It When

Use `tigrbl-core` when you want this subsystem directly as a package boundary instead of consuming it only through the top-level `tigrbl` facade.

## Public Surface

- Primary module root: `tigrbl_core` with module families `_spec/, canonical_json, config/, core/, op/, schema/`.

## Internal Layout

- Workspace path: `pkgs/core/tigrbl_core`.
- Package class: `core framework package`.
- Python requirement: `>=3.10,<3.15`.
- `tigrbl_core` modules: `_spec/, canonical_json, config/, core/, op/, schema/`.

## Dependency Surface

- Workspace package dependencies: [`tigrbl-typing`](https://pypi.org/project/tigrbl-typing/).
- External runtime dependencies: `pydantic>=2.10,<3`, `pyyaml`, `tomli-w`, `tomli>=2.0.1; python_version < '3.11'`.
- Optional extras: none declared.

## Related Packages

- [`tigrbl`](https://pypi.org/project/tigrbl/)
- [`tigrbl-typing`](https://pypi.org/project/tigrbl-typing/)

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
