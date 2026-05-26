<div align="center">
<h1>tigrbl-atoms</h1>
<img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png" alt="Tigrbl logo" width="140"/>
<p><strong>Runtime atom package for Tigrbl stages, phases, typed contexts, event anchors, protocol execution, and composable pipeline algebra.</strong></p>
<a href="https://pypi.org/project/tigrbl-atoms/"><img src="https://img.shields.io/pypi/v/tigrbl-atoms?label=PyPI" alt="PyPI version for tigrbl-atoms"/></a>
<a href="https://pypi.org/project/tigrbl-atoms/"><img src="https://static.pepy.tech/badge/tigrbl-atoms" alt="Downloads for tigrbl-atoms"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_atoms/README.md"><img src="https://hits.sh/github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_atoms/README.md.svg?label=hits" alt="Repository hits for tigrbl-atoms README"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%20to%203.15-3776ab" alt="Python requirement for tigrbl-atoms"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/docs/README.md"><img src="https://img.shields.io/badge/workspace-core-1f6feb" alt="Workspace group for tigrbl-atoms"/></a>
</div>

## Install

```bash
uv add tigrbl-atoms
```

```bash
pip install tigrbl-atoms
```

## What It Owns

`tigrbl-atoms` owns the atoms boundary inside the split Python workspace. Key implementation roots include `tigrbl_atoms` with `_ctx, _opview_helpers, _request, algebra, atoms/, events`.

## Use It When

Use `tigrbl-atoms` when you want this subsystem directly as a package boundary instead of consuming it only through the top-level `tigrbl` facade.

## Public Surface

- `tigrbl_atoms` exposes `import_module, Any, rust_atoms_enabled, register_rust_atom, register_rust_callback, register_rust_hook, PHASE_SEQUENCE, INGRESS_PHASES`.

## Internal Layout

- Workspace path: `pkgs/core/tigrbl_atoms`.
- Package class: `core framework package`.
- Python requirement: `>=3.10,<3.15`.
- `tigrbl_atoms` modules: `_ctx, _opview_helpers, _request, algebra, atoms/, events, fallback, phases, protocol_runtime, runtime_callbacks`.

## Dependency Surface

- Workspace package dependencies: [`tigrbl-ops-oltp`](https://pypi.org/project/tigrbl-ops-oltp/), [`tigrbl-ops-olap`](https://pypi.org/project/tigrbl-ops-olap/), [`tigrbl-ops-realtime`](https://pypi.org/project/tigrbl-ops-realtime/), [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-typing`](https://pypi.org/project/tigrbl-typing/).
- External runtime dependencies: `jinja2>=3.1`, `sqlalchemy>=2.0`, `typing-extensions>=4.0`.
- Optional extras: none declared.

## Related Packages

- [`tigrbl`](https://pypi.org/project/tigrbl/)
- [`tigrbl-ops-oltp`](https://pypi.org/project/tigrbl-ops-oltp/)
- [`tigrbl-ops-olap`](https://pypi.org/project/tigrbl-ops-olap/)
- [`tigrbl-ops-realtime`](https://pypi.org/project/tigrbl-ops-realtime/)
- [`tigrbl-core`](https://pypi.org/project/tigrbl-core/)
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
