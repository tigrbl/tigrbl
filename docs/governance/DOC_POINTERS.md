# Documentation Pointer Map

This map is a non-authoritative navigation aid. It does not define features,
claims, evidence, boundaries, releases, ADRs, or specs.

## Authoritative Sources

| Need | Source |
|---|---|
| Feature, claim, test, evidence, boundary, release state | `.ssot/registry.json` |
| Architectural decisions | `.ssot/adr/` |
| Normative specs | `.ssot/specs/` |
| Boundary and release snapshots | `.ssot/releases/` |
| Generated SSOT reports and verification artifacts | `.ssot/reports/` |
| SSOT schemas | `.ssot/schemas/` |

## Project Docs

| Need | Source |
|---|---|
| Repository overview | `README.md` |
| Documentation overview | `docs/README.md` |
| Documentation pointer map | `docs/governance/DOC_POINTERS.md` |
| Governance policies | `docs/governance/` |
| Conformance evidence area | `docs/conformance/` |
| Conformance overview | `docs/conformance/README.md` |
| Current frozen target narrative | `docs/conformance/CURRENT_TARGET.md` |
| Developer and operator docs | `docs/developer/` |
| Application authoring BCP | `docs/developer/AUTHORING_BCP.md` |
| Equivalence guide index | `docs/developer/EQUIVALENCE_INDEX.md` |
| Tigrbl, Starlette, and FastAPI application authoring comparison | `docs/developer/AUTHORING_EQUIVALENCE.md` |
| Transport, ASGI 3, WebSocket, and WebTransport comparison | `docs/developer/TRANSPORT_EQUIVALENCE.md` |
| Engine, SQLAlchemy, SQL dialect, and backend plugin comparison | `docs/developer/ENGINE_SQL_EQUIVALENCE.md` |
| Transport and framing reference | `docs/developer/TRANSPORTS_AND_FRAMING.md` |
| Package catalog | `docs/developer/PACKAGE_CATALOG.md` |
| Package layout | `docs/developer/PACKAGE_LAYOUT.md` |
| Release-note policy | `docs/release-notes/README.md` |
| Working and archived notes | `docs/notes/` |

## Governance Policies

| Need | Source |
|---|---|
| Target boundary narrative | `docs/governance/TARGET_BOUNDARY.md` |
| Certification policy | `docs/governance/CERTIFICATION_POLICY.md` |
| Claim tier language | `docs/governance/CLAIM_TIERS.md` |
| Release policy | `docs/governance/RELEASE_POLICY.md` |
| Versioning policy | `docs/governance/VERSIONING_POLICY.md` |
| Package structure policy | `docs/governance/PACKAGE_STRUCTURE_POLICY.md` |
| Path length policy | `docs/governance/PATH_LENGTH_POLICY.md` |
| Notes policy | `docs/governance/NOTES_POLICY.md` |
| Style guide | `docs/governance/STYLE_GUIDE.md` |

## Conformance Artifacts

| Need | Source |
|---|---|
| Historical release evidence bundles | `docs/conformance/releases/` |
| Development checkpoint evidence bundles | `docs/conformance/dev/` |
| Audit and checkpoint captures | `docs/conformance/audit/` |
| Archived legacy conformance material | `docs/conformance/archive/` |
| Declared-surface current-state report | `.ssot/reports/current_state/2026-04-07-phase1-declarative-surface.md` |
| Declared-surface certification-state report | `.ssot/reports/certification_state/2026-04-07-phase1-declarative-surface.md` |

Root-level conformance gate documents, shadow claim registries, and shadow
evidence registries are intentionally not listed here. Use SSOT entities and
snapshots instead.

## CI And Validation

Validation tooling under `tools/ci/` is a guardrail layer over repository state.
It is not an authority source. Validators that still reference removed
conformance projections should be retired or rewritten to consume SSOT state.
The current CI validation guide lives at `docs/developer/CI_VALIDATION.md`.
