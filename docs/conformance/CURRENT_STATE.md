# Current State — Post-promotion handoff

## Scope and method

This document carries forward the Gate B surface-closure, Gate C conformance/security, Gate D reproducibility, and Gate E promotion checkpoints and records the Post-promotion handoff work completed to freeze the promoted release as release history while opening the next governed development line.

Post-promotion handoff focused on:

- preserving stable release `0.3.18` as frozen current-boundary release history
- retaining `docs/conformance/dev/0.3.18.dev1/` as the exact promotion-source dev bundle
- advancing the working-tree facade package version from `0.3.18` to `0.3.19.dev1`
- creating `docs/conformance/NEXT_TARGETS.md`
- moving the datatype/table program into governed next-target ADRs and plans
- archiving promotion-only WIP notes under `docs/notes/archive/2026/post-promotion-handoff/`
- creating an active dev-bundle scaffold at `docs/conformance/dev/0.3.19.dev1/`

The current state below is grounded in:

1. direct inspection of the governed docs tree
2. direct inspection of the Gate B, Gate C, Gate D, and Gate E validators, workflows, and bundle files
3. direct inspection of the new Post-promotion handoff validator, workflow, ADRs, and audit note
4. execution of the repository policy validators under `tools/ci/`
5. execution of the Gate B, Gate C, Gate D, Gate E, and Post-promotion handoff validator pytest slices
6. carried-forward audit evidence for the closed release bundle `0.3.18`

## Certification status

Gate E remains passed for the promoted stable release `0.3.18`.

Within the declared current target boundary, the promoted stable release `0.3.18` remains honestly describable as:

- certifiably fully featured
- certifiably fully RFC/spec/standard compliant

The active working-tree line `0.3.19.dev1` is a governed next-target planning checkpoint. It is **not** described here as a new certified release and it does not inherit Tier 3 wording merely by following the promoted release.

Boundary note: the certification wording above still applies only within the declared current target boundary. Deferred datatype/table work and out-of-boundary server/runtime transport ownership remain outside the claim set for the frozen release.

## Exact gate state

- Gate A: passed and still enforced
- Gate B: passed and still enforced
- Gate C: passed in the Gate C conformance/security checkpoint
- Gate D: passed in the Gate D reproducibility checkpoint
- Gate E: passed in the Gate E promotion checkpoint
- Post-promotion handoff: verified in the current checkpoint

## Exact current Gate B statement carried forward

There are **no unresolved current-target surface gaps** remaining.

## Exact retained spec/security state carried forward

There are no unresolved retained spec/security gaps remain in the governed current-target set.

### OpenAPI / JSON Schema / JSON-RPC / OpenRPC rows

Closed and proved in Gate C for frozen release `0.3.18`:

- OpenAPI 3.1.0 docs and emitted behavior
- explicit JSON Schema Draft 2020-12 declaration via `jsonSchemaDialect`
- request body / response / parameter behavior
- `components.schemas`
- `components.securitySchemes`
- operation-level security requirements from `secdeps`
- JSON-RPC 2.0 explicit target and runtime/docs behavior
- OpenRPC 1.2.6 explicit target and runtime/docs behavior

### Security-scheme and RFC rows retained in the frozen current cycle

Closed and proved in Gate C for frozen release `0.3.18`:

- `apiKey` docs/runtime alignment
- HTTP Basic docs/runtime alignment
- HTTP Bearer docs/runtime alignment
- `oauth2` OAS scheme docs/runtime alignment
- `openIdConnect` OAS scheme docs/runtime alignment
- `mutualTLS` OAS scheme docs/runtime alignment
- RFC 7235 retained HTTP auth challenge semantics
- RFC 7617 retained Basic parsing/challenge behavior
- RFC 6750 retained Bearer parsing/challenge behavior

### Exact rows explicitly de-scoped and still outside the frozen release cycle

These rows remain explicitly de-scoped and therefore do **not** block the frozen release `0.3.18`:

- OIDC Core 1.0 exact closure
- RFC 6749 exact OAuth 2.0 closure
- RFC 7519 exact JWT closure
- RFC 7636 exact PKCE closure
- RFC 8414 exact authorization-server metadata closure
- RFC 8705 exact OAuth mutual-TLS closure
- RFC 9110 exact framework-owned semantics closure
- RFC 9449 exact DPoP closure

## Active working-tree status

The active working tree is now `0.3.19.dev1`.

What is governed now:

- stable release history remains frozen under `docs/conformance/releases/0.3.18/`
- promotion-source dev evidence remains frozen under `docs/conformance/dev/0.3.18.dev1/`
- active planning work is isolated under `docs/conformance/NEXT_TARGETS.md`
- the active dev bundle is scaffolded under `docs/conformance/dev/0.3.19.dev1/`
- the datatype/table program is governed by ADR-0011 and ADR-0012 rather than by loose WIP notes

What is not yet true for `0.3.19.dev1`:

- no Tier 3 certification claim is attached to the active dev line
- no new stable release has been promoted
- no next-target implementation closure is claimed yet

## Post-promotion handoff machine-checks now in tree

| Surface | Current state | Evidence |
|---|---|---|
| Gate E validator | implemented | `tools/ci/validate_gate_e_promotion.py` |
| Gate E validator pytest slice | implemented | `tools/ci/tests/test_gate_e_promotion.py` |
| Gate E workflow | implemented | `.github/workflows/gate-e-promotion.yml` |
| Post-promotion handoff validator | implemented | `tools/ci/validate_post_promotion_handoff.py` |
| Post-promotion handoff pytest slice | implemented | `tools/ci/tests/test_post_promotion_handoff.py` |
| Post-promotion handoff workflow | implemented | `.github/workflows/post-promotion-handoff.yml` |
| Active dev-bundle scaffold | implemented | `docs/conformance/dev/0.3.19.dev1/` |
| Next-target plan | implemented | `docs/conformance/NEXT_TARGETS.md` |

## Evidence-backed conclusions

1. The selected candidate build `0.3.18.dev1` remains the exact source build for the promoted stable release `0.3.18`.
2. The stable release bundle remains frozen and synchronized across release notes, claims, evidence index, current-target snapshot, gate results, and artifact manifests.
3. The working-tree facade package metadata is now advanced to `0.3.19.dev1` for the next governed line.
4. The datatype/table program is now isolated into governed next-target ADRs and plans instead of being carried as unresolved release-cycle WIP.
5. The current-boundary Tier 3 claim rows remain attached to the frozen stable release bundle only.

The clean-room evidence passes on the selected candidate build.

## Authoritative companion documents

- `docs/conformance/CURRENT_TARGET.md`
- `docs/conformance/NEXT_TARGETS.md`
- `docs/conformance/CLAIM_REGISTRY.md`
- `docs/conformance/IMPLEMENTATION_MAP.md`
- `docs/conformance/RFC_SECURITY_EVIDENCE_MAP.md`
- `docs/conformance/EVIDENCE_MODEL.md`
- `docs/conformance/EVIDENCE_REGISTRY.json`
- `docs/conformance/gates/GATE_C_CONFORMANCE_SECURITY.md`
- `docs/conformance/gates/GATE_D_REPRODUCIBILITY.md`
- `docs/conformance/gates/GATE_E_PROMOTION.md`
- `docs/conformance/dev/0.3.19.dev1/EVIDENCE_INDEX.md`
- `docs/conformance/releases/0.3.18/EVIDENCE_INDEX.md`
- `docs/conformance/NEXT_STEPS.md`
- `docs/governance/DOC_POINTERS.md`
