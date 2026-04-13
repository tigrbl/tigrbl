# Current Target

## Purpose

This document now freezes the closed current-target cycle as release history for stable release `0.3.18`. The active next-line work is isolated under `docs/conformance/NEXT_TARGETS.md` and does not reopen the already-closed current-target boundary.

## Gate A freeze status

- Freeze status: current target frozen for the current cycle
- Boundary freeze marker: `docs/conformance/gates/TARGET_FREEZE_CURRENT_CYCLE.json`
- Boundary freeze manifest: `docs/conformance/gates/GATE_A_BOUNDARY_FREEZE_MANIFEST.json`
- Update rule: any change to the current-target or boundary docs must include a synchronized `docs/conformance/CLAIM_REGISTRY.md` update and a regenerated boundary-freeze manifest/marker pair.

## Gate B status

- Gate B status: passed in the Phase 10 checkpoint
- Gate B validator: `tools/ci/validate_gate_b_surface_closure.py`
- Gate B workflow: `.github/workflows/gate-b-surface-closure.yml`

## Gate C status

- Gate C status: passed in the Phase 11 checkpoint
- Gate C validator: `tools/ci/validate_gate_c_conformance_security.py`
- Gate C workflow: `.github/workflows/gate-c-conformance-security.yml`

## Gate D status

- Gate D status: passed in the Phase 12 checkpoint
- Gate D validator: `tools/ci/validate_gate_d_reproducibility.py`
- Gate D workflow: `.github/workflows/gate-d-reproducibility.yml`

## Gate E status

- Gate E status: passed in the Phase 13 promotion checkpoint
- Gate E validator: `tools/ci/validate_gate_e_promotion.py`
- Gate E workflow: `.github/workflows/gate-e-promotion.yml`
- promotion-source dev build: `docs/conformance/dev/0.3.18.dev1/`
- promoted stable release: `docs/conformance/releases/0.3.18/`

## Phase 14 handoff status

- handoff status: current-target release history frozen and preserved
- active next-line dev bundle: `docs/conformance/dev/0.3.19.dev1/`
- next-target planning document: `docs/conformance/NEXT_TARGETS.md`
- active working-tree facade package version: `0.3.19.dev1`

## In-boundary ownership

Tigrbl currently targets framework ownership over:

- application semantics
- API semantics
- auth semantics
- OAS 3.1 security-scheme-first docs and runtime alignment
- OpenAPI / OpenRPC docs emission within the framework boundary
- JSON-RPC / OpenRPC behavior within the framework boundary
- retained RFC auth rows at the framework boundary
- public operator surfaces owned by the framework
- the unified framework CLI
- support for Tigrcorn, Uvicorn, Hypercorn, and Gunicorn as supported serving paths

## Current-target surfaces already closed in checkpoints 5 through 12

### OAS / docs / schema

- OpenAPI document emission at explicit `3.1.0`
- explicit `jsonSchemaDialect` set to Draft 2020-12
- `components.schemas`
- request body emission
- response emission
- path/query parameter emission
- `components.securitySchemes`
- operation-level `security` derived from `secdeps`
- mounted `/openapi.json`
- mounted Swagger UI at `/docs`
- mounted `/openrpc.json`
- mounted Lens / OpenRPC UI at `/lens`
- mounted JSON Schema bundle at `/schemas.json`
- mounted AsyncAPI spec at `/asyncapi.json`

### OAS security schemes

- `apiKey`
- `http` Basic
- `http` Bearer
- `oauth2`
- `openIdConnect`
- `mutualTLS`

### JSON-RPC / OpenRPC

- explicit JSON-RPC 2.0 target in the framework docs/runtime surface
- OpenRPC emission at explicit `1.2.6`
- JSON-RPC method envelope / notification / docs alignment covered by current tests

### Retained exact RFC rows proved in Gate C

- RFC 7235 — framework-owned HTTP authentication challenge semantics
- RFC 7617 — HTTP Basic parsing and challenge behavior
- RFC 6750 — HTTP Bearer token parsing and challenge behavior

### Operator surfaces closed in Phase 7 and proved in Gate B

- static files
- cookies
- streaming responses
- WebSockets
- WHATWG SSE
- forms / multipart
- upload handling
- bounded built-in middleware catalog
- generic auth surface explicitly kept dependency/hook-based only

### CLI surface closed in Phase 8 and proved in Gate B

- `tigrbl run`
- `tigrbl serve`
- `tigrbl dev`
- `tigrbl routes`
- `tigrbl openapi`
- `tigrbl openrpc`
- `tigrbl doctor`
- `tigrbl capabilities`
- `--server {tigrcorn,uvicorn,hypercorn,gunicorn}`
- `--host`
- `--port`
- `--reload`
- `--workers`
- `--root-path`
- `--proxy-headers`
- `--uds`
- `--docs-path`
- `--openapi-path`
- `--openrpc-path`
- `--lens-path`

## Certification infrastructure established in Phase 9 and preserved in Phase 14

Phase 9 created the durable evidence model. Phase 13 promoted the exact chosen dev bundle into the current stable release. Phase 14 opens a new planning-only dev line without changing the frozen release bundle.

Established now:

- `docs/conformance/EVIDENCE_MODEL.md`
- `docs/conformance/EVIDENCE_REGISTRY.json`
- governed promotion-source dev bundle under `docs/conformance/dev/0.3.18.dev1/`
- governed active next-line dev bundle under `docs/conformance/dev/0.3.19.dev1/`
- historical stable scaffold under `docs/conformance/releases/0.3.17/`
- promoted stable release bundle under `docs/conformance/releases/0.3.18/`
- evidence-lane CI workflow for:
  - unit
  - integration
  - spec conformance
  - security / negative
  - docs UI smoke
  - CLI smoke
  - operator-surface smoke
  - server compatibility smoke
  - clean-room package tests

## Current-target rows explicitly de-scoped before Gate C

### Exact RFC rows de-scoped in Phase 6

- OIDC Core 1.0 exact closure
- RFC 6749 exact OAuth 2.0 closure
- RFC 7519 exact JWT closure
- RFC 7636 exact PKCE closure
- RFC 8414 exact authorization-server metadata closure
- RFC 8705 exact OAuth 2.0 mutual-TLS closure
- RFC 9110 exact framework-owned semantics closure
- RFC 9449 exact DPoP closure

### Docs/UI rows de-scoped in Phase 7

- AsyncAPI UI (spec emission kept)
- JSON Schema UI (spec emission kept)
- OIDC discovery/docs surface

The de-scopes above keep the current target honest. They do **not** remove the already-closed OAS security-scheme rows for `oauth2`, `openIdConnect`, or `mutualTLS`, and they do **not** remove the emitted `/asyncapi.json` or `/schemas.json` surfaces.

## Current-target surfaces still missing

None.

## Frozen release identity

- stable release version: `0.3.18`
- source dev build: `0.3.18.dev1`
- facade package metadata path for the promoted release history: `pkgs/core/tigrbl/pyproject.toml` (current working tree has advanced past the release)
- stable release bundle: `docs/conformance/releases/0.3.18/`

## Active next-line identity

- active working-tree version: `0.3.19.dev1`
- active dev bundle: `docs/conformance/dev/0.3.19.dev1/`
- next-target planning document: `docs/conformance/NEXT_TARGETS.md`

## Deferred next-target program

The datatype/table program remains outside the frozen `0.3.18` release claim set and is now governed as the active next-target program in `docs/conformance/NEXT_TARGETS.md`.
