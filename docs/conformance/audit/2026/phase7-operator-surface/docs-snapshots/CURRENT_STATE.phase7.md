# Current State — Phase 7 Docs UI and Operator-Surface Closure

## Scope and method

This document carries forward the Phase 6 RFC/security checkpoint and records the Phase 7 work completed against the docs UI and public operator surfaces.

Phase 7 focused on:

- keeping the existing OpenAPI / Swagger / OpenRPC / Lens surfaces intact
- adding first-class JSON Schema and AsyncAPI spec endpoints
- de-scoping the unimplemented AsyncAPI UI, JSON Schema UI, and OIDC discovery/docs surfaces
- closing the current-target operator surfaces for static files, cookies, streaming responses, WebSockets, WHATWG SSE, forms/multipart, upload handling, and the bounded middleware catalog
- explicitly keeping the generic auth surface dependency/hook-based only for this cycle

The current state below is grounded in:

1. direct code inspection of the Phase 7 tree
2. the existing Phase 5 and Phase 6 evidence
3. direct inspection of the governed documentation tree
4. execution of the repository policy validators under `tools/ci/`
5. execution of the standalone Phase 7 pytest slice preserved under `docs/conformance/audit/2026/phase7-operator-surface/`

## Certification status

This checkpoint does **not** justify a Tier 3 current-boundary certification claim.

The repository is **not** honestly describable at this checkpoint as:

- certifiably fully featured
- certifiably fully RFC/spec/standard compliant

within the declared current target boundary.

The Phase 7 deliverable closes the operator-surface rows and the docs parity decisions for this cycle, but the unified CLI and later promotion/evidence gates remain open.

## Exact docs/UI state

### Kept and verified now

- `/openapi.json`
- Swagger UI at `/docs`
- `/openrpc.json`
- Lens / OpenRPC UI at `/lens`
- `/schemas.json` as a JSON Schema bundle endpoint
- `/asyncapi.json` as an AsyncAPI spec endpoint

### Explicitly de-scoped in this checkpoint

- AsyncAPI UI
- JSON Schema UI
- OIDC discovery/docs surface

The current cycle keeps the emitted spec endpoints and de-scopes the missing interactive UI/discovery rows rather than overstating closure.

## Exact operator-surface state

### Closed now

| Surface | Current state | Evidence |
|---|---|---|
| static files | closed | `pkgs/core/tigrbl_concrete/tigrbl_concrete/system/static.py`, `pkgs/core/tigrbl_tests/tests/unit/test_operator_surface_closure.py` |
| cookies | closed | `pkgs/core/tigrbl_concrete/tigrbl_concrete/_concrete/_request.py`, `pkgs/core/tigrbl_concrete/tigrbl_concrete/_concrete/_response.py`, `pkgs/core/tigrbl_tests/tests/unit/test_operator_surface_closure.py` |
| streaming responses | closed | `pkgs/core/tigrbl_concrete/tigrbl_concrete/_concrete/_streaming_response.py`, `pkgs/core/tigrbl_atoms/tigrbl_atoms/atoms/egress/asgi_send.py`, `pkgs/core/tigrbl_tests/tests/unit/test_operator_surface_closure.py` |
| WebSockets | closed | `pkgs/core/tigrbl_concrete/tigrbl_concrete/_concrete/_websocket.py`, `pkgs/core/tigrbl_concrete/tigrbl_concrete/_concrete/_app.py`, `pkgs/core/tigrbl_tests/tests/unit/test_operator_surface_closure.py` |
| WHATWG SSE | closed | `pkgs/core/tigrbl_concrete/tigrbl_concrete/_concrete/_event_stream_response.py`, `pkgs/core/tigrbl_tests/tests/unit/test_operator_surface_closure.py` |
| forms / multipart | closed | `pkgs/core/tigrbl_concrete/tigrbl_concrete/_concrete/_request.py`, `pkgs/core/tigrbl_tests/tests/unit/test_operator_surface_closure.py` |
| upload handling | closed | `pkgs/core/tigrbl_concrete/tigrbl_concrete/_concrete/_request.py`, `pkgs/core/tigrbl_tests/tests/unit/test_operator_surface_closure.py` |
| bounded built-in middleware catalog | closed | `pkgs/core/tigrbl_concrete/tigrbl_concrete/_concrete/_middleware.py`, `pkgs/core/tigrbl_concrete/tigrbl_concrete/_concrete/_cors_middleware.py`, docs under `docs/developer/operator/middleware-catalog.md` |

### Auth-surface decision closed now

The framework keeps auth **dependency/hook-based only** in the current cycle.

That means:

- security dependencies remain the first-class auth surface
- `AuthNProvider`, `set_auth(...)`, `allow_anon`, and authz callback hooks remain the governing abstractions
- the framework does **not** add a new monolithic generic auth middleware abstraction in this cycle

## Exact CLI state

There is still **no unified top-level `tigrbl` CLI** in the tree.

The target command set recorded in `docs/developer/CLI_REFERENCE.md` remains absent:

- `tigrbl run`
- `tigrbl serve`
- `tigrbl dev`
- `tigrbl routes`
- `tigrbl openapi`
- `tigrbl openrpc`
- `tigrbl doctor`
- `tigrbl capabilities`

The explicit `--server {tigrcorn,uvicorn,hypercorn,gunicorn}` flag contract also remains absent.

## Evidence-backed conclusions

1. The current cycle now has no unresolved current-target docs/operator-surface gaps.
2. The operator boundary is closed by a mix of implementation work and explicit de-scoping where the UI/discovery rows were not honestly implemented.
3. The bounded middleware catalog and dependency/hook-based auth decision are now explicit rather than implied.
4. The major remaining current-cycle blocker is the missing unified CLI surface, followed by the later reproducibility/promotion gates.

## Authoritative companion documents

- `docs/conformance/IMPLEMENTATION_MAP.md`
- `docs/conformance/RFC_SECURITY_EVIDENCE_MAP.md`
- `docs/conformance/NEXT_STEPS.md`
- `docs/conformance/CLAIM_REGISTRY.md`
- `docs/conformance/audit/2026/phase7-operator-surface/README.md`
