# Full-Feature Certification Target

Generated: 2026-05-10

This is a derived planning view over `.ssot/registry.json`. The registry remains authoritative.

- Boundary: `bnd:tigrbl-full-feature-certification-001`
- Boundary status: `draft`
- Active in-scope gaps: `167`
- Absent: `51`
- Partial: `116`
- Ready for freeze: `117`
- Blocked from freeze: `50`

Rows are excluded when they are deprecated, obsolete, removed, descoped, or explicitly out of bounds.

## Concern Summary

| Concern | Absent | Partial | Total |
|---|---:|---:|---:|
| Canonical operation families and exports | 0 | 2 | 2 |
| Documentation, schema, UIX, and mount surfaces | 3 | 17 | 20 |
| Engine, DDL, schema, and datatype surfaces | 2 | 19 | 21 |
| Governance, conformance, profiles, tests, and evidence | 0 | 7 | 7 |
| Kernel, plan, cache, and dispatch ownership | 1 | 11 | 12 |
| Operator, middleware, security, and request helper surfaces | 0 | 12 | 12 |
| Protocol dispatch, framing, phases, and runtime taxonomy | 22 | 12 | 34 |
| Public API, helpers, facades, compatibility, and aliases | 0 | 12 | 12 |
| Python/Rust runtime lanes and performance | 23 | 1 | 24 |
| REST, JSON-RPC, Uvicorn, routing, and error parity | 0 | 23 | 23 |

## Freeze Blockers

The boundary must remain draft until every row has linked specs, required tests, claims, target claim tier, and executable evidence.

| Feature | Status | Concern | Blockers |
|---|---|---|---|
| `feat:apikey-security-dependency-001` | partial | Operator, middleware, security, and request helper surfaces | missing_claim_link |
| `feat:attrdict-contract-001` | partial | Public API, helpers, facades, compatibility, and aliases | missing_claim_link, missing_target_claim_tier |
| `feat:backgroundtask-concrete-class-001` | partial | Operator, middleware, security, and request helper surfaces | missing_claim_link |
| `feat:bind-helper-surface-001` | partial | Public API, helpers, facades, compatibility, and aliases | missing_claim_link, missing_target_claim_tier |
| `feat:cli-module-target-resolution-001` | partial | Governance, conformance, profiles, tests, and evidence | missing_claim_link |
| `feat:cli-path-target-resolution-001` | partial | Governance, conformance, profiles, tests, and evidence | missing_claim_link |
| `feat:cli-shared-target-loader-001` | partial | Governance, conformance, profiles, tests, and evidence | missing_claim_link |
| `feat:cli-target-surface-loading-001` | partial | Governance, conformance, profiles, tests, and evidence | missing_claim_link |
| `feat:ddl-initialization-modes-001` | partial | Engine, DDL, schema, and datatype surfaces | missing_claim_link |
| `feat:default-canonical-engine-catalog-001` | partial | Engine, DDL, schema, and datatype surfaces | missing_target_claim_tier |
| `feat:defaultsession-concrete-session-class-001` | partial | Engine, DDL, schema, and datatype surfaces | missing_claim_link |
| `feat:depends-concrete-dependency-helper-001` | partial | Operator, middleware, security, and request helper surfaces | missing_claim_link |
| `feat:docs-mount-runtime-surface-parity-001` | partial | Documentation, schema, UIX, and mount surfaces | missing_claim_link |
| `feat:engine-extension-surface-001` | partial | Engine, DDL, schema, and datatype surfaces | missing_target_claim_tier |
| `feat:gate-c-conformance-security-checkpoint-001` | partial | Operator, middleware, security, and request helper surfaces | missing_spec_link |
| `feat:get-schema-python-helper-surface-001` | partial | Python/Rust runtime lanes and performance | missing_claim_link, missing_target_claim_tier |
| `feat:include-tables-helper-surface-001` | partial | Public API, helpers, facades, compatibility, and aliases | missing_claim_link, missing_target_claim_tier |
| `feat:integration-test-registry-coverage-001` | partial | Governance, conformance, profiles, tests, and evidence | missing_claim_link |
| `feat:kernelz-mount-surface-001` | partial | Kernel, plan, cache, and dispatch ownership | missing_claim_link, missing_target_claim_tier |
| `feat:kernelz-uix-surface-001` | absent | Kernel, plan, cache, and dispatch ownership | missing_claim_link, missing_target_claim_tier |
| `feat:methodz-mount-surface-001` | partial | Documentation, schema, UIX, and mount surfaces | missing_claim_link, missing_target_claim_tier |
| `feat:methodz-payload-surface-001` | partial | Documentation, schema, UIX, and mount surfaces | missing_claim_link, missing_target_claim_tier |
| `feat:middleware-extension-surface-001` | partial | Engine, DDL, schema, and datatype surfaces | missing_claim_link |
| `feat:middleware-surface-auth-separation-001` | partial | Engine, DDL, schema, and datatype surfaces | missing_claim_link |
| `feat:middleware-surface-builtin-catalog-001` | partial | Engine, DDL, schema, and datatype surfaces | missing_claim_link |
| `feat:middleware-surface-protocol-composition-001` | partial | Protocol dispatch, framing, phases, and runtime taxonomy | missing_claim_link |
| `feat:middleware-surface-public-projection-001` | partial | Engine, DDL, schema, and datatype surfaces | missing_claim_link |
| `feat:middlewarespec-protocol-001` | partial | Protocol dispatch, framing, phases, and runtime taxonomy | missing_claim_link, missing_target_claim_tier |
| `feat:monotone-spec-merge-precedence-001` | partial | Public API, helpers, facades, compatibility, and aliases | missing_target_claim_tier |
| `feat:mount-static-helper-surface-001` | partial | Documentation, schema, UIX, and mount surfaces | missing_claim_link |
| `feat:operator-bounded-middleware-catalog-001` | partial | Engine, DDL, schema, and datatype surfaces | missing_spec_link |
| `feat:operator-cookie-roundtrip-surface-001` | partial | Operator, middleware, security, and request helper surfaces | missing_spec_link |
| `feat:operator-static-files-surface-001` | partial | Documentation, schema, UIX, and mount surfaces | missing_spec_link |
| `feat:protocol-runtime-boundary-certification-001` | absent | Protocol dispatch, framing, phases, and runtime taxonomy | missing_required_test_plan, missing_claim_link |
| `feat:protocol-runtime-profile-pack-001` | absent | Protocol dispatch, framing, phases, and runtime taxonomy | missing_required_test_plan, missing_claim_link |
| `feat:protocol-runtime-ssot-feature-granularity-001` | absent | Protocol dispatch, framing, phases, and runtime taxonomy | missing_required_test_plan, missing_claim_link |
| `feat:protocol-runtime-test-evidence-suite-001` | absent | Protocol dispatch, framing, phases, and runtime taxonomy | missing_required_test_plan, missing_claim_link |
| `feat:rebind-helper-surface-001` | partial | Public API, helpers, facades, compatibility, and aliases | missing_claim_link, missing_target_claim_tier |
| `feat:rust-protocol-plan-parity-001` | absent | Python/Rust runtime lanes and performance | missing_required_test_plan, missing_claim_link |
| `feat:schema-migration-runtime-surface-001` | absent | Engine, DDL, schema, and datatype surfaces | missing_target_claim_tier |
| `feat:security-concrete-dependency-helper-001` | partial | Operator, middleware, security, and request helper surfaces | missing_claim_link |
| `feat:sqlite-attach-runtime-surface-001` | partial | Engine, DDL, schema, and datatype surfaces | missing_target_claim_tier |
| `feat:static-files-surface-001` | partial | Documentation, schema, UIX, and mount surfaces | missing_claim_link |
| `feat:tigrbl-test-suite-coverage-intake-001` | partial | Governance, conformance, profiles, tests, and evidence | missing_spec_link, missing_target_claim_tier |
| `feat:tigrblapp-concrete-facade-class-001` | partial | Public API, helpers, facades, compatibility, and aliases | missing_claim_link |
| `feat:tigrblrouter-concrete-facade-class-001` | partial | REST, JSON-RPC, Uvicorn, routing, and error parity | missing_claim_link |
| `feat:well-known-concrete-constants-surface-001` | partial | Public API, helpers, facades, compatibility, and aliases | missing_claim_link |
| `feat:well-known-decorator-surface-001` | partial | Public API, helpers, facades, compatibility, and aliases | missing_claim_link |
| `feat:well-known-imperative-surface-001` | partial | Public API, helpers, facades, compatibility, and aliases | missing_claim_link |
| `feat:wrap-sessionmaker-helper-surface-001` | partial | Engine, DDL, schema, and datatype surfaces | missing_claim_link |

## Full Target Feature List

| Feature | Status | Concern | Tier | Specs | Tests | Claims |
|---|---|---|---|---:|---:|---:|
| `feat:analytical-family-membership-freeze-001` | partial | Canonical operation families and exports | T2 | 3 | 39 | 2 |
| `feat:analytical-runtime-docs-export-parity-001` | partial | Documentation, schema, UIX, and mount surfaces | T2 | 3 | 39 | 2 |
| `feat:anon-access-projection-001` | partial | Operator, middleware, security, and request helper surfaces | T2 | 3 | 6 | 1 |
| `feat:apikey-security-dependency-001` | partial | Operator, middleware, security, and request helper surfaces | T2 | 2 | 6 | 0 |
| `feat:app-framed-message-codec-runtime-001` | absent | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 4 | 1 | 2 |
| `feat:asgi-router-compatibility-001` | partial | REST, JSON-RPC, Uvicorn, routing, and error parity | T2 | 1 | 1 | 1 |
| `feat:asyncapi-mount-surface-001` | partial | Documentation, schema, UIX, and mount surfaces | T2 | 1 | 14 | 1 |
| `feat:asyncapi-payload-surface-001` | partial | Documentation, schema, UIX, and mount surfaces | T2 | 1 | 14 | 1 |
| `feat:asyncapi-uix-surface-001` | absent | Documentation, schema, UIX, and mount surfaces | T2 | 2 | 14 | 1 |
| `feat:attrdict-contract-001` | partial | Public API, helpers, facades, compatibility, and aliases |  | 1 | 1 | 0 |
| `feat:backgroundtask-concrete-class-001` | partial | Operator, middleware, security, and request helper surfaces | T2 | 1 | 20 | 0 |
| `feat:bind-helper-surface-001` | partial | Public API, helpers, facades, compatibility, and aliases |  | 1 | 1 | 0 |
| `feat:binding-driven-ingress-001` | partial | REST, JSON-RPC, Uvicorn, routing, and error parity | T2 | 3 | 41 | 3 |
| `feat:binding-subevent-phase-atom-legality-matrix-001` | absent | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 3 | 1 | 2 |
| `feat:bootstrap-dbschema-runtime-surface-001` | partial | Engine, DDL, schema, and datatype surfaces | T2 | 3 | 33 | 1 |
| `feat:bootstrappable-table-mixin-001` | partial | Public API, helpers, facades, compatibility, and aliases | T2 | 3 | 77 | 2 |
| `feat:build-asyncapi-spec-helper-surface-001` | partial | Documentation, schema, UIX, and mount surfaces | T2 | 1 | 14 | 1 |
| `feat:build-handlers-helper-surface-001` | partial | Public API, helpers, facades, compatibility, and aliases | T2 | 2 | 38 | 1 |
| `feat:c-bulk-hot-path-prioritization-atoms-001` | partial | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 1 | 1 | 1 |
| `feat:c-bulk-hot-path-prioritization-default-ops-001` | partial | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 1 | 1 | 1 |
| `feat:c-bulk-hot-path-prioritization-kernel-001` | partial | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 3 | 1 | 1 |
| `feat:c-bulk-hot-path-prioritization-runtime-001` | partial | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 4 | 1 | 1 |
| `feat:canonical-analytical-ops-001` | partial | Operator, middleware, security, and request helper surfaces | T2 | 3 | 39 | 2 |
| `feat:canonical-realtime-transfer-ops-001` | partial | Operator, middleware, security, and request helper surfaces | T2 | 3 | 39 | 2 |
| `feat:cli-module-target-resolution-001` | partial | Governance, conformance, profiles, tests, and evidence | T2 | 1 | 4 | 0 |
| `feat:cli-path-target-resolution-001` | partial | Governance, conformance, profiles, tests, and evidence | T2 | 1 | 4 | 0 |
| `feat:cli-shared-target-loader-001` | partial | Governance, conformance, profiles, tests, and evidence | T2 | 1 | 4 | 0 |
| `feat:cli-target-error-classification-001` | partial | REST, JSON-RPC, Uvicorn, routing, and error parity | T2 | 2 | 5 | 1 |
| `feat:cli-target-resolution-001` | partial | Governance, conformance, profiles, tests, and evidence | T2 | 2 | 5 | 1 |
| `feat:cli-target-surface-loading-001` | partial | Governance, conformance, profiles, tests, and evidence | T2 | 1 | 4 | 0 |
| `feat:completion-fence-emit-complete-001` | absent | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 2 | 2 | 3 |
| `feat:concrete-engine-lowering-to-inventory-001` | absent | Engine, DDL, schema, and datatype surfaces | T1 | 1 | 1 | 1 |
| `feat:core-access-compatibility-001` | partial | Public API, helpers, facades, compatibility, and aliases | T2 | 1 | 1 | 1 |
| `feat:ddl-initialization-modes-001` | partial | Engine, DDL, schema, and datatype surfaces | T2 | 1 | 32 | 0 |
| `feat:ddl-runtime-surface-001` | partial | Engine, DDL, schema, and datatype surfaces | T2 | 4 | 33 | 1 |
| `feat:default-canonical-engine-catalog-001` | partial | Engine, DDL, schema, and datatype surfaces |  | 3 | 2 | 1 |
| `feat:default-kernel-identity-001` | partial | Kernel, plan, cache, and dispatch ownership | T2 | 2 | 15 | 1 |
| `feat:defaultsession-concrete-session-class-001` | partial | Engine, DDL, schema, and datatype surfaces | T2 | 4 | 32 | 0 |
| `feat:depends-concrete-dependency-helper-001` | partial | Operator, middleware, security, and request helper surfaces | T2 | 2 | 1 | 0 |
| `feat:derived-runtime-subevent-taxonomy-001` | absent | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 3 | 1 | 1 |
| `feat:dispatch-exchange-family-subevent-atoms-001` | absent | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 3 | 1 | 2 |
| `feat:docs-mount-runtime-surface-parity-001` | partial | Documentation, schema, UIX, and mount surfaces | T2 | 5 | 8 | 0 |
| `feat:engine-extension-surface-001` | partial | Engine, DDL, schema, and datatype surfaces |  | 2 | 2 | 1 |
| `feat:engine-resolver-multi-table-rpc-001` | partial | Engine, DDL, schema, and datatype surfaces | T2 | 5 | 48 | 1 |
| `feat:engine-resolver-precedence-001` | partial | Engine, DDL, schema, and datatype surfaces | T2 | 3 | 15 | 1 |
| `feat:engine-session-runtime-surface-001` | partial | Engine, DDL, schema, and datatype surfaces | T2 | 4 | 33 | 1 |
| `feat:engine-surface-plugin-resolution-001` | partial | Engine, DDL, schema, and datatype surfaces | T2 | 3 | 33 | 1 |
| `feat:ensure-primed-idempotence-001` | partial | Kernel, plan, cache, and dispatch ownership | T2 | 2 | 15 | 1 |
| `feat:ensure-schemas-runtime-surface-001` | partial | Engine, DDL, schema, and datatype surfaces | T2 | 2 | 33 | 1 |
| `feat:error-envelope-structure-parity-001` | partial | REST, JSON-RPC, Uvicorn, routing, and error parity | T2 | 2 | 6 | 1 |
| `feat:error-parity-response-structure-001` | partial | REST, JSON-RPC, Uvicorn, routing, and error parity | T2 | 3 | 7 | 2 |
| `feat:executor-dispatch-removal-001` | partial | Kernel, plan, cache, and dispatch ownership | T2 | 4 | 9 | 3 |
| `feat:extended-hook-selector-matching-001` | absent | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 4 | 1 | 2 |
| `feat:framing-decode-encode-atoms-001` | absent | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 6 | 1 | 2 |
| `feat:gate-c-conformance-security-checkpoint-001` | partial | Operator, middleware, security, and request helper surfaces | T2 | 0 | 17 | 2 |
| `feat:get-schema-python-helper-surface-001` | partial | Python/Rust runtime lanes and performance |  | 1 | 1 | 0 |
| `feat:harness-runtime-routing-parity-001` | partial | REST, JSON-RPC, Uvicorn, routing, and error parity | T2 | 2 | 15 | 1 |
| `feat:include-tables-helper-surface-001` | partial | Public API, helpers, facades, compatibility, and aliases |  | 2 | 1 | 0 |
| `feat:integration-test-registry-coverage-001` | partial | Governance, conformance, profiles, tests, and evidence | T1 | 2 | 5 | 0 |
| `feat:json-schema-mount-surface-001` | partial | Documentation, schema, UIX, and mount surfaces | T2 | 1 | 14 | 1 |
| `feat:json-schema-payload-surface-001` | partial | Documentation, schema, UIX, and mount surfaces | T2 | 1 | 14 | 1 |
| `feat:json-schema-uix-surface-001` | absent | Documentation, schema, UIX, and mount surfaces | T2 | 2 | 14 | 1 |
| `feat:jsonrpc-20-runtime-surface-001` | partial | REST, JSON-RPC, Uvicorn, routing, and error parity | T2 | 1 | 14 | 4 |
| `feat:jsonrpc-batch-framing-001` | partial | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 3 | 8 | 2 |
| `feat:jsonrpc-endpoint-key-001` | partial | REST, JSON-RPC, Uvicorn, routing, and error parity | T2 | 3 | 40 | 3 |
| `feat:jsonrpc-notification-204-projection-001` | partial | REST, JSON-RPC, Uvicorn, routing, and error parity | T2 | 2 | 15 | 1 |
| `feat:kernel-bootstrap-plan-parity-001` | partial | Kernel, plan, cache, and dispatch ownership | T2 | 3 | 15 | 1 |
| `feat:kernel-cache-invalidation-contract-001` | partial | Kernel, plan, cache, and dispatch ownership | T2 | 2 | 15 | 1 |
| `feat:kernel-prime-opview-cache-001` | partial | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 2 | 15 | 1 |
| `feat:kernel-priming-runtime-parity-001` | partial | Kernel, plan, cache, and dispatch ownership | T2 | 2 | 15 | 1 |
| `feat:kernelplan-dispatch-ownership-001` | partial | Kernel, plan, cache, and dispatch ownership | T2 | 4 | 9 | 3 |
| `feat:kernelz-bounded-payload-001` | partial | Kernel, plan, cache, and dispatch ownership | T2 | 2 | 2 | 1 |
| `feat:kernelz-mount-surface-001` | partial | Kernel, plan, cache, and dispatch ownership |  | 2 | 1 | 0 |
| `feat:kernelz-uix-surface-001` | absent | Kernel, plan, cache, and dispatch ownership |  | 2 | 1 | 0 |
| `feat:key-digest-uvicorn-stability-001` | partial | REST, JSON-RPC, Uvicorn, routing, and error parity | T2 | 1 | 1 | 1 |
| `feat:lazy-compat-dict-publication-fallback-only-001` | partial | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 1 | 1 | 1 |
| `feat:mapping-dispatch-convergence-001` | partial | Kernel, plan, cache, and dispatch ownership | T2 | 3 | 2 | 1 |
| `feat:message-datagram-runtime-families-001` | absent | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 4 | 1 | 2 |
| `feat:methodz-mount-surface-001` | partial | Documentation, schema, UIX, and mount surfaces |  | 1 | 1 | 0 |
| `feat:methodz-payload-surface-001` | partial | Documentation, schema, UIX, and mount surfaces |  | 1 | 1 | 0 |
| `feat:middleware-extension-surface-001` | partial | Engine, DDL, schema, and datatype surfaces | T2 | 1 | 1 | 0 |
| `feat:middleware-surface-auth-separation-001` | partial | Engine, DDL, schema, and datatype surfaces | T2 | 1 | 1 | 0 |
| `feat:middleware-surface-builtin-catalog-001` | partial | Engine, DDL, schema, and datatype surfaces | T2 | 1 | 1 | 0 |
| `feat:middleware-surface-protocol-composition-001` | partial | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 1 | 1 | 0 |
| `feat:middleware-surface-public-projection-001` | partial | Engine, DDL, schema, and datatype surfaces | T2 | 1 | 1 | 0 |
| `feat:middlewarespec-protocol-001` | partial | Protocol dispatch, framing, phases, and runtime taxonomy |  | 1 | 1 | 0 |
| `feat:monotone-spec-merge-precedence-001` | partial | Public API, helpers, facades, compatibility, and aliases |  | 1 | 3 | 1 |
| `feat:mount-lens-helper-surface-001` | partial | Documentation, schema, UIX, and mount surfaces | T2 | 1 | 14 | 1 |
| `feat:mount-static-helper-surface-001` | partial | Documentation, schema, UIX, and mount surfaces | T2 | 1 | 2 | 0 |
| `feat:mount-swagger-helper-surface-001` | partial | Documentation, schema, UIX, and mount surfaces | T2 | 1 | 14 | 1 |
| `feat:mounted-prefix-routing-parity-001` | partial | REST, JSON-RPC, Uvicorn, routing, and error parity | T2 | 2 | 15 | 1 |
| `feat:multi-engine-interop-runtime-surface-001` | partial | Engine, DDL, schema, and datatype surfaces | T2 | 2 | 33 | 1 |
| `feat:multi-table-routing-parity-001` | partial | REST, JSON-RPC, Uvicorn, routing, and error parity | T2 | 2 | 15 | 1 |
| `feat:multipart-form-preservation-001` | partial | REST, JSON-RPC, Uvicorn, routing, and error parity | T2 | 2 | 3 | 2 |
| `feat:no-check-attr-hot-runner-preference-001` | partial | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 1 | 1 | 1 |
| `feat:operation-security-emission-from-secdeps-001` | partial | Operator, middleware, security, and request helper surfaces | T2 | 1 | 14 | 3 |
| `feat:operator-bounded-middleware-catalog-001` | partial | Engine, DDL, schema, and datatype surfaces | T2 | 0 | 3 | 2 |
| `feat:operator-cookie-roundtrip-surface-001` | partial | Operator, middleware, security, and request helper surfaces | T2 | 0 | 3 | 2 |
| `feat:operator-static-files-surface-001` | partial | Documentation, schema, UIX, and mount surfaces | T2 | 0 | 3 | 2 |
| `feat:operator-surface-framing-semantics-001` | partial | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 2 | 2 | 1 |
| `feat:operator-surface-smoke-runtime-parity-001` | partial | Operator, middleware, security, and request helper surfaces | T2 | 2 | 3 | 1 |
| `feat:opview-on-demand-cache-reuse-001` | partial | Kernel, plan, cache, and dispatch ownership | T2 | 2 | 15 | 1 |
| `feat:owner-dispatch-loop-modes-001` | absent | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 2 | 2 | 3 |
| `feat:phase-tree-error-branches-001` | absent | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 3 | 1 | 1 |
| `feat:post-emit-completion-fence-compilation-001` | absent | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 4 | 1 | 2 |
| `feat:pre-tx-dependency-execution-001` | partial | Operator, middleware, security, and request helper surfaces | T2 | 3 | 5 | 2 |
| `feat:protocol-anchor-ordering-parity-001` | absent | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 4 | 1 | 2 |
| `feat:protocol-fused-segments-001` | absent | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 5 | 1 | 2 |
| `feat:protocol-runtime-boundary-certification-001` | absent | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 4 | 0 | 0 |
| `feat:protocol-runtime-profile-pack-001` | absent | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 4 | 0 | 0 |
| `feat:protocol-runtime-ssot-feature-granularity-001` | absent | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 4 | 0 | 0 |
| `feat:protocol-runtime-test-evidence-suite-001` | absent | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 4 | 0 | 0 |
| `feat:protocol-scope-schemas-001` | absent | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 2 | 1 | 2 |
| `feat:python-asgi-boundary-evidence-001` | absent | Python/Rust runtime lanes and performance | T2 | 3 | 2 | 2 |
| `feat:python-direct-runtime-microbench-001` | absent | Python/Rust runtime lanes and performance | T2 | 2 | 2 | 2 |
| `feat:python-engine-session-lifecycle-001` | absent | Python/Rust runtime lanes and performance | T2 | 2 | 2 | 2 |
| `feat:python-request-envelope-contract-001` | absent | Python/Rust runtime lanes and performance | T2 | 2 | 2 | 2 |
| `feat:python-request-hot-path-no-ddl-001` | absent | Python/Rust runtime lanes and performance | T2 | 3 | 2 | 2 |
| `feat:python-runtime-2x-target-comparison-001` | absent | Python/Rust runtime lanes and performance | T2 | 2 | 2 | 2 |
| `feat:python-runtime-callgraph-export-001` | absent | Python/Rust runtime lanes and performance | T2 | 2 | 2 | 2 |
| `feat:python-runtime-ddl-initialization-boundary-001` | absent | Python/Rust runtime lanes and performance | T2 | 2 | 2 | 2 |
| `feat:python-runtime-performance-baseline-001` | absent | Python/Rust runtime lanes and performance | T2 | 2 | 2 | 2 |
| `feat:python-schema-readiness-fail-closed-001` | absent | Python/Rust runtime lanes and performance | T2 | 2 | 2 | 2 |
| `feat:python-transaction-hot-path-001` | absent | Python/Rust runtime lanes and performance | T2 | 3 | 2 | 2 |
| `feat:realtime-transfer-family-membership-freeze-001` | partial | Canonical operation families and exports | T2 | 3 | 39 | 2 |
| `feat:realtime-transfer-runtime-docs-export-parity-001` | partial | Documentation, schema, UIX, and mount surfaces | T2 | 3 | 39 | 2 |
| `feat:rebind-helper-surface-001` | partial | Public API, helpers, facades, compatibility, and aliases |  | 1 | 1 | 0 |
| `feat:rest-create-success-status-001` | partial | REST, JSON-RPC, Uvicorn, routing, and error parity | T2 | 2 | 6 | 1 |
| `feat:rest-operation-id-uniqueness-001` | partial | REST, JSON-RPC, Uvicorn, routing, and error parity | T2 | 1 | 1 | 1 |
| `feat:rest-rpc-symmetry-header-parity-001` | partial | REST, JSON-RPC, Uvicorn, routing, and error parity | T2 | 1 | 1 | 1 |
| `feat:runtime-owned-hook-legality-enforcement-001` | absent | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 4 | 1 | 2 |
| `feat:rust-asgi-boundary-evidence-001` | absent | Python/Rust runtime lanes and performance | T2 | 3 | 2 | 2 |
| `feat:rust-direct-runtime-microbench-001` | absent | Python/Rust runtime lanes and performance | T2 | 2 | 2 | 2 |
| `feat:rust-engine-session-lifecycle-001` | absent | Python/Rust runtime lanes and performance | T2 | 2 | 2 | 2 |
| `feat:rust-protocol-plan-parity-001` | absent | Python/Rust runtime lanes and performance | T2 | 4 | 0 | 0 |
| `feat:rust-request-envelope-contract-001` | absent | Python/Rust runtime lanes and performance | T2 | 2 | 2 | 2 |
| `feat:rust-request-hot-path-no-ddl-001` | absent | Python/Rust runtime lanes and performance | T2 | 3 | 2 | 2 |
| `feat:rust-runtime-2x-python-target-001` | absent | Python/Rust runtime lanes and performance | T2 | 2 | 2 | 2 |
| `feat:rust-runtime-callgraph-export-001` | absent | Python/Rust runtime lanes and performance | T2 | 2 | 2 | 2 |
| `feat:rust-runtime-ddl-initialization-boundary-001` | absent | Python/Rust runtime lanes and performance | T2 | 2 | 2 | 2 |
| `feat:rust-runtime-performance-baseline-001` | absent | Python/Rust runtime lanes and performance | T2 | 2 | 2 | 2 |
| `feat:rust-schema-readiness-fail-closed-001` | absent | Python/Rust runtime lanes and performance | T2 | 2 | 2 | 2 |
| `feat:rust-transaction-hot-path-001` | absent | Python/Rust runtime lanes and performance | T2 | 3 | 2 | 2 |
| `feat:schema-migration-runtime-surface-001` | absent | Engine, DDL, schema, and datatype surfaces |  | 2 | 2 | 1 |
| `feat:security-concrete-dependency-helper-001` | partial | Operator, middleware, security, and request helper surfaces | T2 | 2 | 6 | 0 |
| `feat:security-per-route-include-router-compat-001` | partial | REST, JSON-RPC, Uvicorn, routing, and error parity | T2 | 1 | 1 | 1 |
| `feat:segment-fusion-barrier-policy-001` | absent | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 2 | 2 | 3 |
| `feat:sqlite-attach-runtime-surface-001` | partial | Engine, DDL, schema, and datatype surfaces |  | 2 | 2 | 1 |
| `feat:static-files-surface-001` | partial | Documentation, schema, UIX, and mount surfaces | T2 | 1 | 3 | 0 |
| `feat:stdapi-openapi-docs-parity-001` | partial | Documentation, schema, UIX, and mount surfaces | T2 | 1 | 1 | 1 |
| `feat:stdapi-routing-parity-001` | partial | REST, JSON-RPC, Uvicorn, routing, and error parity | T2 | 1 | 1 | 1 |
| `feat:swagger-openapi-uix-001` | partial | Documentation, schema, UIX, and mount surfaces | T2 | 1 | 15 | 1 |
| `feat:tiered-soa-byte-layout-hot-metadata-001` | absent | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 1 | 1 | 1 |
| `feat:tigrbl-lens-openrpc-uix-001` | partial | REST, JSON-RPC, Uvicorn, routing, and error parity | T2 | 1 | 15 | 1 |
| `feat:tigrbl-test-suite-coverage-intake-001` | partial | Governance, conformance, profiles, tests, and evidence |  | 0 | 252 | 2 |
| `feat:tigrblapp-concrete-facade-class-001` | partial | Public API, helpers, facades, compatibility, and aliases | T2 | 2 | 14 | 0 |
| `feat:tigrblrouter-concrete-facade-class-001` | partial | REST, JSON-RPC, Uvicorn, routing, and error parity | T2 | 2 | 14 | 0 |
| `feat:tx-phase-legacy-alias-removal-001` | absent | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 3 | 1 | 2 |
| `feat:uniform-diagnostics-uix-surface-001` | absent | Documentation, schema, UIX, and mount surfaces | T2 | 2 | 14 | 1 |
| `feat:uploaded-file-runtime-contract-001` | partial | REST, JSON-RPC, Uvicorn, routing, and error parity | T2 | 2 | 3 | 2 |
| `feat:uvicorn-protocol-mode-runtime-parity-001` | partial | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 3 | 16 | 1 |
| `feat:uvicorn-rest-rpc-semantic-parity-001` | partial | REST, JSON-RPC, Uvicorn, routing, and error parity | T2 | 2 | 15 | 1 |
| `feat:validation-failure-projection-parity-001` | partial | REST, JSON-RPC, Uvicorn, routing, and error parity | T2 | 2 | 6 | 1 |
| `feat:well-known-concrete-constants-surface-001` | partial | Public API, helpers, facades, compatibility, and aliases | T2 | 3 | 3 | 0 |
| `feat:well-known-decorator-surface-001` | partial | Public API, helpers, facades, compatibility, and aliases | T2 | 4 | 5 | 0 |
| `feat:well-known-imperative-surface-001` | partial | Public API, helpers, facades, compatibility, and aliases | T2 | 4 | 3 | 0 |
| `feat:wrap-sessionmaker-helper-surface-001` | partial | Engine, DDL, schema, and datatype surfaces | T2 | 4 | 32 | 0 |
