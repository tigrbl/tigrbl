# Tigrbl Workspace

<p align="center">
    <a href="https://hits.sh/github.com/tigrbl/tigrbl/">
        <img src="https://hits.sh/github.com/tigrbl/tigrbl.svg" alt="Repository views for tigrbl"/></a>
    <a href="https://github.com/tigrbl/tigrbl/blob/master/docs/README.md">
        <img src="https://img.shields.io/badge/docs-repository%20docs-1f6feb" alt="Repository docs for tigrbl"/></a>
    <a href="https://github.com/tigrbl/tigrbl/actions/workflows/branch-coverage.yml">
        <img src="https://github.com/tigrbl/tigrbl/actions/workflows/branch-coverage.yml/badge.svg?branch=master" alt="Branch Coverage workflow status for tigrbl"/></a>
    <a href="https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml">
        <img src="https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml/badge.svg" alt="Publish Packages workflow status for tigrbl"/></a>
    <a href="https://github.com/Tigrbl/tigrbl/blob/master/.ssot/registry.json">
        <img src="https://img.shields.io/badge/SSOT-governed-2f6f4e.svg" alt="SSOT governed status for tigrbl"/></a>
    <a href="https://discord.gg/K4YTAPapjR">
        <img src="https://img.shields.io/badge/Discord-Join%20chat-5865F2?logo=discord&logoColor=white" alt="Discord community for tigrbl"/></a>
</p>

![Tigrbl package graph](docs/assets/tigrbl-package-graph.png)

Tigrbl is a mixed Python and Rust workspace for building schema-first REST and
JSON-RPC APIs around SQLAlchemy models, typed validation, lifecycle hooks, and
engine-backed execution.

The root `pyproject.toml` is a `uv` workspace with packaging disabled. The root
`Cargo.toml` is a Rust workspace for the additive runtime substrate.

## Workspace Layout

- `pkgs/core/` - 16 core Python packages, including the public `tigrbl`
  distribution and its supporting framework layers.
- `pkgs/engines/` - 24 Python engine packages.
- `pkgs/apps/` - 2 application packages.
- `crates/` - 11 Rust crates for the Rust runtime, bindings, and supporting
  execution layers.
- `examples/` - non-authoritative demos and verification helpers.
- `.ssot/` - authoritative ADR, SPEC, registry, feature, claim, test, evidence,
  boundary, and release governance data.
- `docs/` - projected documentation, conformance records, governance policy, and
  release evidence.
- `tools/ci/` - repository policy and gate validation scripts.
- `tools/conformance/` - spec snapshot and conformance generation helpers.

## Current Package Line

The active workspace package line is declared in
`pkgs/core/tigrbl/pyproject.toml`. At this checkpoint the public `tigrbl`
package is on `0.3.19.dev1`.

Stable release evidence and historical conformance records live under
`docs/conformance/releases/`. Development evidence for active targets lives
under `docs/conformance/dev/`.

## Canonical Documentation

Read the repository in this order when orienting on current scope, governance,
and release status:

1. `docs/conformance/CURRENT_TARGET.md`
2. `docs/conformance/CURRENT_STATE.md`
3. `docs/conformance/NEXT_TARGETS.md`
4. `docs/conformance/RFC_SECURITY_EVIDENCE_MAP.md`
5. `docs/conformance/EVIDENCE_MODEL.md`
6. `docs/conformance/IMPLEMENTATION_MAP.md`
7. `docs/conformance/NEXT_STEPS.md`
8. `docs/conformance/dev/`
9. `docs/conformance/releases/`
10. `docs/governance/DOC_POINTERS.md`
11. `docs/governance/TARGET_BOUNDARY.md`
12. `CONTRIBUTING.md`
13. `CODE_OF_CONDUCT.md`
14. `SECURITY.md`

## Governance Model

The `.ssot/` tree is the source of truth for governed entities. Documentation
under `docs/` should be treated as projected or explanatory unless a specific
policy document declares otherwise.

Do not use the root README as release certification evidence. Use the
conformance and governance documents above, plus the SSOT registry, for
auditable release status.

## Development

Install and work through the workspace with `uv`:

```powershell
uv sync --all-extras --dev
```

Common focused checks:

```powershell
uv run pytest pkgs/core/tigrbl_tests/tests
uv run ssot validate .
cargo test --workspace
```

Some Rust/native-runtime checks require a local Rust toolchain and a compatible
Python interpreter for the PyO3 bridge.
