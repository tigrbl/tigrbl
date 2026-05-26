<div align="center">
<h1>tigrbl-typing</h1>
<img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png" alt="Tigrbl logo" width="140"/>
<p><strong>Typing protocols, aliases, generics, and shared type helpers for Tigrbl framework packages and extensions.</strong></p>
<a href="https://pypi.org/project/tigrbl-typing/"><img src="https://img.shields.io/pypi/v/tigrbl-typing?label=PyPI" alt="PyPI version for tigrbl-typing"/></a>
<a href="https://pypi.org/project/tigrbl-typing/"><img src="https://static.pepy.tech/badge/tigrbl-typing" alt="Downloads for tigrbl-typing"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_typing/README.md"><img src="https://hits.sh/github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_typing/README.md.svg?label=hits" alt="Repository hits for tigrbl-typing README"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%20to%203.15-3776ab" alt="Python requirement for tigrbl-typing"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/docs/README.md"><img src="https://img.shields.io/badge/workspace-core-1f6feb" alt="Workspace group for tigrbl-typing"/></a>
</div>

## Install

```bash
uv add tigrbl-typing
```

```bash
pip install tigrbl-typing
```

## What It Owns

`tigrbl-typing` owns the typing boundary inside the split Python workspace. Key implementation roots include `tigrbl_typing` with `channel, gw/, phases, protocols, request, status/`.

## Use It When

Use `tigrbl-typing` when you want this subsystem directly as a package boundary instead of consuming it only through the top-level `tigrbl` facade.

## Public Surface

- `tigrbl_typing` exposes `import_module, Any`.

## Internal Layout

- Workspace path: `pkgs/core/tigrbl_typing`.
- Package class: `core framework package`.
- Python requirement: `>=3.10,<3.15`.
- `tigrbl_typing` modules: `channel, gw/, phases, protocols, request, status/, types/, vendor/`.

## Dependency Surface

- Workspace package dependencies: none declared.
- External runtime dependencies: `pydantic>=2.10,<3`.
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
