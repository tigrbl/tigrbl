# Tigrbl Workspace

This repository is a mixed Python + Rust workspace for Tigrbl. It contains:

- Python core packages under `pkgs/core/`
- Python engine packages under `pkgs/engines/`
- Python application packages under `pkgs/apps/`
- Non-authoritative examples under `examples/`
- Rust crates under `crates/`
- The Python↔Rust runtime bridge under `pkgs/core/tigrbl_runtime/`

The root `pyproject.toml` is configured as a uv workspace with packaging disabled. The root `Cargo.toml` is configured as a Rust workspace for the additive Rust substrate.

## Repository status

This checkpoint completes **Phase 14 - post-promotion handoff** on top of the already-passed **Phase 13 - Gate E promotion and release**.

The repository now records:

- stable release `0.3.18` frozen as governed release history under `docs/conformance/releases/0.3.18/`
- promotion-source dev bundle `0.3.18.dev1` retained unchanged under `docs/conformance/dev/0.3.18.dev1/`
- active working-tree version advanced to `0.3.19.dev1` at `pkgs/core/tigrbl/pyproject.toml`
- a governed next-target planning document at `docs/conformance/NEXT_TARGETS.md`
- next-target ADRs for the datatype/table program under `docs/adr/`
- archived promotion-only WIP notes under `docs/notes/archive/2026/p14-post-promotion-handoff/`

Boundary note: the existing Tier 3 certification wording still applies only to the frozen stable release `0.3.18` within the declared current target boundary in `docs/governance/TARGET_BOUNDARY.md`. The active `0.3.19.dev1` line is a governed next-target planning line and is **not** described here as a new promoted Tier 3 release.

## Workspace layout

- `pkgs/core/` - 15 core Python packages
- `pkgs/engines/` - 22 Python engine packages
- `pkgs/apps/` - 6 application packages
- `examples/` - non-authoritative demos and verification helpers
- `crates/` - 9 Rust crates
- `docs/` - single authoritative documentation tree
- `tools/ci/` - repository policy and gate validation scripts
- `tools/conformance/` - spec snapshot generation helpers

## Canonical documentation

Read the repository in this order:

1. `docs/conformance/CURRENT_TARGET.md`
2. `docs/conformance/CURRENT_STATE.md`
3. `docs/conformance/NEXT_TARGETS.md`
4. `docs/conformance/RFC_SECURITY_EVIDENCE_MAP.md`
5. `docs/conformance/EVIDENCE_MODEL.md`
6. `docs/conformance/IMPLEMENTATION_MAP.md`
7. `docs/conformance/NEXT_STEPS.md`
8. `docs/conformance/dev/0.3.19.dev1/EVIDENCE_INDEX.md`
9. `docs/conformance/releases/0.3.18/EVIDENCE_INDEX.md`
10. `docs/governance/DOC_POINTERS.md`
11. `CONTRIBUTING.md`
12. `CODE_OF_CONDUCT.md`
13. `SECURITY.md`
