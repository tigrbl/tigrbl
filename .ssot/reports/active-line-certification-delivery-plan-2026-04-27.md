# Active Line Certification Delivery Plan

## Run Context

- Date: 2026-04-27
- Active package line: `0.3.19.dev1`
- Registry command path used in this sandbox: `.venv/Scripts/ssot.exe`
- Registry validation result: passed with warnings

The frozen `0.3.18` release remains the only fully certified release boundary in the documentation set. The active line cannot honestly be claimed fully featured, fully functional, fully conformant, or fully compliant yet.

## Current Registry State

| Surface | Count |
|---|---:|
| Features | 555 |
| Profiles | 6 |
| Tests | 675 |
| Claims | 242 |
| Evidence | 282 |
| Issues | 6 |
| Risks | 3 |
| Boundaries | 12 |
| Releases | 8 |

Feature implementation status:

| Status | Count |
|---|---:|
| Implemented | 168 |
| Partial | 303 |
| Absent | 84 |

Feature status by horizon:

| Horizon | Implemented | Partial | Absent |
|---|---:|---:|---:|
| Current | 154 | 0 | 0 |
| Explicit | 2 | 0 | 0 |
| Next | 0 | 29 | 26 |
| Backlog | 8 | 167 | 6 |
| Future | 0 | 83 | 52 |
| Out of bounds | 4 | 24 | 0 |

Verification state:

| Entity | Blocking State |
|---|---|
| Claims | 40 blocked, 22 proposed, 75 declared, 79 asserted |
| Tests | 54 planned, 33 blocked, 5 skipped |
| Evidence | 68 planned, 1 failed |
| Issues | 6 open, release-blocking |
| Risks | 3 active |

## Delivery Tracks

### Certification Scope

Create reusable profiles for the main certification and capability surfaces. This run completed that through the SSOT CLI:

- `prf:tigrbl-active-line-certification-closure`
- `prf:tigrbl-public-operator-surface`
- `prf:tigrbl-extension-and-plugin-surface`
- `prf:tigrbl-runtime-protocol-conformance`
- `prf:tigrbl-production-hardening`
- `prf:tigrbl-development-governance`

Exit condition: each profile evaluates cleanly, has only implemented in-bound features, and has satisfying claims at the required tier.

### Current-Line Blockers

Close the remaining current partial row:

- `feat:runtime-executor-doc-endpoint-parity-001`

Exit condition: the row is implemented, linked to passing tests, linked to passed evidence, and backed by satisfying claims.

### Security Contract Closure

Resolve the existing critical/high release-blocking issues:

- unauthenticated generated REST reads
- unauthenticated generated JSON-RPC reads
- generated OpenAPI operations missing auth security
- generated OpenRPC methods missing auth security
- JSON-RPC create validation and persistence error sanitization

Exit condition: runtime policy and generated OpenAPI/OpenRPC policy agree, negative tests pass, and linked evidence replaces the active `rsk:security-contract-auth-drift-001` risk.

### Datatype And Table Program

Implement the next-target datatype/table rows:

- datatype catalog and semantic center
- `ColumnSpec.datatype`
- adapter and registry contract
- engine datatype lowering bridge
- reflected datatype mapping
- multi-engine table portability
- schema reflection round-trip recovery

Exit condition: Python contracts, engine lowerers, reflection tests, and registry evidence all certify the next-target datatype surface.

### Transport Dispatch And Runtime Protocols

Finish the next-target transport dispatch rows:

- remove transport bypasses
- make KernelPlan and atoms own transport lookup and matching
- restore REST/JSON-RPC parity through one dispatch path
- close the skipped transport-dispatch parity placeholder test

Exit condition: the skipped placeholder is replaced by passing tests and the runtime protocol profile evaluates cleanly.

### Production Hardening

Close hardening rows for:

- RFC 8785 JCS vectors, canonicalizer, and rejection semantics
- runtime DDL initialization and request hot-path exclusion
- schema readiness fail-closed behavior
- Python/Rust engine session lifecycle
- Python/Rust performance, callgraph, and microbenchmark evidence

Exit condition: hardening profile evaluates cleanly and release-blocking risks are mitigated or retired.

### Claim, Test, And Evidence Closure

Convert non-certifying proof chain records into usable certification evidence:

- blocked/proposed/declared/asserted claims must become evidenced/certified where in scope
- planned/blocked/skipped tests must either pass or move out of the active certification boundary
- planned or failed evidence must be replaced with passed evidence or scoped out explicitly
- server-support claims without evidence need direct evidence links or honest out-of-bound handling

Exit condition: profile evaluation failures no longer cite missing satisfying claims, non-passing tests, or non-passed evidence for in-bound features.

## Work Completed In This Run

1. Validated the registry through the repo-local SSOT CLI entrypoint.
2. Added six reusable SSOT profiles for certification, operator, extension/plugin, protocol, production hardening, and development governance surfaces.
3. Added `iss:active-line-certification-closure-blocked-001` to track active-line closure as a release-blocking issue.
4. Added three release-blocking risks:
   - `rsk:active-line-nonimplemented-feature-claims-001`
   - `rsk:security-contract-auth-drift-001`
   - `rsk:profileless-certification-scope-001`
5. Re-ran `ssot validate . --write-report`; validation passed with warnings that accurately describe remaining certification blockers.
6. Implemented and certified `feat:package-buildability-importability-001`.
7. Repaired package importability blockers in `tigrbl.session`, `tigrbl_spiffe`, and `tigrbl_engine_dataframe`.
8. Replaced the planned package evidence placeholder with passed evidence and certified claim `clm:pkg-buildability-importability-001`.
9. Re-ran and certified the current-line runtime documentation endpoint parity slice:
   - `pkgs\core\tigrbl_runtime\tests\test_rust_runtime_demo_docs_surface.py`: 5 passed.
   - `pkgs\core\tigrbl_tests\tests\unit\test_jsonrpc_openrpc.py`: 19 passed.
   - `feat:runtime-executor-doc-endpoint-parity-001` is now implemented.
10. Re-ran and certified the HTTP route, documentation support, declared-surface docs, and operator surface slices:
   - HTTP route registration, system docs builders, and declarative decorator surface: 19 passed.
   - Operator surface closure, operator docs parity, and declared-surface docs: 10 passed.
   - Added `evd:operator-docs-http-surface-20260427`.
   - Certified `clm:docs-support-001`, `clm:docs-support-002`, `clm:http-route-001`, `clm:http-route-002`, `clm:http-route-003`, and `clm:op-003` through `clm:op-007`.
   - Marked `feat:http-route-001`, `feat:docs-support-001`, `feat:declared-surface-docs-extension-001`, and the streaming, WebSocket, SSE, form/multipart, and uploaded-file operator surface rows implemented.
11. Detached obsolete failed evidence `evd:tigrbl-tests-current-failing-pytest` from tests that now have passing closure evidence, while preserving the historical evidence row.

## Remaining Certification Blockers

The active certification profile currently fails because multiple linked features are not implemented and lack satisfying T2+ claims. Representative blockers include:

- `feat:appspec-contract-001`
- `feat:appspec-routerspec-composition-001`
- `feat:canonical-datatype-catalog-semantic-center-001`
- `feat:columnspec-datatype-attachment-point-001`
- `feat:engine-datatype-lowering-registry-bridge-001`
- `feat:executor-dispatch-removal-001`
- `feat:kernelplan-dispatch-ownership-001`
- `feat:rfc-8785-jcs-canonicalizer-001`
- `feat:rfc-8785-jcs-conformance-vectors-001`
- `feat:rfc-8785-jcs-rejection-semantics-001`
- `feat:rust-asgi-boundary-evidence-001`

The package is therefore not certifiably fully featured, fully functional, fully conformant, or fully compliant on the active line. The current and explicit rows are now implemented; the next delivery unit should continue through the security contract blockers, profile evaluation blockers, unlinked legacy claims, unsupported server-support evidence rows, and the remaining next/backlog/future implementation surfaces before broad release certification.

## Security Contract Continuation

Additional work completed later on 2026-04-27:

1. Re-ran the OpenAPI/OpenRPC security metadata checks:
   - `pkgs/core/tigrbl_tests/tests/unit/test_docs_security_parity.py`
   - `pkgs/core/tigrbl_tests/tests/unit/test_openapi_documentation_security_behavior.py`
   - `pkgs/core/tigrbl_tests/tests/unit/test_openrpc_documentation_security_behavior.py`
   - Result: 4 passed.
2. Re-ran the pre-transaction security dependency execution checks:
   - `pkgs/core/tigrbl_tests/tests/test_secdeps_execute_in_pre_tx.py`
   - Result: 5 passed.
3. Added passed evidence `evd:security-contract-docs-proof-20260427` pointing at `.ssot/reports/security-contract-docs-proof-2026-04-27.md`.
4. Certified `clm:pre-tx-dependency-execution-contract-001`.
5. Marked `feat:pre-tx-security-dependency-execution-001` implemented.
6. Closed these release-blocking issues with linked proof:
   - `iss:jsonrpc-create-missing-required-fields-leaks-persistence-errors-001`
   - `iss:openapi-generated-operations-missing-auth-security-001`
   - `iss:openrpc-generated-methods-missing-auth-security-001`

Current remaining release-blocking issues at that point:

- `iss:generated-rest-read-allows-unauthenticated-access-001`
- `iss:generated-jsonrpc-read-allows-unauthenticated-access-001`
- `iss:active-line-certification-closure-blocked-001`

Next delivery unit: decide and implement the generated CRUD authentication policy. The two valid choices are protected-by-default generated CRUD, or explicit public-by-default generated CRUD with OpenAPI/OpenRPC public-operation declarations. Until that policy is implemented and evidenced, the active line still cannot be certified fully compliant or fully conformant.

## Generated CRUD Auth Policy Continuation

Additional work completed later on 2026-04-27:

1. Chose the explicit public-by-default generated CRUD policy:
   generated CRUD operations remain public unless app/router/table/op security
   dependencies are configured.
2. Added `x-tigrbl-auth` to OpenAPI operations and OpenRPC methods:
   - `policy: public-by-default` for operations with no security dependencies.
   - `policy: protected` for operations with concrete security requirements.
3. Added focused regression coverage:
   - REST/OpenAPI protected and public-default projection.
   - OpenRPC public-default projection.
4. Verified:
   - `pkgs/core/tigrbl_tests/tests/unit/test_operator_auth_surface_contracts.py`
   - `pkgs/core/tigrbl_tests/tests/unit/test_jsonrpc_openrpc.py`
   - Result: 24 passed, 1 existing expected xfail.
5. Added passed evidence `evd:generated-crud-auth-policy-proof-20260427`.
6. Added certified claim `clm:generated-crud-public-default-auth-policy-20260427`.
7. Linked and closed:
   - `iss:generated-rest-read-allows-unauthenticated-access-001`
   - `iss:generated-jsonrpc-read-allows-unauthenticated-access-001`
8. Linked and mitigated `rsk:security-contract-auth-drift-001`.
9. Re-ran `ssot validate . --write-report`; validation passed with warnings.

Current remaining release-blocking issue:

- `iss:active-line-certification-closure-blocked-001`

Current remaining active risks:

- `rsk:active-line-nonimplemented-feature-claims-001`
- `rsk:profileless-certification-scope-001`

Next delivery unit: close the active-line certification profile blockers by
working down the nonimplemented feature list, beginning with AppSpec/RouterSpec
contract closure and the datatype/table program, then transport dispatch and
production hardening. The package still cannot honestly be certified fully
featured, fully functional, fully conformant, or fully compliant until those
linked rows are implemented, tested, evidenced, and moved to satisfying claims.

## AppSpec RouterSpec Contract Continuation

Additional work completed later on 2026-04-27:

1. Verified the linked V4 spec contract slice:
   - `pkgs/core/tigrbl_tests/v4/tests/spec/test_master_app_spec_surface.py`
   - `pkgs/core/tigrbl_tests/v4/tests/spec/test_spec_export_surface.py`
   - `pkgs/core/tigrbl_tests/v4/tests/spec/test_appspec_routerspec_contract.py`
   - `pkgs/core/tigrbl_tests/v4/tests/spec/test_table_column_spec_contract.py`
   - `pkgs/core/tigrbl_tests/v4/tests/spec/test_opspec_response_contract.py`
   - Result: 22 passed.
2. Verified the core AppSpec, RouterSpec, nested-spec, and serde regression slice:
   - `pkgs/core/tigrbl_core/tests/test_app_spec.py`
   - `pkgs/core/tigrbl_core/tests/test_router_spec.py`
   - `pkgs/core/tigrbl_core/tests/test_nested_specs_only.py`
   - `pkgs/core/tigrbl_core/tests/test_spec_serde.py`
   - Result: 17 passed.
3. Added proof report `evd:appspec-routerspec-composition-pytest` now points at:
   - `.ssot/reports/appspec-routerspec-composition-proof-2026-04-27.md`
4. Marked these feature rows implemented through the SSOT CLI:
   - `feat:appspec-contract-001`
   - `feat:routerspec-contract-001`
   - `feat:appspec-routerspec-composition-001`

## Datatype Table Program Continuation

Additional work completed later on 2026-04-27:

1. Verified the core datatype/table program slice:
   - `pkgs/core/tigrbl_core/tests/test_semantic_datatype_core.py`
   - `pkgs/core/tigrbl_core/tests/test_column_datatype_integration.py`
   - `pkgs/core/tigrbl_core/tests/test_adapter_registry_contract.py`
   - `pkgs/core/tigrbl_core/tests/test_engine_bridge_lowering.py`
   - `pkgs/core/tigrbl_core/tests/test_reflection_roundtrip_recovery.py`
   - `pkgs/core/tigrbl_core/tests/test_engine_family_alignment.py`
   - `pkgs/core/tigrbl_core/tests/test_table_portability_contract.py`
   - `pkgs/core/tigrbl_core/tests/test_schema_roundtrip_recovery.py`
   - Result: 35 passed.
2. Verified base and Rust datatype contract slices:
   - `pkgs/core/tigrbl_base/tests/test_column_datatype_lowering.py`: 1 passed.
   - `cargo test -p tigrbl_rs_spec --test spec_contract`: 9 passed.
3. Added passed evidence:
   - `evd:datatype-table-program-proof-20260427`
   - `.ssot/reports/datatype-table-program-proof-2026-04-27.md`
4. Marked `tst:tcase-0001`, `tst:tcase-0003`, and `tst:tcase-0004` through `tst:tcase-0011` passing.
5. Advanced `clm:next-003` through `clm:next-010` to evidenced.
6. Marked these feature rows implemented through the SSOT CLI:
   - `feat:canonical-datatype-catalog-semantic-center-001`
   - `feat:columnspec-datatype-attachment-point-001`
   - `feat:datatype-adapter-registry-contract-001`
   - `feat:engine-datatype-lowering-registry-bridge-001`
   - `feat:reflected-datatype-mapper-reverse-mapping-001`
   - `feat:default-canonical-engine-family-datatype-alignment-001`
   - `feat:multi-engine-table-portability-interoperability-001`
   - `feat:schema-reflection-roundtrip-recovery-001`

Current remaining release-blocking issue:

- `iss:active-line-certification-closure-blocked-001`

Current remaining active risks:

- `rsk:active-line-nonimplemented-feature-claims-001`
- `rsk:profileless-certification-scope-001`

Next delivery unit: continue into transport dispatch and production hardening.
The live registry still has in-bound partial and absent features, active
release-blocking risks, planned/blocked tests, declared claims, and active
profiles that do not yet evaluate cleanly.

## Current Run Continuation

Additional work completed later on 2026-04-27:

1. Re-verified the AppSpec/RouterSpec contract proof chain:
   - `pkgs/core/tigrbl_tests/v4/tests/spec/test_master_app_spec_surface.py`
   - `pkgs/core/tigrbl_tests/v4/tests/spec/test_spec_export_surface.py`
   - `pkgs/core/tigrbl_tests/v4/tests/spec/test_appspec_routerspec_contract.py`
   - `pkgs/core/tigrbl_tests/v4/tests/spec/test_table_column_spec_contract.py`
   - `pkgs/core/tigrbl_tests/v4/tests/spec/test_opspec_response_contract.py`
   - `pkgs/core/tigrbl_core/tests/test_app_spec.py`
   - `pkgs/core/tigrbl_core/tests/test_router_spec.py`
   - `pkgs/core/tigrbl_core/tests/test_nested_specs_only.py`
   - `pkgs/core/tigrbl_core/tests/test_spec_serde.py`
   - Result: 39 passed.
2. Marked these contract rows implemented through the SSOT CLI:
   - `feat:appspec-contract-001`
   - `feat:routerspec-contract-001`
   - `feat:appspec-routerspec-composition-001`
   - `feat:tablespec-contract-001`
   - `feat:columnspec-contract-001`
   - `feat:storagespec-contract-001`
   - `feat:fieldspec-contract-001`
   - `feat:iospec-contract-001`
   - `feat:foreignkeyspec-contract-001`
   - `feat:opspec-contract-001`
   - `feat:responsespec-contract-001`
3. Certified `clm:appspec-routerspec-composition-contract-001` after claim evaluation passed.
4. Added core-owned `tigrbl_core.canonical_json` with deterministic UTF-8 canonical JSON output and fail-closed rejection for non-finite JSON numbers; `tigrbl.canonical_json` remains an import/export compatibility projection only.
5. Verified the RFC 8785 JCS Python contract:
   - `pkgs/core/tigrbl_tests/tests/unit/test_jcs_canonicalization_contract.py`
   - Result: 5 passed.
6. Added passed evidence `evd:rfc-8785-jcs-python-proof-20260427` pointing at `.ssot/reports/rfc-8785-jcs-python-proof-2026-04-27.md`.
7. Added passing test row `tst:rfc-8785-jcs-python-contract`.
8. Added and certified `clm:rfc-8785-jcs-python-canonicalization-20260427`.
9. Marked these JCS rows implemented through the SSOT CLI:
   - `feat:rfc-8785-jcs-canonicalizer-001`
   - `feat:rfc-8785-jcs-conformance-vectors-001`
   - `feat:rfc-8785-jcs-rejection-semantics-001`
10. Re-ran `ssot validate . --write-report`; validation passed with warnings.

Current live counts after this continuation:

| Surface | Count |
|---|---:|
| Features | 555 |
| Profiles | 6 |
| Tests | 676 |
| Claims | 244 |
| Evidence | 286 |
| Issues | 6 |
| Risks | 3 |

Feature implementation status is now `191` implemented, `283` partial, and
`81` absent. Remaining in-bound nonimplemented features are concentrated in
backlog (`173`), future (`135`), and next (`32`) horizons. The only open
release-blocking issue remains `iss:active-line-certification-closure-blocked-001`.
The active release-blocking risks remain `rsk:active-line-nonimplemented-feature-claims-001`
and `rsk:profileless-certification-scope-001`.

## Executable Proof Guard Continuation

Additional work completed on 2026-04-27T20:03:50-05:00:

1. Removed the stale xfail fallback from
   `pkgs/core/tigrbl_tests/tests/unit/test_jcs_canonicalization_contract.py`.
   The JCS contract now fails closed if both the core-owned helper and its facade projection disappear.
2. Re-ran the RFC 8785 JCS Python contract:
   - `pkgs/core/tigrbl_tests/tests/unit/test_jcs_canonicalization_contract.py`
   - Result: 5 passed.
3. Refreshed the governed SSOT rows through the repo-local CLI:
   - `tst:rfc-8785-jcs-python-contract` remains `passing`.
   - `evd:rfc-8785-jcs-python-proof-20260427` remains `passed` at `T2`.
4. Re-ran `ssot validate . --write-report`; validation passed with warnings.

Current live counts after this continuation:

| Surface | Count |
|---|---:|
| Features | 555 |
| Profiles | 6 |
| Tests | 676 |
| Claims | 244 |
| Evidence | 286 |
| Issues | 6 |
| Risks | 3 |

Feature implementation status remains `191` implemented, `283` partial, and
`81` absent. The package is still not certifiably fully featured or fully
conformant because all six active certification profiles still emit validation
warnings, `iss:active-line-certification-closure-blocked-001` remains open, and
the active risks `rsk:active-line-nonimplemented-feature-claims-001` and
`rsk:profileless-certification-scope-001` remain active.

## Server Support Claim Evidence Continuation

Additional work completed on 2026-04-27T21:04:48-05:00:

1. Re-reviewed the live registry and current profile evaluations.
2. Confirmed current live registry counts:
   - 555 features
   - 244 claims
   - 676 tests
   - 287 evidence rows after this continuation
   - 6 profiles
   - 6 issues
   - 3 risks
3. Confirmed feature implementation status remains:
   - 191 implemented
   - 283 partial
   - 81 absent
4. Verified the governed CLI server-support contract:
   - `pkgs/core/tigrbl_tests/tests/unit/test_cli_srv.py`
   - Result: 21 passed.
5. Added passed evidence:
   - `evd:server-support-cli-contract-proof-20260427`
   - `.ssot/reports/server-support-cli-contract-proof-2026-04-27.md`
6. Linked that evidence to all governed supported-server and out-of-boundary
   server claims:
   - `clm:server-support-tigrcorn-001`
   - `clm:server-support-uvicorn-001`
   - `clm:server-support-hypercorn-001`
   - `clm:server-support-gunicorn-001`
   - `clm:server-support-daphne-001`
   - `clm:server-support-twisted-001`
   - `clm:server-support-granian-001`
7. Marked the linked server-support claims `evidenced` through the SSOT CLI.
8. Marked `tst:pkgs-core-tigrbl_tests-tests-unit-test_cli_srv.py` passing
   through the SSOT CLI.
9. Re-ran `ssot validate . --write-report`; validation passed with warnings.
   The prior server-support no-linked-evidence warnings are closed.

Current remaining validation warnings:

- `clm:blk-001` through `clm:blk-007` have no linked features.
- `clm:cur-001` through `clm:cur-007` have no linked features.
- `clm:evd-001` through `clm:evd-004` have no linked features.
- All six active profiles still emit evaluation warnings.

The active certification profile still fails on unimplemented or non-certifying
features including executor dispatch removal, KernelPlan dispatch ownership,
module alias compatibility, ORM alias compatibility, runtime documentation
endpoint claim support, Python/Rust runtime hardening evidence, and request
hot-path/DDL boundaries. The production hardening profile additionally fails on
concrete security dependency helpers, DDL runtime surfaces, middleware surface
contracts, Gate C checkpoint closure, and runtime performance/readiness rows.

Next delivery unit: close the active-line profile failures by selecting the
smallest still-failing feature cluster with executable tests already present,
then promote the corresponding claim/test/evidence chain through the SSOT CLI.

## Transport Dispatch Parity Continuation

Additional work completed on 2026-04-27T22:05:18-05:00:

1. Replaced the transport-dispatch parity placeholder test with an executable
   REST/JSON-RPC semantic parity regression:
   - `pkgs/core/tigrbl_tests/tests/unit/test_transport_dispatch_parity_contract.py`
2. Replaced the endpoint-keyed JSON-RPC placeholder test with an executable
   core spec contract:
   - `pkgs/core/tigrbl_core/tests/test_jsonrpc_endpoint_binding_spec_contract.py`
3. Verified the new contract slice:
   - Result: 2 passed.
4. Re-verified the existing runtime parity proof slice:
   - `pkgs/core/tigrbl_tests/tests/parity/test_executor_metamorphic_parity.py`
   - `pkgs/core/tigrbl_tests/tests/harness_v3/test_uvicorn_e2e_appspec.py`
   - Result: 2 passed.
5. Added proof report:
   - `.ssot/reports/transport-dispatch-parity-proof-2026-04-27.md`
6. Updated SSOT rows through the repo-local CLI:
   - `tst:transport-dispatch-parity-contract` is `passing`.
   - `evd:transport-dispatch-parity-test` is `passed`.
   - `clm:transport-parity-contract-001` is `evidenced`.
   - `feat:transport-parity-contract-001` is `implemented`.
   - `tst:jsonrpc-endpoint-binding-contract` is `passing`.
   - `evd:transport-dispatch-jsonrpc-test` is `passed`.
   - `clm:jsonrpc-endpoint-key-001` is `evidenced`.

Current live implementation status after this continuation:

| Horizon | Implemented | Partial | Absent |
|---|---:|---:|---:|
| Current | 154 | 0 | 0 |
| Explicit | 2 | 0 | 0 |
| Next | 24 | 8 | 23 |
| Backlog | 8 | 167 | 6 |
| Future | 0 | 83 | 52 |
| Out of bounds | 4 | 24 | 0 |

Remaining next-target blockers:

- `feat:executor-dispatch-removal-001`
- `feat:kernelplan-dispatch-ownership-001`
- `feat:transport-bypass-removal-001`
- `feat:bootstrappable-table-mixin-001`
- `feat:pre-tx-dependency-execution-001`
- `feat:governed-module-alias-compatibility-001`
- `feat:orm-alias-export-compatibility-001`
- `feat:orm-mixins-alias-compatibility-001`
- Python/Rust DDL, schema-readiness, session lifecycle, transaction hot-path,
  benchmark, callgraph, request-envelope, ASGI-boundary, and 2x-target rows
- `feat:tx-phase-legacy-alias-deprecation-001`

Runtime protocol profile evaluation now passes `feat:transport-parity-contract-001`
but still fails on wider protocol rows including binding-driven ingress,
BindingSpec-to-KernelPlan protocol compilation, executor dispatch removal,
KernelPlan dispatch ownership, JSON-RPC batch/notification behavior, OpenRPC
helper surfaces, transport bypass removal, websocket/webtransport contracts,
and Python/Rust ASGI boundary evidence.

## Runtime Documentation Endpoint Claim Closure

Additional work completed on 2026-04-28:

1. Re-audited the live registry through the repo-local SSOT CLI after the
   transport-dispatch continuation.
2. Verified the runtime documentation endpoint proof slice:
   - `pkgs/core/tigrbl_runtime/tests/test_rust_runtime_demo_docs_surface.py`
   - `pkgs/core/tigrbl_tests/tests/unit/test_jsonrpc_openrpc.py`
   - Result: 25 passed.
3. Added proof report:
   - `.ssot/reports/runtime-doc-endpoint-parity-proof-2026-04-28.md`
4. Updated SSOT rows through the repo-local CLI:
   - `evd:runtime-doc-endpoint-parity-proof-20260428` is `passed`.
   - `clm:runtime-doc-endpoint-parity-contract-20260428` is `certified`.
5. Re-ran claim evaluation for
   `clm:runtime-doc-endpoint-parity-contract-20260428`; it passed and
   recommended `certified`.
6. Re-ran active-line profile evaluation. The row
   `feat:runtime-executor-doc-endpoint-parity-001` now passes with satisfying
   T2 claim `clm:runtime-doc-endpoint-parity-contract-20260428`.
7. Re-ran `ssot validate . --write-report`; validation passed with warnings.

Current live counts after this continuation:

| Surface | Count |
|---|---:|
| Features | 593 |
| Profiles | 6 |
| Tests | 679 |
| Claims | 248 |
| Evidence | 292 |
| Issues | 8 |
| Risks | 4 |
| Boundaries | 12 |
| Releases | 8 |
| ADRs | 131 |
| SPECs | 140 |

Feature implementation status is now `230` implemented, `282` partial, and
`81` absent. Remaining nonimplemented features are concentrated in backlog
(`173`), future (`135`), next (`31`), and out-of-bounds (`24`) horizons.

The remaining open issues are:

- `iss:active-line-certification-closure-blocked-001`
- `iss:certifiable-package-proof-chain-gap-001`

The remaining active risks are:

- `rsk:active-line-nonimplemented-feature-claims-001`
- `rsk:profileless-certification-scope-001`
- `rsk:unverified-package-proof-chain-001`

The active-line profile now fails on the remaining concrete blockers:

- `feat:bootstrappable-table-mixin-001`
- `feat:executor-dispatch-removal-001`
- `feat:governed-module-alias-compatibility-001`
- `feat:kernelplan-dispatch-ownership-001`
- `feat:orm-alias-export-compatibility-001`
- `feat:orm-mixins-alias-compatibility-001`
- `feat:pre-tx-dependency-execution-001`
- `feat:pre-tx-security-dependency-execution-001`
- `feat:python-asgi-boundary-evidence-001`
- `feat:python-direct-runtime-microbench-001`
- `feat:python-engine-session-lifecycle-001`
- `feat:python-request-envelope-contract-001`
- `feat:python-request-hot-path-no-ddl-001`
- `feat:python-runtime-2x-target-comparison-001`
- `feat:python-runtime-callgraph-export-001`
- `feat:python-runtime-ddl-initialization-boundary-001`
- `feat:python-runtime-performance-baseline-001`
- `feat:python-schema-readiness-fail-closed-001`
- `feat:python-transaction-hot-path-001`
- `feat:rust-asgi-boundary-evidence-001`
- `feat:rust-direct-runtime-microbench-001`

Next delivery unit: select one of the remaining active-line blockers with
existing executable coverage, prove or implement it, then promote the
claim/test/evidence chain through the SSOT CLI.
