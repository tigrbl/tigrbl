# Full-Feature Certification Target

Generated: 2026-05-23

This is a derived planning view over `.ssot/registry.json`. The registry remains authoritative.

- Boundary: `bnd:tigrbl-full-feature-certification-001`
- Boundary status: `draft`
- Active in-scope gaps: `78`
- Absent: `5`
- Partial: `73`
- Ready for freeze: `78`
- Blocked from freeze: `0`

Rows are excluded when they are deprecated, obsolete, removed, descoped, or explicitly out of bounds.

## Concern Summary

| Concern | Absent | Partial | Total |
|---|---:|---:|---:|
| Documentation, schema, UIX, and mount surfaces | 2 | 14 | 16 |
| Engine, DDL, schema, and datatype surfaces | 1 | 13 | 14 |
| Governance, conformance, profiles, tests, and evidence | 0 | 6 | 6 |
| Kernel, plan, cache, and dispatch ownership | 1 | 1 | 2 |
| Operator, middleware, security, and request helper surfaces | 0 | 11 | 11 |
| Protocol dispatch, framing, phases, and runtime taxonomy | 1 | 7 | 8 |
| Public API, helpers, facades, compatibility, and aliases | 0 | 11 | 11 |
| Python/Rust runtime lanes and performance | 0 | 1 | 1 |
| REST, JSON-RPC, Uvicorn, routing, and error parity | 0 | 9 | 9 |

## Freeze Blockers

The boundary must remain draft until every row has linked specs, required tests, claims, target claim tier, and executable evidence.

| Feature | Status | Concern | Blockers |
|---|---|---|---|

## Full Target Feature List

| Feature | Status | Concern | Tier | Specs | Tests | Claims |
|---|---|---|---|---:|---:|---:|
| `feat:analytical-runtime-docs-export-parity-001` | partial | Documentation, schema, UIX, and mount surfaces | T2 | 3 | 39 | 2 |
| `feat:anon-access-projection-001` | partial | Operator, middleware, security, and request helper surfaces | T2 | 3 | 6 | 1 |
| `feat:apikey-security-dependency-001` | partial | Operator, middleware, security, and request helper surfaces | T2 | 2 | 6 | 1 |
| `feat:asgi-router-compatibility-001` | partial | REST, JSON-RPC, Uvicorn, routing, and error parity | T2 | 1 | 1 | 1 |
| `feat:attrdict-contract-001` | partial | Public API, helpers, facades, compatibility, and aliases | T2 | 1 | 1 | 1 |
| `feat:backgroundtask-concrete-class-001` | partial | Operator, middleware, security, and request helper surfaces | T2 | 1 | 20 | 1 |
| `feat:bind-helper-surface-001` | partial | Public API, helpers, facades, compatibility, and aliases | T2 | 1 | 1 | 1 |
| `feat:build-handlers-helper-surface-001` | partial | Public API, helpers, facades, compatibility, and aliases | T2 | 2 | 38 | 1 |
| `feat:c-bulk-hot-path-prioritization-atoms-001` | partial | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 1 | 1 | 1 |
| `feat:c-bulk-hot-path-prioritization-default-ops-001` | partial | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 1 | 1 | 1 |
| `feat:c-bulk-hot-path-prioritization-kernel-001` | partial | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 3 | 1 | 1 |
| `feat:c-bulk-hot-path-prioritization-runtime-001` | partial | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 4 | 1 | 1 |
| `feat:canonical-analytical-ops-001` | partial | Operator, middleware, security, and request helper surfaces | T2 | 3 | 39 | 2 |
| `feat:canonical-realtime-transfer-ops-001` | partial | Operator, middleware, security, and request helper surfaces | T2 | 3 | 39 | 2 |
| `feat:cli-module-target-resolution-001` | partial | Governance, conformance, profiles, tests, and evidence | T2 | 1 | 4 | 1 |
| `feat:cli-path-target-resolution-001` | partial | Governance, conformance, profiles, tests, and evidence | T2 | 1 | 4 | 1 |
| `feat:cli-shared-target-loader-001` | partial | Governance, conformance, profiles, tests, and evidence | T2 | 1 | 4 | 1 |
| `feat:cli-target-surface-loading-001` | partial | Governance, conformance, profiles, tests, and evidence | T2 | 1 | 4 | 1 |
| `feat:core-access-compatibility-001` | partial | Public API, helpers, facades, compatibility, and aliases | T2 | 1 | 1 | 1 |
| `feat:ddl-initialization-modes-001` | partial | Engine, DDL, schema, and datatype surfaces | T2 | 1 | 32 | 1 |
| `feat:ddl-runtime-surface-001` | partial | Engine, DDL, schema, and datatype surfaces | T2 | 4 | 33 | 1 |
| `feat:default-canonical-engine-catalog-001` | partial | Engine, DDL, schema, and datatype surfaces | T2 | 3 | 2 | 1 |
| `feat:defaultsession-concrete-session-class-001` | partial | Engine, DDL, schema, and datatype surfaces | T2 | 4 | 32 | 1 |
| `feat:depends-concrete-dependency-helper-001` | partial | Operator, middleware, security, and request helper surfaces | T2 | 2 | 1 | 1 |
| `feat:docs-mount-runtime-surface-parity-001` | partial | Documentation, schema, UIX, and mount surfaces | T2 | 5 | 8 | 1 |
| `feat:engine-extension-surface-001` | partial | Engine, DDL, schema, and datatype surfaces | T2 | 2 | 2 | 1 |
| `feat:engine-resolver-multi-table-rpc-001` | partial | Engine, DDL, schema, and datatype surfaces | T2 | 5 | 48 | 1 |
| `feat:gate-c-conformance-security-checkpoint-001` | partial | Operator, middleware, security, and request helper surfaces | T2 | 3 | 17 | 2 |
| `feat:get-schema-python-helper-surface-001` | partial | Python/Rust runtime lanes and performance | T2 | 1 | 1 | 1 |
| `feat:include-tables-helper-surface-001` | partial | Public API, helpers, facades, compatibility, and aliases | T2 | 2 | 1 | 1 |
| `feat:integration-test-registry-coverage-001` | partial | Governance, conformance, profiles, tests, and evidence | T1 | 2 | 5 | 1 |
| `feat:json-schema-mount-surface-001` | partial | Documentation, schema, UIX, and mount surfaces | T2 | 1 | 14 | 1 |
| `feat:json-schema-payload-surface-001` | partial | Documentation, schema, UIX, and mount surfaces | T2 | 1 | 14 | 1 |
| `feat:json-schema-uix-surface-001` | absent | Documentation, schema, UIX, and mount surfaces | T2 | 2 | 14 | 1 |
| `feat:kernel-prime-opview-cache-001` | partial | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 2 | 15 | 1 |
| `feat:kernelz-mount-surface-001` | partial | Kernel, plan, cache, and dispatch ownership | T2 | 2 | 1 | 1 |
| `feat:kernelz-uix-surface-001` | absent | Kernel, plan, cache, and dispatch ownership | T2 | 2 | 1 | 1 |
| `feat:key-digest-uvicorn-stability-001` | partial | REST, JSON-RPC, Uvicorn, routing, and error parity | T2 | 1 | 1 | 1 |
| `feat:methodz-mount-surface-001` | partial | Documentation, schema, UIX, and mount surfaces | T2 | 1 | 1 | 1 |
| `feat:methodz-payload-surface-001` | partial | Documentation, schema, UIX, and mount surfaces | T2 | 1 | 1 | 1 |
| `feat:middleware-extension-surface-001` | partial | Engine, DDL, schema, and datatype surfaces | T2 | 1 | 1 | 1 |
| `feat:middleware-surface-auth-separation-001` | partial | Engine, DDL, schema, and datatype surfaces | T2 | 1 | 1 | 1 |
| `feat:middleware-surface-builtin-catalog-001` | partial | Engine, DDL, schema, and datatype surfaces | T2 | 1 | 1 | 1 |
| `feat:middleware-surface-protocol-composition-001` | partial | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 1 | 1 | 1 |
| `feat:middleware-surface-public-projection-001` | partial | Engine, DDL, schema, and datatype surfaces | T2 | 1 | 1 | 1 |
| `feat:middlewarespec-protocol-001` | partial | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 1 | 1 | 1 |
| `feat:monotone-spec-merge-precedence-001` | partial | Public API, helpers, facades, compatibility, and aliases | T2 | 1 | 3 | 1 |
| `feat:mount-lens-helper-surface-001` | partial | Documentation, schema, UIX, and mount surfaces | T2 | 1 | 14 | 1 |
| `feat:mount-static-helper-surface-001` | partial | Documentation, schema, UIX, and mount surfaces | T2 | 1 | 2 | 1 |
| `feat:mount-swagger-helper-surface-001` | partial | Documentation, schema, UIX, and mount surfaces | T2 | 1 | 14 | 1 |
| `feat:mounted-prefix-routing-parity-001` | partial | REST, JSON-RPC, Uvicorn, routing, and error parity | T2 | 2 | 15 | 1 |
| `feat:operation-security-emission-from-secdeps-001` | partial | Operator, middleware, security, and request helper surfaces | T2 | 1 | 14 | 3 |
| `feat:operator-bounded-middleware-catalog-001` | partial | Engine, DDL, schema, and datatype surfaces | T2 | 2 | 3 | 2 |
| `feat:operator-cookie-roundtrip-surface-001` | partial | Operator, middleware, security, and request helper surfaces | T2 | 2 | 3 | 2 |
| `feat:operator-static-files-surface-001` | partial | Documentation, schema, UIX, and mount surfaces | T2 | 2 | 3 | 2 |
| `feat:operator-surface-smoke-runtime-parity-001` | partial | Operator, middleware, security, and request helper surfaces | T2 | 2 | 3 | 1 |
| `feat:phase-tree-error-branches-001` | absent | Protocol dispatch, framing, phases, and runtime taxonomy | T2 | 3 | 1 | 1 |
| `feat:realtime-transfer-runtime-docs-export-parity-001` | partial | Documentation, schema, UIX, and mount surfaces | T2 | 3 | 39 | 2 |
| `feat:rebind-helper-surface-001` | partial | Public API, helpers, facades, compatibility, and aliases | T2 | 1 | 1 | 1 |
| `feat:rest-operation-id-uniqueness-001` | partial | REST, JSON-RPC, Uvicorn, routing, and error parity | T2 | 1 | 1 | 1 |
| `feat:rest-rpc-symmetry-header-parity-001` | partial | REST, JSON-RPC, Uvicorn, routing, and error parity | T2 | 1 | 1 | 1 |
| `feat:schema-migration-runtime-surface-001` | absent | Engine, DDL, schema, and datatype surfaces | T2 | 2 | 2 | 1 |
| `feat:security-concrete-dependency-helper-001` | partial | Operator, middleware, security, and request helper surfaces | T2 | 2 | 6 | 1 |
| `feat:security-per-route-include-router-compat-001` | partial | REST, JSON-RPC, Uvicorn, routing, and error parity | T2 | 1 | 1 | 1 |
| `feat:sqlite-attach-runtime-surface-001` | partial | Engine, DDL, schema, and datatype surfaces | T2 | 2 | 2 | 1 |
| `feat:static-files-surface-001` | partial | Documentation, schema, UIX, and mount surfaces | T2 | 1 | 3 | 1 |
| `feat:stdapi-openapi-docs-parity-001` | partial | Documentation, schema, UIX, and mount surfaces | T2 | 1 | 1 | 1 |
| `feat:stdapi-routing-parity-001` | partial | REST, JSON-RPC, Uvicorn, routing, and error parity | T2 | 1 | 1 | 1 |
| `feat:swagger-openapi-uix-001` | partial | Documentation, schema, UIX, and mount surfaces | T2 | 1 | 15 | 1 |
| `feat:tigrbl-lens-openrpc-uix-001` | partial | REST, JSON-RPC, Uvicorn, routing, and error parity | T2 | 1 | 15 | 1 |
| `feat:tigrbl-test-suite-coverage-intake-001` | partial | Governance, conformance, profiles, tests, and evidence | T2 | 2 | 252 | 2 |
| `feat:tigrblapp-concrete-facade-class-001` | partial | Public API, helpers, facades, compatibility, and aliases | T2 | 2 | 14 | 1 |
| `feat:tigrblrouter-concrete-facade-class-001` | partial | REST, JSON-RPC, Uvicorn, routing, and error parity | T2 | 2 | 14 | 1 |
| `feat:uniform-diagnostics-uix-surface-001` | absent | Documentation, schema, UIX, and mount surfaces | T2 | 2 | 14 | 1 |
| `feat:well-known-concrete-constants-surface-001` | partial | Public API, helpers, facades, compatibility, and aliases | T2 | 3 | 3 | 1 |
| `feat:well-known-decorator-surface-001` | partial | Public API, helpers, facades, compatibility, and aliases | T2 | 4 | 5 | 1 |
| `feat:well-known-imperative-surface-001` | partial | Public API, helpers, facades, compatibility, and aliases | T2 | 4 | 3 | 1 |
| `feat:wrap-sessionmaker-helper-surface-001` | partial | Engine, DDL, schema, and datatype surfaces | T2 | 4 | 32 | 1 |
