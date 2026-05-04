![Tigrbl Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png)

<p align="center">
    <a href="https://pypi.org/project/tigrbl/">
        <img src="https://img.shields.io/pypi/dm/tigrbl" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl/">
        <img alt="Hits" src="https://hits.sh/github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl.svg"/></a>
    <a href="https://pypi.org/project/tigrbl/">
        <img src="https://img.shields.io/pypi/pyversions/tigrbl" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/tigrbl/">
        <img src="https://img.shields.io/pypi/l/tigrbl" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/tigrbl/">
        <img src="https://img.shields.io/pypi/v/tigrbl?label=tigrbl&color=green" alt="PyPI - tigrbl"/></a>
</p>

---

# Tigrbl 🐅🐂

A high-leverage ASGI meta-framework that turns plain SQLAlchemy models into a REST+RPC surface with near-zero boilerplate. 🚀

## Features ✨

- ⚡ Zero-boilerplate CRUD for SQLAlchemy models
- 🔌 Unified REST and RPC endpoints from a single definition
- 🪝 Hookable phase system for deep customization
- 🧩 Pluggable engine and provider abstractions
- 🚀 Built as an ASGI-native framework with Pydantic-powered schema generation

## Split Package Module Locations 🗂️

These surfaces are maintained in the split Tigrbl packages, with `tigrbl.*`
kept as compatibility imports:

- `tigrbl.ddl` -> `tigrbl_concrete.ddl`
- `tigrbl.system` -> `tigrbl_concrete.system`
- `tigrbl.op` -> `tigrbl_core.op`
- `tigrbl.config` -> `tigrbl_core.config`
- `tigrbl.schema` -> `tigrbl_core.schema`
- `tigrbl.security` -> `tigrbl_concrete.security`

## Package-local entry point

This file is a package-local distribution entry point.
It is not the authoritative location for repository governance, current target status, current state reporting, certification claims, or release evidence.

## Canonical repository docs

- `README.md`
- `docs/README.md`
- `docs/conformance/CURRENT_TARGET.md`
- `docs/conformance/CURRENT_STATE.md`
- `docs/conformance/NEXT_STEPS.md`
- `docs/governance/DOC_POINTERS.md`
- `docs/developer/PACKAGE_CATALOG.md`
- `docs/developer/PACKAGE_LAYOUT.md`

## Package identity

- canonical repository: `https://github.com/tigrbl/tigrbl`
- organization: `https://github.com/tigrbl`
- social: `https://discord.gg/K4YTAPapjR`
- package path: `https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl`
- workspace path: `pkgs/core/tigrbl`
- workspace class: core Python package
- implementation layout: `tigrbl/`

Long-form repository documentation is governed from `docs/`.
