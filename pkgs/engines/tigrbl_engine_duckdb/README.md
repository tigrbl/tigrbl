<div align="center">
<h1>tigrbl_engine_duckdb</h1>
<img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png" alt="Tigrbl logo" width="140"/>
<p><strong>DuckDB engine plugin for embedded analytical database sessions, OLAP workloads, and Tigrbl engine registration.</strong></p>
<a href="https://pypi.org/project/tigrbl_engine_duckdb/"><img src="https://img.shields.io/pypi/v/tigrbl_engine_duckdb?label=PyPI" alt="PyPI version for tigrbl_engine_duckdb"/></a>
<a href="https://pypi.org/project/tigrbl_engine_duckdb/"><img src="https://static.pepy.tech/badge/tigrbl_engine_duckdb" alt="Downloads for tigrbl_engine_duckdb"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/engines/tigrbl_engine_duckdb/README.md"><img src="https://hits.sh/github.com/tigrbl/tigrbl/blob/master/pkgs/engines/tigrbl_engine_duckdb/README.md.svg?label=hits" alt="Repository hits for tigrbl_engine_duckdb README"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%20to%203.15-3776ab" alt="Python requirement for tigrbl_engine_duckdb"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/docs/README.md"><img src="https://img.shields.io/badge/workspace-engines-1f6feb" alt="Workspace group for tigrbl_engine_duckdb"/></a>
</div>

## Install

```bash
uv add tigrbl_engine_duckdb
```

```bash
pip install tigrbl_engine_duckdb
```

## What It Owns

`tigrbl_engine_duckdb` owns the engine duckdb backend boundary for Tigrbl, including engine registration, session adapters, and backend-specific helpers. Key implementation roots include `tigrbl_engine_duckdb` with `duck_builder, duck_session, plugin`.

## Use It When

Use `tigrbl_engine_duckdb` when you want the engine duckdb backend installed as an isolated dependency instead of pulling every engine into your environment.

## Public Surface

- `tigrbl_engine_duckdb` exposes `duckdb_engine, duckdb_capabilities, DuckDBSession, register`.

## Internal Layout

- Workspace path: `pkgs/engines/tigrbl_engine_duckdb`.
- Package class: `engine plugin`.
- Python requirement: `>=3.10,<3.15`.
- `tigrbl_engine_duckdb` modules: `duck_builder, duck_session, plugin`.

## Dependency Surface

- Workspace package dependencies: none declared.
- External runtime dependencies: `duckdb>=1.0.0`, `tigrbl>=0.3.0.dev4`.
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
