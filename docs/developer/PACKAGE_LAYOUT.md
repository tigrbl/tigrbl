# Package Layout

This document defines the normalized workspace layout enforced in the package-layout checkpoint.

## Root layout

Allowed top-level repository entries are:

- `.github/`
- `.gitignore`
- `CODE_OF_CONDUCT.md`
- `CONTRIBUTING.md`
- `LICENSE`
- `README.md`
- `SECURITY.md`
- `docs/`
- `examples/`
- `pkgs/`
- `pyproject.toml`
- `tools/`

## Python workspace package layout

Python packages live under one of:

- `pkgs/<layer-id>/<package>/`

Layer membership is governed by `pkgs/LAYERS.toml` and projected in
`docs/developer/PACKAGE_LAYERS.md`. The physical source root is the layer id.

Each Python package root must contain:

- `pyproject.toml`
- `README.md` as a package-local pointer stub
- exactly one implementation layout:
  - `src/<package>/`
  - `<package>/`

Nested package roots inside a package directory are not allowed.

## Rust Runtime Binding Package Layout

No Rust runtime binding package layout is supported. Tigrbl packages are Python
packages, and runtime execution is Python-only.

## Documentation boundary

The only Markdown file allowed inside an active package root is the package root `README.md`.
Long-form package documentation belongs under the governed docs projection tree in `docs/`.

## Examples and tests

Examples, notebooks, and tests may remain inside package roots when they are code or data, but they may not become independent documentation authorities.
Top-level `examples/` is allowed for non-authoritative demos and verification helpers.
