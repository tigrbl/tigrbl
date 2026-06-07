# Conformance

This directory is a non-authoritative projection and evidence area. The
authoritative source for features, claims, tests, evidence, boundaries, releases,
ADRs, and specs is the SSOT tree:

- `.ssot/registry.json`
- `.ssot/adr/`
- `.ssot/specs/`
- `.ssot/releases/`
- `.ssot/reports/`

Do not treat root-level conformance projections as source of truth when they
disagree with SSOT state. Stale current-target, gate, claim-registry, and
evidence-registry projections have been removed from this directory.

## Reader Path

1. Inspect `.ssot/registry.json` for current entity state.
2. Inspect `.ssot/adr/` and `.ssot/specs/` for governing decisions and specs.
3. Inspect `.ssot/releases/` for boundary and release snapshots.
4. Inspect `.ssot/reports/` for generated reports and verification artifacts.
5. Use `docs/conformance/releases/`, `docs/conformance/dev/`, and
   `docs/conformance/audit/` only as historical or checkpoint evidence unless a
   file explicitly says it was generated from the current SSOT state.

## Directory Roles

- `releases/` stores historical release evidence bundles.
- `dev/` stores development checkpoint evidence bundles.
- `audit/` stores captured audit/checkpoint material.
- `archive/` stores legacy conformance material retained for traceability.

Any new conformance summary should be generated from SSOT state and should state
its generation source and timestamp.
