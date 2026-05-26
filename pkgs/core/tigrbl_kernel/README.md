<div align="center">
<h1>tigrbl-kernel</h1>
<img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png" alt="Tigrbl logo" width="140"/>
<p><strong>Kernel orchestration for composing Tigrbl runtime plans, bindings, operation dispatch, and optimized ASGI execution.</strong></p>
<a href="https://pypi.org/project/tigrbl-kernel/"><img src="https://img.shields.io/pypi/v/tigrbl-kernel?label=PyPI" alt="PyPI version for tigrbl-kernel"/></a>
<a href="https://pypi.org/project/tigrbl-kernel/"><img src="https://static.pepy.tech/badge/tigrbl-kernel" alt="Downloads for tigrbl-kernel"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_kernel/README.md"><img src="https://hits.sh/github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_kernel/README.md.svg?label=hits" alt="Repository hits for tigrbl-kernel README"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%20to%203.15-3776ab" alt="Python requirement for tigrbl-kernel"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/docs/README.md"><img src="https://img.shields.io/badge/workspace-core-1f6feb" alt="Workspace group for tigrbl-kernel"/></a>
</div>

## Install

```bash
uv add tigrbl-kernel
```

```bash
pip install tigrbl-kernel
```

## What It Owns

`tigrbl-kernel` owns the kernel boundary inside the split Python workspace. Key implementation roots include `tigrbl_kernel` with `_build, _compile, atoms, cache, callbacks, core`.

## Use It When

Use `tigrbl-kernel` when you want this subsystem directly as a package boundary instead of consuming it only through the top-level `tigrbl` facade.

## Public Surface

- `tigrbl_kernel` exposes `import_module, Any, Dict, List, Mapping, build_rust_kernel, build_rust_parity_snapshot, normalize_rust_spec`.

## Internal Layout

- Workspace path: `pkgs/core/tigrbl_kernel`.
- Package class: `core framework package`.
- Python requirement: `>=3.10,<3.15`.
- `tigrbl_kernel` modules: `_build, _compile, atoms, cache, callbacks, core, eventkey, eventkey_hooks, events, helpers`.

## Dependency Surface

- Workspace package dependencies: [`tigrbl-typing`](https://pypi.org/project/tigrbl-typing/), [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/), [`tigrbl-core`](https://pypi.org/project/tigrbl-core/).
- External runtime dependencies: none declared.
- Optional extras: none declared.

## Related Packages

- [`tigrbl`](https://pypi.org/project/tigrbl/)
- [`tigrbl-typing`](https://pypi.org/project/tigrbl-typing/)
- [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/)
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
