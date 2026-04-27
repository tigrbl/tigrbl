# Features With Fewer Than 5 Linked Test Cases

Source: `.ssot/registry.json`
Threshold: `len(feature.test_ids) < 5`
Total matching features: `313`

## Category Summary

| Concern | Features |
| --- | ---: |
| `appspec-corpus` | 2 |
| `auth-security` | 2 |
| `buildability-baseline-001` | 1 |
| `conformance` | 66 |
| `diagnostics` | 1 |
| `integration-coverage` | 1 |
| `jsonrpc` | 3 |
| `jsonrpc-validation-hardening` | 2 |
| `legacy-feature-id-alias` | 21 |
| `operator-surface` | 14 |
| `op-owner-scope` | 3 |
| `protocol-runtime-governance` | 10 |
| `runtime-kernel` | 45 |
| `runtime-root-surface` | 1 |
| `server-support` | 7 |
| `spec-composition` | 1 |
| `spec-linked-unslotted` | 2 |
| `ssot-governance` | 32 |
| `surface-inventory` | 98 |
| `transport-dispatch` | 1 |

## appspec-corpus (2)

| Feature | Tests | Impl | Title |
| --- | ---: | --- | --- |
| `feat:appspec-corpus-canonical-fixture-001` | 4 | `implemented` | AppSpec canonical corpus fixture |
| `feat:appspec-corpus-negative-fail-closed-001` | 4 | `implemented` | AppSpec negative corpus fail-closed lane |

## auth-security (2)

| Feature | Tests | Impl | Title |
| --- | ---: | --- | --- |
| `feat:operator-auth-dependency-hook-surface-001` | 3 | `partial` | Dependency and hook based auth operator surface |
| `feat:operator-oidc-discovery-docs-descoped-001` | 3 | `partial` | OIDC discovery and docs surface de-scoped from current cycle |

## buildability-baseline-001 (1)

| Feature | Tests | Impl | Title |
| --- | ---: | --- | --- |
| `feat:package-buildability-importability-001` | 1 | `partial` | Package buildability and importability baseline |

## conformance (66)

| Feature | Tests | Impl | Title |
| --- | ---: | --- | --- |
| `feat:diagnostics-absence-warning-suppression-001` | 1 | `partial` | Diagnostics absence-warning suppression |
| `feat:diagnostics-contract-001` | 1 | `partial` | Diagnostics endpoint contracts |
| `feat:diagnostics-system-prefix-mount-001` | 1 | `partial` | Diagnostics system-prefix mount |
| `feat:gate-d-reproducibility-conditions-validation` | 1 | `implemented` | Gate D reproducibility conditions validation |
| `feat:gate-d-reproducibility-validator-workflow` | 1 | `implemented` | Gate D reproducibility validator workflow |
| `feat:healthz-stable-payload-001` | 1 | `partial` | Healthz stable payload |
| `feat:post-promotion-handoff-validator-workflow` | 1 | `implemented` | Post-promotion handoff validator workflow |
| `feat:rfc-8785-jcs-rejection-semantics-001` | 1 | `absent` | RFC 8785 JCS rejection semantics |
| `feat:surface-binding-proto-emission-001` | 1 | `partial` | Declared-surface binding proto emission |
| `feat:surface-optional-metadata-emission-001` | 1 | `partial` | Declared-surface optional metadata emission |
| `feat:clean-room-package-smoke-lane` | 2 | `implemented` | Clean-room package smoke lane |
| `feat:dev-bundle-evidence-structure` | 2 | `implemented` | Dev-bundle evidence structure |
| `feat:diagnostics-warning-vocabulary-001` | 2 | `partial` | Diagnostics warning vocabulary |
| `feat:evidence-lane-ci-workflow` | 2 | `implemented` | Evidence-lane CI workflow |
| `feat:evidence-registry-bundle-validator-checkpoint` | 2 | `implemented` | Evidence registry and bundle validator checkpoint |
| `feat:evidence-registry-claim-test-artifact-map` | 2 | `implemented` | Evidence registry claim/test/artifact map |
| `feat:factories-001` | 2 | `implemented` | Canonical factories and shortcut re-exports |
| `feat:gate-b-surface-closure-validator-workflow` | 2 | `implemented` | Gate B surface-closure validator workflow |
| `feat:gate-c-conformance-security-validator-workflow` | 2 | `implemented` | Gate C conformance/security validator workflow |
| `feat:gate-e-promotion-validator-workflow` | 2 | `implemented` | Gate E promotion validator workflow |
| `feat:kernelz-bounded-payload-001` | 2 | `partial` | Kernelz bounded payload |
| `feat:next-dev-line-governed-opening` | 2 | `implemented` | Next dev line governed opening |
| `feat:next-target-datatype-table-isolation` | 2 | `implemented` | Next-target datatype/table isolation |
| `feat:oidc-core-discovery-descope` | 2 | `implemented` | OIDC Core/discovery de-scope |
| `feat:post-promotion-release-history-freeze` | 2 | `implemented` | Post-promotion release history freeze |
| `feat:rfc-6749` | 2 | `implemented` | RFC-6749 feature |
| `feat:rfc-7519` | 2 | `implemented` | RFC-7519 feature |
| `feat:rfc-7636` | 2 | `implemented` | RFC-7636 feature |
| `feat:rfc-8414` | 2 | `implemented` | RFC-8414 feature |
| `feat:rfc-8705` | 2 | `implemented` | RFC-8705 feature |
| `feat:rfc-8785-jcs-canonicalizer-001` | 2 | `absent` | RFC 8785 JCS canonicalizer |
| `feat:rfc-8785-jcs-conformance-vectors-001` | 2 | `absent` | RFC 8785 JCS conformance vectors |
| `feat:rfc-9110` | 2 | `implemented` | RFC-9110 feature |
| `feat:rfc-9449` | 2 | `implemented` | RFC-9449 feature |
| `feat:stable-release-evidence-structure` | 2 | `implemented` | Stable-release evidence structure |
| `feat:surface-binding-family-emission-001` | 2 | `partial` | Declared-surface binding family emission |
| `feat:surface-metadata-omission-contract-001` | 2 | `partial` | Declared-surface metadata omission contract |
| `feat:apache-2-license-root` | 3 | `implemented` | Root Apache 2.0 license |
| `feat:boundary-freeze-diff-enforcement` | 3 | `implemented` | Boundary-freeze diff enforcement |
| `feat:boundary-freeze-manifest-validation` | 3 | `implemented` | Boundary-freeze manifest validation |
| `feat:checkpoint-path-name-conformance` | 3 | `implemented` | Checkpoint path/name conformance |
| `feat:claim-language-lint` | 3 | `implemented` | Claim-language lint |
| `feat:code-of-conduct` | 3 | `implemented` | Code of conduct |
| `feat:contributor-policy` | 3 | `implemented` | Contributor policy |
| `feat:doc-pointer-validation` | 3 | `implemented` | Doc-pointer validation |
| `feat:gate-a-boundary-freeze-manifest` | 3 | `implemented` | Gate A boundary-freeze manifest |
| `feat:gate-a-checkpoint-validation-suite` | 3 | `implemented` | Gate A checkpoint validation suite |
| `feat:gate-a-current-cycle-boundary-freeze-marker` | 3 | `implemented` | Gate A current-cycle boundary-freeze marker |
| `feat:gate-b-surface-closure-validation` | 3 | `implemented` | Gate B surface-closure validation |
| `feat:gate-e-release-promotion-synchronization` | 3 | `implemented` | Gate E release promotion synchronization |
| `feat:governed-docs-projection-tree` | 3 | `implemented` | Governed docs projection tree |
| `feat:package-layout-validation` | 3 | `implemented` | Package layout validation |
| `feat:path-length-policy` | 3 | `implemented` | Path-length policy |
| `feat:path-length-validation` | 3 | `implemented` | Path-length validation |
| `feat:policy-governance-ci-workflow` | 3 | `implemented` | Policy governance CI workflow |
| `feat:release-note-claim-lint` | 3 | `implemented` | Release-note claim lint |
| `feat:root-clutter-generated-artifact-validation` | 3 | `implemented` | Root-clutter and generated-artifact validation |
| `feat:security-policy` | 3 | `implemented` | Security policy |
| `feat:stable-release-current-boundary-tier3-certification` | 3 | `implemented` | Stable release current-boundary Tier 3 certification |
| `feat:stable-release-rfc-security-tier3-certification` | 3 | `implemented` | Stable release RFC/spec/security Tier 3 certification |
| `feat:cli-module-target-resolution-001` | 4 | `partial` | CLI module target resolution |
| `feat:cli-path-target-resolution-001` | 4 | `partial` | CLI path target resolution |
| `feat:cli-shared-target-loader-001` | 4 | `partial` | CLI shared target loader |
| `feat:cli-target-surface-loading-001` | 4 | `partial` | CLI target surface loading |
| `feat:supported-server-cli-smoke-dispatch` | 4 | `implemented` | Supported-server CLI smoke dispatch |
| `feat:unified-tigrbl-cli-command-and-flag-surface` | 4 | `implemented` | Unified tigrbl CLI command and flag surface |

## diagnostics (1)

| Feature | Tests | Impl | Title |
| --- | ---: | --- | --- |
| `feat:operation-diagnostics-projection-001` | 2 | `partial` | Operation diagnostics projection |

## integration-coverage (1)

| Feature | Tests | Impl | Title |
| --- | ---: | --- | --- |
| `feat:deprecated-export-compat-window-001` | 1 | `partial` | Deprecated export compatibility window |

## jsonrpc (3)

| Feature | Tests | Impl | Title |
| --- | ---: | --- | --- |
| `feat:http-rest-jsonrpc-atom-chains-001` | 0 | `absent` | HTTP REST and JSON-RPC atom chains |
| `feat:dispatch-exchange-family-subevent-atoms-001` | 1 | `absent` | Dispatch exchange family subevent atoms |
| `feat:framing-decode-encode-atoms-001` | 1 | `absent` | Framing decode and encode atoms |

## jsonrpc-validation-hardening (2)

| Feature | Tests | Impl | Title |
| --- | ---: | --- | --- |
| `feat:jsonrpc-input-validation-before-persistence-001` | 3 | `implemented` | JSON-RPC input validation before persistence |
| `feat:jsonrpc-persistence-error-sanitization-001` | 3 | `implemented` | JSON-RPC persistence exception response sanitization |

## legacy-feature-id-alias (21)

| Feature | Tests | Impl | Title |
| --- | ---: | --- | --- |
| `feat:gate-009` | 0 | `partial` | Obsolete alias for Gate C conformance and security checkpoint conditions |
| `feat:oas-001` | 0 | `partial` | Obsolete alias for OpenAPI 3.1.0 document emission |
| `feat:oas-002` | 0 | `partial` | Obsolete alias for OpenAPI JSON Schema Draft 2020-12 dialect declaration |
| `feat:oas-003` | 0 | `partial` | Obsolete alias for OpenAPI components.schemas emission |
| `feat:oas-004` | 0 | `partial` | Obsolete alias for OpenAPI request body, response, and parameter emission |
| `feat:oas-006` | 0 | `partial` | Obsolete alias for Mounted OpenAPI JSON and Swagger docs surface |
| `feat:op-001` | 0 | `partial` | Obsolete alias for Static files operator surface |
| `feat:op-002` | 0 | `partial` | Obsolete alias for Cookie request and response round-trip surface |
| `feat:op-003` | 0 | `partial` | Obsolete alias for Streaming response operator surface |
| `feat:op-004` | 0 | `partial` | Obsolete alias for WebSocket route operator surface |
| `feat:op-005` | 0 | `partial` | Obsolete alias for WHATWG SSE event-stream operator surface |
| `feat:op-006` | 0 | `partial` | Obsolete alias for Form and multipart request operator surface |
| `feat:op-007` | 0 | `partial` | Obsolete alias for Uploaded file request operator surface |
| `feat:op-008` | 0 | `partial` | Obsolete alias for Bounded built-in middleware catalog |
| `feat:op-009` | 0 | `partial` | Obsolete alias for Dependency and hook based auth operator surface |
| `feat:op-010` | 0 | `partial` | Obsolete alias for AsyncAPI UI de-scoped while AsyncAPI spec remains in scope |
| `feat:op-011` | 0 | `partial` | Obsolete alias for JSON Schema UI de-scoped while schema bundle remains in scope |
| `feat:op-012` | 0 | `partial` | Obsolete alias for OIDC discovery and docs surface de-scoped from current cycle |
| `feat:rpc-001` | 0 | `partial` | Obsolete alias for JSON-RPC 2.0 runtime surface |
| `feat:rpc-002` | 0 | `partial` | Obsolete alias for OpenRPC 1.2.6 JSON document surface |
| `feat:rpc-003` | 0 | `partial` | Obsolete alias for Lens OpenRPC UI surface |

## operator-surface (14)

| Feature | Tests | Impl | Title |
| --- | ---: | --- | --- |
| `feat:datatype-adapter-registry-contract-001` | 2 | `partial` | Datatype adapter and registry contract |
| `feat:reflected-datatype-mapper-reverse-mapping-001` | 2 | `partial` | Reflected datatype mapper and reverse mapping |
| `feat:schema-reflection-roundtrip-recovery-001` | 2 | `partial` | Schema reflection round-trip recovery |
| `feat:monotone-spec-merge-precedence-001` | 3 | `partial` | Monotone spec-merge precedence |
| `feat:operator-asyncapi-ui-descoped-001` | 3 | `partial` | AsyncAPI UI de-scoped while AsyncAPI spec remains in scope |
| `feat:operator-bounded-middleware-catalog-001` | 3 | `partial` | Bounded built-in middleware catalog |
| `feat:operator-cookie-roundtrip-surface-001` | 3 | `partial` | Cookie request and response round-trip surface |
| `feat:operator-form-multipart-surface-001` | 3 | `partial` | Form and multipart request operator surface |
| `feat:operator-json-schema-ui-descoped-001` | 3 | `partial` | JSON Schema UI de-scoped while schema bundle remains in scope |
| `feat:operator-sse-event-stream-surface-001` | 3 | `partial` | WHATWG SSE event-stream operator surface |
| `feat:operator-static-files-surface-001` | 3 | `partial` | Static files operator surface |
| `feat:operator-streaming-response-surface-001` | 3 | `partial` | Streaming response operator surface |
| `feat:operator-uploaded-file-surface-001` | 3 | `partial` | Uploaded file request operator surface |
| `feat:operator-websocket-route-surface-001` | 3 | `partial` | WebSocket route operator surface |

## op-owner-scope (3)

| Feature | Tests | Impl | Title |
| --- | ---: | --- | --- |
| `feat:op-ctx-app-owner-scope-materialization-001` | 2 | `partial` | op_ctx app owner-scope materialization |
| `feat:op-ctx-router-owner-scope-materialization-001` | 2 | `partial` | op_ctx router owner-scope materialization |
| `feat:op-ctx-table-owner-scope-materialization-001` | 2 | `partial` | op_ctx table owner-scope materialization |

## protocol-runtime-governance (10)

| Feature | Tests | Impl | Title |
| --- | ---: | --- | --- |
| `feat:completion-fence-emit-complete-001` | 2 | `absent` | Completion fence emit-complete semantics |
| `feat:eventful-protocol-decorator-surface-001` | 2 | `absent` | Eventful protocol decorator surface |
| `feat:eventkey-bit-coded-dispatch-001` | 2 | `absent` | EventKey bit-coded dispatch |
| `feat:eventkey-hook-bucket-compilation-001` | 2 | `absent` | EventKey hook bucket compilation |
| `feat:opchannel-capability-handshake-001` | 2 | `absent` | OpChannel capability handshake |
| `feat:owner-dispatch-loop-modes-001` | 2 | `absent` | Owner and dispatch loop modes |
| `feat:primary-secondary-subevent-selection-001` | 2 | `absent` | Primary and secondary subevent selection |
| `feat:segment-fusion-barrier-policy-001` | 2 | `absent` | Segment fusion barrier policy |
| `feat:subevent-handler-dispatch-001` | 2 | `absent` | Subevent handler dispatch |
| `feat:two-axis-lifecycle-matrix-001` | 2 | `absent` | Two-axis lifecycle matrix |

## runtime-kernel (45)

| Feature | Tests | Impl | Title |
| --- | ---: | --- | --- |
| `feat:bindingspec-event-subevent-schema-001` | 0 | `absent` | BindingSpec event and subevent schema |
| `feat:bindingspec-kernelplan-protocol-compilation-001` | 0 | `absent` | BindingSpec KernelPlan protocol compilation |
| `feat:derived-runtime-subevent-taxonomy-001` | 0 | `absent` | Derived runtime subevent taxonomy |
| `feat:eventful-channel-state-metadata-001` | 0 | `absent` | Eventful channel state metadata |
| `feat:first-class-callback-runtime-001` | 0 | `absent` | First-class callback runtime |
| `feat:first-class-webhook-delivery-001` | 0 | `absent` | First-class webhook delivery |
| `feat:lifespan-runtime-chain-001` | 0 | `absent` | Lifespan runtime chain |
| `feat:static-file-runtime-chain-001` | 0 | `absent` | Static file runtime chain |
| `feat:subevent-transaction-units-001` | 0 | `absent` | Subevent transaction units |
| `feat:transport-accept-emit-close-atoms-001` | 0 | `absent` | Transport accept emit close atoms |
| `feat:transport-event-registry-001` | 0 | `absent` | Transport event registry |
| `feat:webtransport-transport-events-001` | 0 | `absent` | WebTransport transport events |
| `feat:app-framed-message-codec-runtime-001` | 1 | `absent` | App-framed message codec runtime |
| `feat:binding-subevent-phase-atom-legality-matrix-001` | 1 | `absent` | Binding subevent phase atom legality matrix |
| `feat:canonical-exchange-normalization-001` | 1 | `absent` | Canonical exchange normalization |
| `feat:canonical-ingress-route-phase-cleanup-001` | 1 | `absent` | Canonical INGRESS_ROUTE phase cleanup |
| `feat:compiled-loop-regions-001` | 1 | `absent` | Compiled loop regions |
| `feat:extended-hook-selector-matching-001` | 1 | `absent` | Extended hook selector matching |
| `feat:http-stream-atom-chains-001` | 1 | `absent` | HTTP stream atom chains |
| `feat:message-datagram-runtime-families-001` | 1 | `absent` | Message and datagram runtime families |
| `feat:phase-tree-error-branches-001` | 1 | `absent` | Phase tree error branches |
| `feat:post-emit-completion-fence-compilation-001` | 1 | `absent` | POST_EMIT completion fence compilation |
| `feat:protocol-fused-segments-001` | 1 | `absent` | Protocol fused segments |
| `feat:protocol-phase-tree-plans-001` | 1 | `absent` | Protocol phase tree plans |
| `feat:protocol-scope-schemas-001` | 1 | `absent` | Protocol scope schemas |
| `feat:runtime-owned-hook-legality-enforcement-001` | 1 | `absent` | Runtime-owned hook legality enforcement |
| `feat:sse-lazy-iterator-runtime-001` | 1 | `absent` | SSE lazy iterator runtime |
| `feat:sse-session-message-stream-chains-001` | 1 | `absent` | SSE session message stream chains |
| `feat:websocket-concrete-runtime-class-001` | 1 | `partial` | WebSocket concrete runtime class |
| `feat:websocket-wss-atom-chains-001` | 1 | `absent` | WebSocket and WSS atom chains |
| `feat:yield-iterator-producer-001` | 1 | `absent` | Yield iterator producer |
| `feat:default-canonical-engine-family-datatype-alignment-001` | 2 | `partial` | Default canonical engine-family datatype alignment |
| `feat:operator-surface-framing-semantics-001` | 2 | `partial` | Operator-surface framing and multipart semantics |
| `feat:python-engine-session-lifecycle-001` | 2 | `absent` | Python engine session lifecycle separation |
| `feat:python-schema-readiness-fail-closed-001` | 2 | `absent` | Python schema readiness fail-closed behavior |
| `feat:rust-engine-session-lifecycle-001` | 2 | `absent` | Rust engine session lifecycle separation |
| `feat:rust-schema-readiness-fail-closed-001` | 2 | `absent` | Rust schema readiness fail-closed behavior |
| `feat:canonical-datatype-catalog-semantic-center-001` | 3 | `partial` | Canonical datatype catalog and semantic center |
| `feat:columnspec-datatype-attachment-point-001` | 3 | `partial` | ColumnSpec datatype attachment point |
| `feat:engine-datatype-lowering-registry-bridge-001` | 3 | `partial` | Engine datatype lowering and registry bridge |
| `feat:multipart-form-preservation-001` | 3 | `partial` | Multipart form preservation |
| `feat:operator-surface-smoke-runtime-parity-001` | 3 | `partial` | Operator-surface smoke/runtime parity |
| `feat:sse-event-framing-001` | 3 | `partial` | SSE event framing |
| `feat:stream-chunk-order-preservation-001` | 3 | `partial` | Stream chunk order preservation |
| `feat:uploaded-file-runtime-contract-001` | 3 | `partial` | Uploaded file runtime contract |

## runtime-root-surface (1)

| Feature | Tests | Impl | Title |
| --- | ---: | --- | --- |
| `feat:default-root-path-contract-001` | 3 | `implemented` | Default root path contract |

## server-support (7)

| Feature | Tests | Impl | Title |
| --- | ---: | --- | --- |
| `feat:server-support-daphne-001` | 2 | `implemented` | Out-of-boundary server daphne |
| `feat:server-support-granian-001` | 2 | `implemented` | Out-of-boundary server granian |
| `feat:server-support-gunicorn-001` | 2 | `implemented` | Supported server gunicorn |
| `feat:server-support-hypercorn-001` | 2 | `implemented` | Supported server hypercorn |
| `feat:server-support-tigrcorn-001` | 2 | `implemented` | Supported server tigrcorn |
| `feat:server-support-twisted-001` | 2 | `implemented` | Out-of-boundary server twisted |
| `feat:server-support-uvicorn-001` | 2 | `implemented` | Supported server uvicorn |

## spec-composition (1)

| Feature | Tests | Impl | Title |
| --- | ---: | --- | --- |
| `feat:appspec-routerspec-composition-001` | 1 | `partial` | AppSpec and RouterSpec composition |

## spec-linked-unslotted (2)

| Feature | Tests | Impl | Title |
| --- | ---: | --- | --- |
| `feat:tx-phase-legacy-alias-deprecation-001` | 0 | `absent` | Deprecate legacy transaction phase aliases |
| `feat:tx-phase-legacy-alias-removal-001` | 1 | `absent` | Remove legacy transaction phase aliases |

## ssot-governance (32)

| Feature | Tests | Impl | Title |
| --- | ---: | --- | --- |
| `feat:protocol-runtime-boundary-certification-001` | 0 | `absent` | Protocol runtime boundary certification |
| `feat:protocol-runtime-profile-pack-001` | 0 | `absent` | Protocol runtime profile pack |
| `feat:protocol-runtime-ssot-feature-granularity-001` | 0 | `absent` | Protocol runtime SSOT feature granularity |
| `feat:protocol-runtime-test-evidence-suite-001` | 0 | `absent` | Protocol runtime test evidence suite |
| `feat:rust-protocol-plan-parity-001` | 0 | `absent` | Rust protocol plan parity |
| `feat:protocol-anchor-ordering-parity-001` | 1 | `absent` | Protocol anchor ordering parity |
| `feat:tree-loop-aware-executors-001` | 1 | `absent` | Tree and loop aware executors |
| `feat:python-asgi-boundary-evidence-001` | 2 | `absent` | Python ASGI boundary evidence |
| `feat:python-direct-runtime-microbench-001` | 2 | `absent` | Python direct runtime microbenchmark lane |
| `feat:python-request-envelope-contract-001` | 2 | `absent` | Python request envelope contract |
| `feat:python-request-hot-path-no-ddl-001` | 2 | `absent` | Python request hot path excludes DDL |
| `feat:python-runtime-2x-target-comparison-001` | 2 | `absent` | Python baseline for Rust 2x comparison |
| `feat:python-runtime-callgraph-export-001` | 2 | `absent` | Python executor callgraph export |
| `feat:python-runtime-ddl-initialization-boundary-001` | 2 | `absent` | Python runtime DDL initialization boundary |
| `feat:python-runtime-performance-baseline-001` | 2 | `absent` | Python executor benchmark baseline |
| `feat:python-transaction-hot-path-001` | 2 | `absent` | Python transaction hot path evidence |
| `feat:rust-asgi-boundary-evidence-001` | 2 | `absent` | Rust executor under Python ASGI boundary evidence |
| `feat:rust-direct-runtime-microbench-001` | 2 | `absent` | Rust direct runtime microbenchmark lane |
| `feat:rust-request-envelope-contract-001` | 2 | `absent` | Rust request envelope contract |
| `feat:rust-request-hot-path-no-ddl-001` | 2 | `absent` | Rust request hot path excludes DDL |
| `feat:rust-runtime-2x-python-target-001` | 2 | `absent` | Rust executor 2x Python throughput target |
| `feat:rust-runtime-callgraph-export-001` | 2 | `absent` | Rust executor callgraph export |
| `feat:rust-runtime-ddl-initialization-boundary-001` | 2 | `absent` | Rust runtime DDL initialization boundary |
| `feat:rust-runtime-performance-baseline-001` | 2 | `absent` | Rust executor benchmark baseline |
| `feat:rust-transaction-hot-path-001` | 2 | `absent` | Rust transaction hot path optimization |
| `feat:docs-ci-projection-validation-001` | 3 | `implemented` | Docs and CI projection validation |
| `feat:ssot-authority-migration-001` | 3 | `implemented` | SSOT authority migration |
| `feat:tigrbl-concrete-kernel-import-boundary-001` | 3 | `implemented` | tigrbl_concrete kernel import boundary |
| `feat:feature-test-coverage-completeness-001` | 4 | `implemented` | Feature verification coverage completeness |
| `feat:gate-evaluator-model-001` | 4 | `implemented` | SSOT gate evaluator model |
| `feat:test-result-evidence-ingestion-001` | 4 | `implemented` | Test result evidence ingestion |
| `feat:tool-test-gate-taxonomy-001` | 4 | `implemented` | Tool, test, evidence, and gate taxonomy |

## surface-inventory (98)

| Feature | Tests | Impl | Title |
| --- | ---: | --- | --- |
| `feat:aliasbase-contract-001` | 1 | `partial` | AliasBase contract |
| `feat:aliasspec-contract-001` | 1 | `partial` | AliasSpec contract |
| `feat:appbase-contract-001` | 1 | `partial` | AppBase contract |
| `feat:appbase-public-projection-001` | 1 | `partial` | AppBase public projection |
| `feat:attrdict-contract-001` | 1 | `partial` | AttrDict contract |
| `feat:bind-helper-surface-001` | 1 | `partial` | bind helper surface |
| `feat:bindingbase-contract-001` | 1 | `partial` | BindingBase contract |
| `feat:bindingregistrybase-contract-001` | 1 | `partial` | BindingRegistryBase contract |
| `feat:bindingregistryspec-contract-001` | 1 | `partial` | BindingRegistrySpec contract |
| `feat:bindingspec-contract-001` | 1 | `partial` | BindingSpec contract |
| `feat:build-healthz-endpoint-helper-001` | 1 | `partial` | build_healthz_endpoint helper surface |
| `feat:build-hookz-endpoint-helper-001` | 1 | `partial` | build_hookz_endpoint helper surface |
| `feat:build-methodz-endpoint-helper-001` | 1 | `partial` | build_methodz_endpoint helper surface |
| `feat:build-schemas-helper-surface-001` | 1 | `partial` | build_schemas helper surface |
| `feat:columnbase-contract-001` | 1 | `partial` | ColumnBase contract |
| `feat:datatypespec-contract-001` | 1 | `partial` | DataTypeSpec contract |
| `feat:depends-concrete-dependency-helper-001` | 1 | `partial` | Depends concrete dependency helper |
| `feat:diagnostics-router-mount-surface-001` | 1 | `partial` | Diagnostics router mount surface |
| `feat:foreignkeybase-contract-001` | 1 | `partial` | ForeignKeyBase contract |
| `feat:foreignkeybase-public-projection-001` | 1 | `partial` | ForeignKeyBase public projection |
| `feat:get-schema-python-helper-surface-001` | 1 | `partial` | get_schema Python helper surface |
| `feat:healthz-mount-surface-001` | 1 | `partial` | Healthz mount surface |
| `feat:healthz-uix-surface-001` | 1 | `absent` | Healthz UIX surface |
| `feat:hookbase-contract-001` | 1 | `partial` | HookBase contract |
| `feat:hookbase-public-projection-001` | 1 | `partial` | HookBase public projection |
| `feat:hookphase-vocabulary-001` | 1 | `partial` | HookPhase vocabulary |
| `feat:hookspec-contract-001` | 1 | `partial` | HookSpec contract |
| `feat:hookz-mount-surface-001` | 1 | `partial` | Hookz mount surface |
| `feat:hookz-payload-surface-001` | 1 | `partial` | Hookz payload surface |
| `feat:include-tables-helper-surface-001` | 1 | `partial` | include_tables helper surface |
| `feat:kernelz-mount-surface-001` | 1 | `partial` | Kernelz mount surface |
| `feat:kernelz-uix-surface-001` | 1 | `absent` | Kernelz UIX surface |
| `feat:methodz-mount-surface-001` | 1 | `partial` | Methodz mount surface |
| `feat:methodz-payload-surface-001` | 1 | `partial` | Methodz payload surface |
| `feat:middleware-extension-surface-001` | 1 | `partial` | Middleware extension surface |
| `feat:middlewarespec-protocol-001` | 1 | `partial` | MiddlewareSpec protocol |
| `feat:middleware-surface-auth-separation-001` | 1 | `partial` | Middleware and auth-surface separation |
| `feat:middleware-surface-builtin-catalog-001` | 1 | `partial` | Middleware built-in catalog boundary |
| `feat:middleware-surface-protocol-composition-001` | 1 | `partial` | Middleware protocol and composition |
| `feat:middleware-surface-public-projection-001` | 1 | `partial` | Middleware public projection |
| `feat:opbase-contract-001` | 1 | `partial` | OpBase contract |
| `feat:rebind-helper-surface-001` | 1 | `partial` | rebind helper surface |
| `feat:reflecteddatatype-contract-001` | 1 | `partial` | ReflectedDatatype contract |
| `feat:reflectedtypemapper-contract-001` | 1 | `partial` | ReflectedTypeMapper contract |
| `feat:routerbase-contract-001` | 1 | `partial` | RouterBase contract |
| `feat:routerbase-public-projection-001` | 1 | `partial` | RouterBase public projection |
| `feat:schemabase-contract-001` | 1 | `partial` | SchemaBase contract |
| `feat:schemaref-contract-001` | 1 | `partial` | SchemaRef contract |
| `feat:schemaspec-contract-001` | 1 | `partial` | SchemaSpec contract |
| `feat:storagetransformbase-contract-001` | 1 | `partial` | StorageTransformBase contract |
| `feat:storagetransformspec-contract-001` | 1 | `partial` | StorageTransformSpec contract |
| `feat:storagetyperef-contract-001` | 1 | `partial` | StorageTypeRef contract |
| `feat:tablebase-contract-001` | 1 | `partial` | TableBase contract |
| `feat:tablebase-public-projection-001` | 1 | `partial` | TableBase public projection |
| `feat:tableregistrybase-contract-001` | 1 | `partial` | TableRegistryBase contract |
| `feat:tableregistrybase-public-projection-001` | 1 | `partial` | TableRegistryBase public projection |
| `feat:tableregistryspec-contract-001` | 1 | `partial` | TableRegistrySpec contract |
| `feat:templatespec-contract-001` | 1 | `partial` | TemplateSpec contract |
| `feat:typeadapter-protocol-001` | 1 | `partial` | TypeAdapter protocol |
| `feat:typeregistry-contract-001` | 1 | `partial` | TypeRegistry contract |
| `feat:build-kernelz-endpoint-helper-001` | 2 | `partial` | build_kernelz_endpoint helper surface |
| `feat:default-canonical-engine-catalog-001` | 2 | `partial` | Default canonical engine catalog |
| `feat:enginebase-contract-001` | 2 | `partial` | EngineBase contract |
| `feat:enginedatatypebridge-contract-001` | 2 | `partial` | EngineDatatypeBridge contract |
| `feat:engine-extension-surface-001` | 2 | `partial` | Engine extension surface |
| `feat:engineproviderbase-contract-001` | 2 | `partial` | EngineProviderBase contract |
| `feat:engineproviderspec-contract-001` | 2 | `partial` | EngineProviderSpec contract |
| `feat:engineregistry-contract-001` | 2 | `partial` | EngineRegistry contract |
| `feat:enginespec-contract-001` | 2 | `partial` | EngineSpec contract |
| `feat:engine-surface-public-projection-001` | 2 | `partial` | Engine public and base projection |
| `feat:enginetypelowerer-protocol-001` | 2 | `partial` | EngineTypeLowerer protocol |
| `feat:http-jsonrpc-bindingspec-contract-001` | 2 | `partial` | HttpJsonRpcBindingSpec contract |
| `feat:http-rest-bindingspec-contract-001` | 2 | `partial` | HttpRestBindingSpec contract |
| `feat:http-stream-bindingspec-contract-001` | 2 | `partial` | HttpStreamBindingSpec contract |
| `feat:mount-static-helper-surface-001` | 2 | `partial` | mount_static helper surface |
| `feat:requestbase-contract-001` | 2 | `partial` | RequestBase contract |
| `feat:requestspec-contract-001` | 2 | `partial` | RequestSpec contract |
| `feat:schema-migration-runtime-surface-001` | 2 | `absent` | Schema migration runtime surface |
| `feat:sessionabc-contract-001` | 2 | `partial` | SessionABC contract |
| `feat:sessionspec-contract-001` | 2 | `partial` | SessionSpec contract |
| `feat:sqlite-attach-runtime-surface-001` | 2 | `partial` | register_sqlite_attach runtime surface |
| `feat:sse-bindingspec-contract-001` | 2 | `partial` | SseBindingSpec contract |
| `feat:tigrblsessionbase-contract-001` | 2 | `partial` | TigrblSessionBase contract |
| `feat:webtransport-bindingspec-contract-001` | 2 | `partial` | WebTransportBindingSpec contract |
| `feat:ws-bindingspec-contract-001` | 2 | `partial` | WsBindingSpec contract |
| `feat:appspec-contract-001` | 3 | `partial` | AppSpec contract |
| `feat:columnspec-contract-001` | 3 | `partial` | ColumnSpec contract |
| `feat:fieldspec-contract-001` | 3 | `partial` | FieldSpec contract |
| `feat:foreignkeyspec-contract-001` | 3 | `partial` | ForeignKeySpec contract |
| `feat:iospec-contract-001` | 3 | `partial` | IOSpec contract |
| `feat:opspec-contract-001` | 3 | `partial` | OpSpec contract |
| `feat:routerspec-contract-001` | 3 | `partial` | RouterSpec contract |
| `feat:static-files-surface-001` | 3 | `partial` | Static files surface |
| `feat:storagespec-contract-001` | 3 | `partial` | StorageSpec contract |
| `feat:well-known-concrete-constants-surface-001` | 3 | `partial` | Well-known concrete constants surface |
| `feat:well-known-imperative-surface-001` | 3 | `partial` | Well-known imperative surface |
| `feat:responsespec-contract-001` | 4 | `partial` | ResponseSpec contract |
| `feat:tablespec-contract-001` | 4 | `partial` | TableSpec contract |

## transport-dispatch (1)

| Feature | Tests | Impl | Title |
| --- | ---: | --- | --- |
| `feat:mapping-dispatch-convergence-001` | 2 | `partial` | Mapping dispatch convergence |