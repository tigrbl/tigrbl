# Tigrbl Workspace

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
package is on `0.3.30.dev1`.

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
