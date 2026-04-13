# Package Layout

This document defines the normalized workspace layout enforced in the Phase 2 checkpoint.

## Root layout

Allowed top-level repository entries are:

- `.cargo/`
- `.github/`
- `.gitignore`
- `CODE_OF_CONDUCT.md`
- `CONTRIBUTING.md`
- `Cargo.lock`
- `Cargo.toml`
- `LICENSE`
- `README.md`
- `SECURITY.md`
- `bindings/`
- `crates/`
- `docs/`
- `pkgs/`
- `pyproject.toml`
- `rust-toolchain.toml`
- `tools/`

## Python workspace package layout

Python packages live under one of:

- `pkgs/core/<package>/`
- `pkgs/engines/<package>/`
- `pkgs/apps/<package>/`
- `bindings/python/<package>/`

Each Python package root must contain:

- `pyproject.toml`
- `README.md` as a package-local pointer stub
- exactly one implementation layout:
  - `src/<package>/`
  - `<package>/`

Nested package roots inside a package directory are not allowed.

## Python binding package layout

Binding packages under `bindings/python/` are hybrid packages. They must contain:

- `pyproject.toml`
- `README.md`
- `python/<package>/` for the importable Python surface
- `src/` for the native Rust extension source

## Rust crate layout

Rust crates live under `crates/<crate>/` and must contain:

- `Cargo.toml`
- `README.md`
- `src/`

## Documentation boundary

The only Markdown file allowed inside an active package root is the package root `README.md`.
Long-form package documentation belongs under the authoritative docs tree in `docs/`.

## Examples and tests

Examples, notebooks, and tests may remain inside package roots when they are code or data, but they may not become independent documentation authorities.
