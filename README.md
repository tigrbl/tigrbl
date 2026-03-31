# Tigrbl Workspace

This repository is a mixed Python + Rust workspace for Tigrbl. It contains:

- Python core packages under `pkgs/core/`
- Python engine packages under `pkgs/engines/`
- Python application packages under `pkgs/apps/`
- Rust-native crates under `crates/`
- Python bindings for the native runtime under `bindings/python/`

The root `pyproject.toml` is configured as a uv workspace with packaging disabled. The root `Cargo.toml` is configured as a Rust workspace for the additive native substrate.

## Repository status

This checkpoint completes **Phase 0 — Authority reset and repo freeze** for the supplied archive.

It does **not** claim that the package is already certifiably fully featured or certifiably fully RFC/spec/standard compliant. The current state, target boundary, and remaining gaps are documented in the governed docs tree linked below.

## Workspace layout

- `pkgs/core/` — 15 core Python packages
- `pkgs/engines/` — 22 Python engine packages
- `pkgs/apps/` — 6 application packages
- `crates/` — 9 Rust crates
- `bindings/python/` — 1 Python binding package(s)
- `docs/` — single authoritative documentation tree

## Canonical documentation

Read the repository in this order:

1. [`docs/conformance/CURRENT_TARGET.md`](docs/conformance/CURRENT_TARGET.md)
2. [`docs/conformance/CURRENT_STATE.md`](docs/conformance/CURRENT_STATE.md)
3. [`docs/conformance/NEXT_STEPS.md`](docs/conformance/NEXT_STEPS.md)
4. [`docs/governance/DOC_POINTERS.md`](docs/governance/DOC_POINTERS.md)
5. [`CONTRIBUTING.md`](CONTRIBUTING.md)
6. [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md)
7. [`SECURITY.md`](SECURITY.md)

## Phase 0 checkpoint changes in this archive

- preserved Apache 2.0 licensing
- added `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, and `SECURITY.md`
- created a governed `docs/` authority tree for governance, conformance, ADRs, developer docs, and notes
- archived legacy root-level current-state and build-proof materials under `docs/conformance/archive/2026/phase0-authority-reset/`
- removed generated `target/` output from the distributable checkpoint zip
- documented the current state of the repository and the remaining certification gaps

## Archived legacy materials

Legacy root-level proof and status artifacts from the supplied archive now live under:

- `docs/conformance/archive/2026/phase0-authority-reset/legacy-rust-native-checkpoint/`

See [`docs/governance/DOC_POINTERS.md`](docs/governance/DOC_POINTERS.md) for the canonical pointer map.
