<div align="center">
<h1>tigrbl_acme_ca</h1>
<img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png" alt="Tigrbl logo" width="140"/>
<p><strong>ACME v2 certificate authority app for Tigrbl tables, certificate automation, TLS workflows, and API surfaces.</strong></p>
<a href="https://pypi.org/project/tigrbl_acme_ca/"><img src="https://img.shields.io/pypi/v/tigrbl_acme_ca?label=PyPI" alt="PyPI version for tigrbl_acme_ca"/></a>
<a href="https://pypi.org/project/tigrbl_acme_ca/"><img src="https://static.pepy.tech/badge/tigrbl_acme_ca" alt="Downloads for tigrbl_acme_ca"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/apps/tigrbl_acme_ca/README.md"><img src="https://hits.sh/github.com/tigrbl/tigrbl/blob/master/pkgs/apps/tigrbl_acme_ca/README.md.svg?label=hits" alt="Repository hits for tigrbl_acme_ca README"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%20to%203.15-3776ab" alt="Python requirement for tigrbl_acme_ca"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/docs/README.md"><img src="https://img.shields.io/badge/workspace-apps-1f6feb" alt="Workspace group for tigrbl_acme_ca"/></a>
</div>

## Install

```bash
uv add tigrbl_acme_ca
```

```bash
pip install tigrbl_acme_ca
```

## What It Owns

`tigrbl_acme_ca` owns a packaged Tigrbl application boundary for acme ca, including domain tables, operations, service layers, and app wiring.

## Use It When

Use `tigrbl_acme_ca` when you want a packaged Tigrbl application for acme ca with its tables, operations, services, and API wiring kept together.

## Public Surface

- Package-local implementation lives under `pkgs/apps/tigrbl_acme_ca` and is consumed as a distribution boundary rather than a single broad root re-export.

## Internal Layout

- Workspace path: `pkgs/apps/tigrbl_acme_ca`.
- Package class: `application package`.
- Python requirement: `>=3.10,<3.15`.

## Dependency Surface

- Workspace package dependencies: none declared.
- External runtime dependencies: `tigrbl>=0.3.0.dev4`.
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
