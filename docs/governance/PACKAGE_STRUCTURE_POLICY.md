# Package Structure Policy

## Root rules

The repository root should remain small and predictable. It may contain:

- package/workspace manifests (`pyproject.toml`, `Cargo.toml`, `Cargo.lock`, toolchain files)
- governance entry points (`README.md`, `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`)
- source roots (`pkgs/`, `crates/`, `bindings/`, `docs/`)
- repository configuration directories such as `.cargo/`

The root should not accumulate:

- loose Markdown notes
- loose current-state scratch docs
- build logs
- build artifacts
- generated compiler output such as `target/`

## Source roots

- `pkgs/core/` — core Python packages
- `pkgs/engines/` — engine packages
- `pkgs/apps/` — application packages
- `crates/` — Rust-native crates
- `bindings/python/` — Python bindings to the native runtime

## Documentation authority

All authoritative repo documentation lives under `docs/`.

The supplied archive already contained `docs/architecture/`, `docs/migration/`, and `docs/testing/`. Those directories remain part of the authoritative docs tree. New governance and conformance content must use the governed locations created in this checkpoint.

## Generated output rule

Generated output should be reproducible from source and should not be treated as authoritative repository content.
