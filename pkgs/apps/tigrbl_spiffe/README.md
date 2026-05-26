<div align="center">
<h1>tigrbl_spiffe</h1>
<img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png" alt="Tigrbl logo" width="140"/>
<p><strong>SPIFFE and SPIRE identity app for Tigrbl with workload identity tables, UDS transport, and HTTP API surfaces.</strong></p>
<a href="https://pypi.org/project/tigrbl_spiffe/"><img src="https://img.shields.io/pypi/v/tigrbl_spiffe?label=PyPI" alt="PyPI version for tigrbl_spiffe"/></a>
<a href="https://pypi.org/project/tigrbl_spiffe/"><img src="https://static.pepy.tech/badge/tigrbl_spiffe" alt="Downloads for tigrbl_spiffe"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/apps/tigrbl_spiffe/README.md"><img src="https://hits.sh/github.com/tigrbl/tigrbl/blob/master/pkgs/apps/tigrbl_spiffe/README.md.svg?label=hits" alt="Repository hits for tigrbl_spiffe README"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%20to%203.15-3776ab" alt="Python requirement for tigrbl_spiffe"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/docs/README.md"><img src="https://img.shields.io/badge/workspace-apps-1f6feb" alt="Workspace group for tigrbl_spiffe"/></a>
</div>

## Install

```bash
uv add tigrbl_spiffe
```

```bash
pip install tigrbl_spiffe
```

Optional extras declared in `pyproject.toml`:

```bash
pip install "tigrbl_spiffe[grpc]"
```

## What It Owns

`tigrbl_spiffe` owns a packaged Tigrbl application boundary for spiffe, including domain tables, operations, service layers, and app wiring. Key implementation roots include `tigrbl_spiffe` with `adapters/, authz/, config, exceptions, identity/, middleware/`.

## Use It When

Use `tigrbl_spiffe` when you want a packaged Tigrbl application for spiffe with its tables, operations, services, and API wiring kept together.

## Public Surface

- `tigrbl_spiffe` exposes `TigrblSpiffePlugin, register, Svid, Registrar, Bundle, Workload, Endpoint, TigrblClientAdapter`.

## Internal Layout

- Workspace path: `pkgs/apps/tigrbl_spiffe`.
- Package class: `application package`.
- Python requirement: `>=3.10,<3.15`.
- `tigrbl_spiffe` modules: `adapters/, authz/, config, exceptions, identity/, middleware/, plugin, registry, supports, tables/`.

## Dependency Surface

- Workspace package dependencies: none declared.
- External runtime dependencies: `httpx>=0.27`, `tigrbl>=0.3.4`.
- Optional extras: `grpc`.

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
