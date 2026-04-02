# Implementation Map

This document maps the frozen current-target rows and the Phase 14 handoff controls to concrete code, tests, blockers, owners, and closure paths.

Owner labels in this checkpoint are subsystem owners, not named individuals:

- **Governance**
- **Docs & Runtime**
- **Auth & Security**
- **Protocol / RPC Runtime**
- **Operator Surface**
- **CLI / Developer Experience**
- **Next-target program**
- **Server/runtime boundary**

## Phase 14 handoff and next-target isolation

| Target | Status | Owner | Code / docs locations | Test evidence | Blocker / gap | Closure path |
|---|---|---|---|---|---|---|
| release-history freeze after promotion | verified in checkpoint | Governance | `docs/conformance/CURRENT_TARGET.md`, `docs/conformance/CURRENT_STATE.md`, `docs/conformance/NEXT_TARGETS.md`, `docs/adr/ADR-0011-post-promotion-release-history-freeze.md` | `tools/ci/tests/test_phase14_handoff.py` | — | keep `0.3.18` frozen as governed release history |
| active next-line dev bundle scaffold | verified in checkpoint | Governance | `docs/conformance/dev/0.3.19.dev1/`, `pkgs/core/tigrbl/pyproject.toml`, `docs/governance/VERSIONING_POLICY.md` | `tools/ci/tests/test_phase14_handoff.py` | no implementation closure yet | keep planning language only until real next-target work lands |
| datatype/table program isolation | verified in checkpoint | Next-target program | `docs/conformance/NEXT_TARGETS.md`, `docs/adr/ADR-0010-deferred-next-target-datatype-table-program.md`, `docs/adr/ADR-0012-next-target-datatype-table-program-activation.md` | `tools/ci/tests/test_phase14_handoff.py` | implementation not started in this checkpoint | keep next-target planning out of the frozen `0.3.18` release claim set |

## Governance and repository controls

## Gate B surface-closure proof

| Target | Status | Owner | Code / docs locations | Test evidence | Blocker / gap | Closure path |
|---|---|---|---|---|---|---|
| Gate B surface-closure validator | implemented | Governance | `tools/ci/validate_gate_b_surface_closure.py` | `tools/ci/tests/test_gate_b_surface_closure.py` | — | Keep the validator synchronized with the claim registry and current-target docs. |
| Gate B workflow | implemented | Governance | `.github/workflows/gate-b-surface-closure.yml` | `docs/conformance/audit/2026/p10-gate-b/README.md` | — | Keep the workflow aligned to the governed docs/operator/CLI proof slices. |
| Docs UI rows closed or explicitly de-scoped | verified in checkpoint | Docs & Runtime | `docs/conformance/CURRENT_TARGET.md`, `docs/developer/operator/docs-ui.md` | `pkgs/core/tigrbl_tests/tests/i9n/test_mountable_openapi_uvicorn.py`, `pkgs/core/tigrbl_tests/tests/i9n/test_mountable_swagger_uvicorn.py`, `pkgs/core/tigrbl_tests/tests/i9n/test_mountable_openrpc_uvicorn.py`, `pkgs/core/tigrbl_tests/tests/i9n/test_mountable_lens_uvicorn.py`, `pkgs/core/tigrbl_tests/tests/unit/test_phase7_operator_surface_docs_parity.py` | — | Preserve the closed/de-scoped state without reopening surface gaps. |
| Operator-surface rows closed | verified in checkpoint | Operator Surface | `docs/conformance/CURRENT_TARGET.md`, `docs/developer/operator/` | `pkgs/core/tigrbl_tests/tests/unit/test_phase7_operator_surface_closure.py`, `pkgs/core/tigrbl_tests/tests/unit/test_phase7_operator_surface_docs_parity.py` | — | Preserve the closed surface without widening claims. |
| CLI rows closed | verified in checkpoint | CLI / Developer Experience | `pkgs/core/tigrbl/tigrbl/cli.py`, `docs/developer/CLI_REFERENCE.md` | `pkgs/core/tigrbl_tests/tests/unit/test_phase8_cli_cmds.py`, `pkgs/core/tigrbl_tests/tests/unit/test_phase8_cli_srv.py` | — | Preserve the unified CLI command/flag surface and runner dispatch smoke. |

| Target | Status | Owner | Code locations | Test evidence | Blocker / gap | Closure path |
|---|---|---|---|---|---|---|
| package layout validation | implemented | Governance | `tools/ci/validate_package_layout.py` | governance validator suite + policy workflow | — | keep green |
| doc-pointer validation | implemented | Governance | `tools/ci/validate_doc_pointers.py` | governance validator suite + policy workflow | — | keep green |
| root-clutter validation | implemented | Governance | `tools/ci/validate_root_clutter.py` | governance validator suite + policy workflow | — | keep green |
| claim-language lint | implemented | Governance | `tools/ci/lint_claim_language.py` | governance validator suite + policy workflow | — | keep green |
| path-length validation | implemented | Governance | `tools/ci/path_length_policy.py`<br>`tools/ci/validate_path_lengths.py` | governance validator suite + policy workflow | — | keep green |
| Gate A manifest validation | implemented | Governance | `tools/ci/validate_boundary_freeze_manifest.py` | policy workflow | — | refresh manifest when controlled docs change |
| release-note claim lint | implemented | Governance | `tools/ci/lint_release_note_claims.py` | policy workflow | — | keep release-note claims anchored to supported rows only |

## Docs, spec, and RPC surfaces

| Target | Status | Owner | Code locations | Test evidence | Blocker / gap | Closure path |
|---|---|---|---|---|---|---|
| OpenAPI 3.1.0 emission | verified in checkpoint | Docs & Runtime | `pkgs/core/tigrbl_concrete/tigrbl_concrete/system/docs/openapi/schema.py` | existing Phase 5 tests | — | preserve snapshot lane |
| JSON Schema Draft 2020-12 declaration | verified in checkpoint | Docs & Runtime | `pkgs/core/tigrbl_concrete/tigrbl_concrete/system/docs/openapi/schema.py` | existing Phase 5 tests | — | preserve snapshot lane |
| mounted `/openapi.json` and `/docs` | verified in checkpoint | Docs & Runtime | docs mount helpers + app mounts | existing docs tests | — | preserve mounted parity |
| JSON-RPC 2.0 current surface | verified in checkpoint | Protocol / RPC Runtime | jsonrpc helpers/models | existing JSON-RPC tests | — | preserve envelope/error/docs alignment |
| OpenRPC 1.2.6 emission + mounted `/openrpc.json` + `/lens` | verified in checkpoint | Protocol / RPC Runtime | openrpc/lens docs modules | existing OpenRPC tests | — | preserve mounted parity |
| mounted `/schemas.json` JSON Schema bundle | verified in checkpoint | Docs & Runtime | `pkgs/core/tigrbl_concrete/tigrbl_concrete/system/docs/json_schema.py` | Phase 7 operator pytest slice | interactive UI de-scoped | keep spec endpoint; UI stays de-scoped |
| mounted `/asyncapi.json` AsyncAPI spec | verified in checkpoint | Docs & Runtime | `pkgs/core/tigrbl_concrete/tigrbl_concrete/system/docs/asyncapi.py` | Phase 7 operator pytest slice | interactive UI de-scoped | keep spec endpoint; UI stays de-scoped |

## Retained RFC / security rows

| Target | Status | Owner | Code locations | Test evidence | Blocker / gap | Closure path |
|---|---|---|---|---|---|---|
| RFC 7235 challenge semantics | verified in checkpoint | Auth & Security | Basic/Bearer deps + executor/header propagation | existing Phase 6 tests | — | preserve auth challenge lane |
| RFC 7617 Basic parsing/challenge behavior | verified in checkpoint | Auth & Security | `http_basic.py` | existing Phase 6 tests | — | preserve auth challenge lane |
| RFC 6750 Bearer extraction/challenge behavior | verified in checkpoint | Auth & Security | `http_bearer.py` | existing Phase 6 tests | — | preserve auth challenge lane |

## De-scoped RFC / discovery rows

| Target | Status | Owner | Code locations | Test evidence | Blocker / gap | Closure path |
|---|---|---|---|---|---|---|
| OIDC Core / discovery beyond OAS scheme modeling | de-scoped | Governance + Auth & Security | target docs + evidence map | docs parity pages | not honestly implemented | keep de-scoped this cycle |
| exact OAuth2 / JWT / PKCE / metadata / mTLS / DPoP rows | de-scoped | Governance + Auth & Security | target docs + evidence map | evidence map | not honestly implemented | keep de-scoped this cycle |

## Operator surfaces closed in Phase 7

| Target | Status | Owner | Code locations | Test evidence | Blocker / gap | Closure path |
|---|---|---|---|---|---|---|
| static files | verified in checkpoint | Operator Surface | `pkgs/core/tigrbl_concrete/tigrbl_concrete/system/static.py` | `pkgs/core/tigrbl_tests/tests/unit/test_phase7_operator_surface_closure.py` | — | preserve mount semantics |
| cookies | verified in checkpoint | Operator Surface | request/response cookie helpers | `pkgs/core/tigrbl_tests/tests/unit/test_phase7_operator_surface_closure.py` | — | preserve round-trip semantics |
| streaming responses | verified in checkpoint | Operator Surface | `_streaming_response.py` + ASGI send path | `pkgs/core/tigrbl_tests/tests/unit/test_phase7_operator_surface_closure.py` | — | preserve multi-frame body semantics |
| WebSockets | verified in checkpoint | Operator Surface | `_websocket.py`, `_app.py`, router websocket decorators | `pkgs/core/tigrbl_tests/tests/unit/test_phase7_operator_surface_closure.py` | — | preserve websocket dispatch semantics |
| WHATWG SSE | verified in checkpoint | Operator Surface | `_event_stream_response.py` | `pkgs/core/tigrbl_tests/tests/unit/test_phase7_operator_surface_closure.py` | — | preserve event-stream framing |
| forms / multipart | verified in checkpoint | Operator Surface | `_request.py` form parsing | `pkgs/core/tigrbl_tests/tests/unit/test_phase7_operator_surface_closure.py` | — | preserve parsing semantics |
| upload handling | verified in checkpoint | Operator Surface | `_request.py` uploaded-file model | `pkgs/core/tigrbl_tests/tests/unit/test_phase7_operator_surface_closure.py` | — | preserve file metadata + body semantics |
| bounded middleware catalog | verified in checkpoint | Operator Surface | `_middleware.py`, `_cors_middleware.py`, operator docs | docs parity + existing middleware tests | — | preserve the bounded catalog boundary |
| generic auth surface kept dependency/hook-based only | verified in checkpoint | Operator Surface | existing auth deps + governed docs | docs parity pages | deliberate non-addition of a new auth middleware | preserve this decision in current target docs |
| AsyncAPI UI | de-scoped | Governance + Operator Surface | current target docs + operator docs | docs parity pages | interactive UI not implemented | keep de-scoped this cycle |
| JSON Schema UI | de-scoped | Governance + Operator Surface | current target docs + operator docs | docs parity pages | interactive UI not implemented | keep de-scoped this cycle |
| OIDC discovery/docs surface | de-scoped | Governance + Operator Surface | current target docs + operator docs | docs parity pages | discovery/docs not implemented | keep de-scoped this cycle |

## CLI and operator tooling

| Target | Status | Owner | Code locations | Test evidence | Blocker / gap | Closure path |
|---|---|---|---|---|---|---|
| unified `tigrbl` CLI and required commands/flags | verified in checkpoint | CLI / Developer Experience | `pkgs/core/tigrbl/tigrbl/cli.py`<br>`pkgs/core/tigrbl/tigrbl/__main__.py`<br>`pkgs/core/tigrbl/pyproject.toml` | `pkgs/core/tigrbl_tests/tests/unit/test_phase8_cli_cmds.py`<br>`pkgs/core/tigrbl_tests/tests/unit/test_phase8_cli_srv.py` | later installed-package/live-network smoke remains part of the evidence/reproducibility gates | preserve the command/flag surface and carry it into the later clean-room evidence lanes |
| supported-server runner dispatch/config smoke | verified in checkpoint | CLI / Developer Experience | `pkgs/core/tigrbl/tigrbl/cli.py`<br>`.github/workflows/cli-smoke.yml` | `pkgs/core/tigrbl_tests/tests/unit/test_phase8_cli_srv.py` | this is runner-dispatch/config smoke, not yet full installed-package compatibility certification | preserve this lane and extend it in later evidence/reproducibility gates |

## Evidence-lane build-out in Phase 9

| Target | Status | Owner | Code locations | Test evidence | Blocker / gap | Closure path |
|---|---|---|---|---|---|---|
| claim-to-evidence mapping registry | verified in checkpoint | Governance | `docs/conformance/EVIDENCE_REGISTRY.json`<br>`tools/ci/validate_evidence_registry.py` | `tools/ci/tests/test_evidence_registry.py` | — | keep every claim row mapped whenever claims, tests, workflows, or artifact paths change |
| governed dev-bundle structure | verified in checkpoint | Governance | `docs/conformance/dev/0.3.18.dev1/` | `tools/ci/tests/test_evidence_registry.py` | exact chosen build retained as the promotion source bundle | keep the dev bundle frozen as the source evidence for the promoted release |
| governed stable-release bundle structure | verified in checkpoint | Governance | `docs/conformance/releases/0.3.18/` | `tools/ci/tests/test_evidence_registry.py`, `tools/ci/tests/test_gate_e_promotion.py` | promoted release bundle is now frozen for the current stable line | keep the promoted bundle synchronized and governed |
| evidence-lane CI workflow | implemented | Governance | `.github/workflows/evidence-lanes.yml` | workflow definition + evidence registry validator | lane outputs feed the promoted release bundle but do not replace gate-specific proofs | keep the lane set stable and synchronize it with any future release-grade changes |
| clean-room package smoke | verified in checkpoint | CLI / Developer Experience | `tools/conformance/clean_room_package_smoke.py` | `docs/conformance/audit/2026/p9-evidence/clean_room_package.log`, `docs/conformance/audit/2026/p12-gate-d/clean_room_package.log` | current release proof still inherits the exact chosen dev-build manifests | preserve the source manifests and keep the release artifact manifest synchronized |

## Deferred next-target rows

| Target | Status | Owner | Code locations | Test evidence | Blocker / gap | Closure path |
|---|---|---|---|---|---|---|
| canonical datatype system as active semantic center | deferred | Next-target program | not part of current-target closure | — | explicitly deferred by boundary | keep out of current certification gates |
| table portability / interoperability / reflection-driven round-trip recovery | deferred | Next-target program | not part of current-target closure | — | explicitly deferred by boundary | keep out of current certification gates |

## Out-of-boundary rows

| Target | Status | Owner | Code locations | Test evidence | Blocker / gap | Closure path |
|---|---|---|---|---|---|---|
| HTTP/1.1 / HTTP/2 / HTTP/3 as framework-owned transport targets | OOB | Server/runtime boundary | delegated to serving/runtime layers | — | not owned by the framework boundary | keep out of framework certification claims |
| QUIC / HPACK / QPACK / server-side TLS termination | OOB | Server/runtime boundary | delegated to serving/runtime layers | — | not owned by the framework boundary | keep out of framework certification claims |
