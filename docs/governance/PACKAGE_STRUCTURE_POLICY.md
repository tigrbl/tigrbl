# Package Structure Policy

## Root rules

The repository root should remain small and predictable. It may contain:

- package/workspace manifests (`pyproject.toml`, `Cargo.toml`, `Cargo.lock`, toolchain files)
- governance entry points (`README.md`, `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`)
- source roots (`pkgs/`, `crates/`, `bindings/`, `docs/`)
- repository configuration directories such as `.cargo/` and `.github/`
- repository automation utilities under `tools/`

The root must not accumulate:

- loose Markdown notes
- loose current-state scratch docs
- build logs
- build artifacts
- generated compiler output such as `target/`
- ad hoc validator scripts outside the governed `tools/` tree

## Source roots

- `pkgs/core/` — core Python packages
- `pkgs/engines/` — engine packages
- `pkgs/apps/` — application packages
- `crates/` — Rust-native crates
- `bindings/python/` — Python bindings to the native runtime

## Python package layout

Each Python package root under `pkgs/` must contain:

- `pyproject.toml`
- `README.md`
- exactly one implementation root:
  - `src/<package>/`
  - `<package>/`

Nested package roots inside package directories are not allowed.
Duplicate package mirrors inside an existing package root are not allowed.

## Python binding package layout

Each binding package under `bindings/python/` must contain:

- `pyproject.toml`
- `README.md`
- `python/<package>/`
- `src/`

## Package-local documentation boundary

All authoritative repository documentation lives under `docs/`.

Package-local `README.md` files are allowed only as package distribution entry points. They must point readers back to the authoritative docs tree. Long-form Markdown files inside package directories are not authoritative and should be moved into `docs/` or archived under `docs/notes/archive/`.

## Rust crate layout

Each crate under `crates/` must contain:

- `Cargo.toml`
- `README.md`
- `src/`

## Documentation authority

The supplied archive already contained `docs/architecture/`, `docs/migration/`, and `docs/testing/`. Those directories remain part of the authoritative docs tree. New governance and conformance content must use the governed locations created in the Phase 0 and Phase 2 checkpoints.

## Path-length rule

The governed repository must stay within the declared path limits in `docs/governance/PATH_LENGTH_POLICY.md`.

- file name length <= `64`
- directory name length <= `48`
- repository-relative path length <= `160`

## Generated output rule

Generated output should be reproducible from source and should not be treated as authoritative repository content.
