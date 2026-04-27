# Features Not Robustly Tested

Source: .ssot/registry.json
Generated: 2026-04-27T12:47:45Z

Robustness criteria: feature is listed if it has no linked tests, no passing linked tests, missing test references, or any linked test with status planned/skipped.
Total not robustly tested features: 171

## Priority: next (39)

### Domain: compatibility-surface (3)

| Feature | Title | Impl | Tests | Passing | Planned | Skipped | Reason |
|---|---|---|---:|---:|---:|---:|---|
| `feat:governed-module-alias-compatibility-001` | Governed module alias compatibility | `partial` | 77 | 76 | 0 | 1 | skipped tests: 1 |
| `feat:orm-alias-export-compatibility-001` | tigrbl.orm alias export compatibility | `partial` | 77 | 76 | 0 | 1 | skipped tests: 1 |
| `feat:orm-mixins-alias-compatibility-001` | tigrbl.orm.mixins alias compatibility | `partial` | 77 | 76 | 0 | 1 | skipped tests: 1 |

### Domain: docs-routing-core-surface (6)

| Feature | Title | Impl | Tests | Passing | Planned | Skipped | Reason |
|---|---|---|---:|---:|---:|---:|---|
| `feat:canonical-datatype-catalog-semantic-center-001` | Canonical datatype catalog and semantic center | `partial` | 3 | 1 | 2 | 0 | planned tests: 2 |
| `feat:columnspec-datatype-attachment-point-001` | ColumnSpec datatype attachment point | `partial` | 3 | 1 | 2 | 0 | planned tests: 2 |
| `feat:datatype-adapter-registry-contract-001` | Datatype adapter and registry contract | `partial` | 2 | 0 | 2 | 0 | no passing linked tests; planned tests: 2 |
| `feat:engine-datatype-lowering-registry-bridge-001` | Engine datatype lowering and registry bridge | `partial` | 3 | 1 | 2 | 0 | planned tests: 2 |
| `feat:reflected-datatype-mapper-reverse-mapping-001` | Reflected datatype mapper and reverse mapping | `partial` | 2 | 0 | 2 | 0 | no passing linked tests; planned tests: 2 |
| `feat:schema-reflection-roundtrip-recovery-001` | Schema reflection round-trip recovery | `partial` | 2 | 0 | 2 | 0 | no passing linked tests; planned tests: 2 |

### Domain: extension-surface (2)

| Feature | Title | Impl | Tests | Passing | Planned | Skipped | Reason |
|---|---|---|---:|---:|---:|---:|---|
| `feat:default-canonical-engine-family-datatype-alignment-001` | Default canonical engine-family datatype alignment | `partial` | 2 | 1 | 1 | 0 | planned tests: 1 |
| `feat:multi-engine-table-portability-interoperability-001` | Multi-engine table portability and interoperability | `partial` | 34 | 32 | 1 | 1 | planned tests: 1; skipped tests: 1 |

### Domain: ops-hooks-transport (1)

| Feature | Title | Impl | Tests | Passing | Planned | Skipped | Reason |
|---|---|---|---:|---:|---:|---:|---|
| `feat:tx-phase-legacy-alias-deprecation-001` | Deprecate legacy transaction phase aliases | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |

### Domain: runtime-parity (16)

| Feature | Title | Impl | Tests | Passing | Planned | Skipped | Reason |
|---|---|---|---:|---:|---:|---:|---|
| `feat:python-asgi-boundary-evidence-001` | Python ASGI boundary evidence | `absent` | 2 | 1 | 1 | 0 | planned tests: 1 |
| `feat:python-direct-runtime-microbench-001` | Python direct runtime microbenchmark lane | `absent` | 2 | 1 | 1 | 0 | planned tests: 1 |
| `feat:python-engine-session-lifecycle-001` | Python engine session lifecycle separation | `absent` | 2 | 1 | 1 | 0 | planned tests: 1 |
| `feat:python-request-envelope-contract-001` | Python request envelope contract | `absent` | 2 | 1 | 1 | 0 | planned tests: 1 |
| `feat:python-runtime-2x-target-comparison-001` | Python baseline for Rust 2x comparison | `absent` | 2 | 1 | 1 | 0 | planned tests: 1 |
| `feat:python-runtime-callgraph-export-001` | Python executor callgraph export | `absent` | 2 | 1 | 1 | 0 | planned tests: 1 |
| `feat:python-runtime-performance-baseline-001` | Python executor benchmark baseline | `absent` | 2 | 1 | 1 | 0 | planned tests: 1 |
| `feat:python-transaction-hot-path-001` | Python transaction hot path evidence | `absent` | 2 | 1 | 1 | 0 | planned tests: 1 |
| `feat:rust-asgi-boundary-evidence-001` | Rust executor under Python ASGI boundary evidence | `absent` | 2 | 1 | 1 | 0 | planned tests: 1 |
| `feat:rust-direct-runtime-microbench-001` | Rust direct runtime microbenchmark lane | `absent` | 2 | 1 | 1 | 0 | planned tests: 1 |
| `feat:rust-engine-session-lifecycle-001` | Rust engine session lifecycle separation | `absent` | 2 | 1 | 1 | 0 | planned tests: 1 |
| `feat:rust-request-envelope-contract-001` | Rust request envelope contract | `absent` | 2 | 1 | 1 | 0 | planned tests: 1 |
| `feat:rust-runtime-2x-python-target-001` | Rust executor 2x Python throughput target | `absent` | 2 | 1 | 1 | 0 | planned tests: 1 |
| `feat:rust-runtime-callgraph-export-001` | Rust executor callgraph export | `absent` | 2 | 1 | 1 | 0 | planned tests: 1 |
| `feat:rust-runtime-performance-baseline-001` | Rust executor benchmark baseline | `absent` | 2 | 1 | 1 | 0 | planned tests: 1 |
| `feat:rust-transaction-hot-path-001` | Rust transaction hot path optimization | `absent` | 2 | 1 | 1 | 0 | planned tests: 1 |

### Domain: surface-inventory (1)

| Feature | Title | Impl | Tests | Passing | Planned | Skipped | Reason |
|---|---|---|---:|---:|---:|---:|---|
| `feat:bootstrappable-table-mixin-001` | Bootstrappable table mixin | `partial` | 77 | 76 | 0 | 1 | skipped tests: 1 |

### Domain: transport-dispatch (4)

| Feature | Title | Impl | Tests | Passing | Planned | Skipped | Reason |
|---|---|---|---:|---:|---:|---:|---|
| `feat:executor-dispatch-removal-001` | Executors do not perform transport matching | `partial` | 9 | 7 | 1 | 1 | planned tests: 1; skipped tests: 1 |
| `feat:kernelplan-dispatch-ownership-001` | KernelPlan and atoms own transport lookup and matching | `partial` | 9 | 7 | 1 | 1 | planned tests: 1; skipped tests: 1 |
| `feat:transport-bypass-removal-001` | Remove non-conforming transport bypasses | `partial` | 9 | 7 | 1 | 1 | planned tests: 1; skipped tests: 1 |
| `feat:transport-parity-contract-001` | REST and JSON-RPC parity through the shared dispatch path | `partial` | 8 | 7 | 0 | 1 | skipped tests: 1 |

### Domain: unspecified (6)

| Feature | Title | Impl | Tests | Passing | Planned | Skipped | Reason |
|---|---|---|---:|---:|---:|---:|---|
| `feat:python-request-hot-path-no-ddl-001` | Python request hot path excludes DDL | `absent` | 2 | 1 | 1 | 0 | planned tests: 1 |
| `feat:python-runtime-ddl-initialization-boundary-001` | Python runtime DDL initialization boundary | `absent` | 2 | 1 | 1 | 0 | planned tests: 1 |
| `feat:python-schema-readiness-fail-closed-001` | Python schema readiness fail-closed behavior | `absent` | 2 | 1 | 1 | 0 | planned tests: 1 |
| `feat:rust-request-hot-path-no-ddl-001` | Rust request hot path excludes DDL | `absent` | 2 | 1 | 1 | 0 | planned tests: 1 |
| `feat:rust-runtime-ddl-initialization-boundary-001` | Rust runtime DDL initialization boundary | `absent` | 2 | 1 | 1 | 0 | planned tests: 1 |
| `feat:rust-schema-readiness-fail-closed-001` | Rust schema readiness fail-closed behavior | `absent` | 2 | 1 | 1 | 0 | planned tests: 1 |

## Priority: explicit (1)

### Domain: buildability-baseline-001 (1)

| Feature | Title | Impl | Tests | Passing | Planned | Skipped | Reason |
|---|---|---|---:|---:|---:|---:|---|
| `feat:package-buildability-importability-001` | Package buildability and importability baseline | `partial` | 1 | 0 | 1 | 0 | no passing linked tests; planned tests: 1 |

## Priority: backlog (30)

### Domain: docs-routing-core-surface (13)

| Feature | Title | Impl | Tests | Passing | Planned | Skipped | Reason |
|---|---|---|---:|---:|---:|---:|---|
| `feat:binding-driven-ingress-001` | Binding-driven REST and JSON-RPC ingress materialization | `partial` | 41 | 39 | 2 | 0 | planned tests: 2 |
| `feat:canonical-op-aggregate-001` | Canonical op aggregate | `partial` | 40 | 39 | 1 | 0 | planned tests: 1 |
| `feat:canonical-op-append-chunk-001` | Canonical op append_chunk | `partial` | 40 | 39 | 1 | 0 | planned tests: 1 |
| `feat:canonical-op-checkpoint-001` | Canonical op checkpoint | `partial` | 40 | 39 | 1 | 0 | planned tests: 1 |
| `feat:canonical-op-download-001` | Canonical op download | `partial` | 40 | 39 | 1 | 0 | planned tests: 1 |
| `feat:canonical-op-group-by-001` | Canonical op group_by | `partial` | 40 | 39 | 1 | 0 | planned tests: 1 |
| `feat:canonical-op-publish-001` | Canonical op publish | `partial` | 40 | 39 | 1 | 0 | planned tests: 1 |
| `feat:canonical-op-send-datagram-001` | Canonical op send_datagram | `partial` | 40 | 39 | 1 | 0 | planned tests: 1 |
| `feat:canonical-op-subscribe-001` | Canonical op subscribe | `partial` | 40 | 39 | 1 | 0 | planned tests: 1 |
| `feat:canonical-op-tail-001` | Canonical op tail | `partial` | 40 | 39 | 1 | 0 | planned tests: 1 |
| `feat:canonical-op-upload-001` | Canonical op upload | `partial` | 40 | 39 | 1 | 0 | planned tests: 1 |
| `feat:jsonrpc-endpoint-key-001` | Endpoint-keyed JSON-RPC multiplexing | `partial` | 40 | 39 | 1 | 0 | planned tests: 1 |
| `feat:transport-dispatch-governance-001` | Transport-dispatch governance track setup | `partial` | 47 | 46 | 0 | 1 | skipped tests: 1 |

### Domain: extension-surface (16)

| Feature | Title | Impl | Tests | Passing | Planned | Skipped | Reason |
|---|---|---|---:|---:|---:|---:|---|
| `feat:canonical-op-bulk-create-001` | Canonical op bulk_create | `partial` | 40 | 39 | 1 | 0 | planned tests: 1 |
| `feat:canonical-op-bulk-delete-001` | Canonical op bulk_delete | `partial` | 40 | 39 | 1 | 0 | planned tests: 1 |
| `feat:canonical-op-bulk-merge-001` | Canonical op bulk_merge | `partial` | 40 | 39 | 1 | 0 | planned tests: 1 |
| `feat:canonical-op-bulk-replace-001` | Canonical op bulk_replace | `partial` | 40 | 39 | 1 | 0 | planned tests: 1 |
| `feat:canonical-op-bulk-update-001` | Canonical op bulk_update | `partial` | 40 | 39 | 1 | 0 | planned tests: 1 |
| `feat:canonical-op-clear-001` | Canonical op clear | `partial` | 40 | 39 | 1 | 0 | planned tests: 1 |
| `feat:canonical-op-count-001` | Canonical op count | `partial` | 40 | 39 | 1 | 0 | planned tests: 1 |
| `feat:canonical-op-create-001` | Canonical op create | `partial` | 40 | 39 | 1 | 0 | planned tests: 1 |
| `feat:canonical-op-custom-001` | Canonical op custom | `partial` | 40 | 39 | 1 | 0 | planned tests: 1 |
| `feat:canonical-op-delete-001` | Canonical op delete | `partial` | 40 | 39 | 1 | 0 | planned tests: 1 |
| `feat:canonical-op-exists-001` | Canonical op exists | `partial` | 40 | 39 | 1 | 0 | planned tests: 1 |
| `feat:canonical-op-list-001` | Canonical op list | `partial` | 40 | 39 | 1 | 0 | planned tests: 1 |
| `feat:canonical-op-merge-001` | Canonical op merge | `partial` | 40 | 39 | 1 | 0 | planned tests: 1 |
| `feat:canonical-op-read-001` | Canonical op read | `partial` | 40 | 39 | 1 | 0 | planned tests: 1 |
| `feat:canonical-op-replace-001` | Canonical op replace | `partial` | 40 | 39 | 1 | 0 | planned tests: 1 |
| `feat:canonical-op-update-001` | Canonical op update | `partial` | 40 | 39 | 1 | 0 | planned tests: 1 |

### Domain: unspecified (1)

| Feature | Title | Impl | Tests | Passing | Planned | Skipped | Reason |
|---|---|---|---:|---:|---:|---:|---|
| `feat:tigrbl-test-suite-coverage-intake-001` | Tigrbl test suite coverage intake | `partial` | 264 | 255 | 8 | 1 | planned tests: 8; skipped tests: 1 |

## Priority: future (80)

### Domain: docs-routing-core-surface (10)

| Feature | Title | Impl | Tests | Passing | Planned | Skipped | Reason |
|---|---|---|---:|---:|---:|---:|---|
| `feat:appspec-harness-uvicorn-e2e-parity-001` | AppSpec and harness Uvicorn E2E parity | `partial` | 15 | 14 | 0 | 1 | skipped tests: 1 |
| `feat:appspec-imperative-plan-parity-001` | AppSpec and imperative plan parity | `partial` | 14 | 13 | 0 | 1 | skipped tests: 1 |
| `feat:engine-resolver-multi-table-rpc-001` | Engine resolver and multi-table RPC parity under Uvicorn | `partial` | 48 | 46 | 0 | 2 | skipped tests: 2 |
| `feat:engine-resolver-precedence-001` | Engine resolver precedence | `partial` | 15 | 14 | 0 | 1 | skipped tests: 1 |
| `feat:harness-runtime-routing-parity-001` | Harness and runtime routing parity | `partial` | 15 | 14 | 0 | 1 | skipped tests: 1 |
| `feat:jsonrpc-notification-204-projection-001` | JSON-RPC notification 204 projection | `partial` | 15 | 14 | 0 | 1 | skipped tests: 1 |
| `feat:kernel-bootstrap-plan-parity-001` | Kernel bootstrap and plan idempotence parity | `partial` | 15 | 14 | 0 | 1 | skipped tests: 1 |
| `feat:mounted-prefix-routing-parity-001` | Mounted prefix routing parity | `partial` | 15 | 14 | 0 | 1 | skipped tests: 1 |
| `feat:multi-table-routing-parity-001` | Multi-table routing parity | `partial` | 15 | 14 | 0 | 1 | skipped tests: 1 |
| `feat:uvicorn-rest-rpc-semantic-parity-001` | Uvicorn REST and JSON-RPC semantic parity | `partial` | 15 | 14 | 0 | 1 | skipped tests: 1 |

### Domain: integration-coverage (1)

| Feature | Title | Impl | Tests | Passing | Planned | Skipped | Reason |
|---|---|---|---:|---:|---:|---:|---|
| `feat:uvicorn-protocol-mode-runtime-parity-001` | Uvicorn protocol-mode runtime parity | `partial` | 16 | 15 | 0 | 1 | skipped tests: 1 |

### Domain: ops-hooks-transport (7)

| Feature | Title | Impl | Tests | Passing | Planned | Skipped | Reason |
|---|---|---|---:|---:|---:|---:|---|
| `feat:canonical-exchange-normalization-001` | Canonical exchange normalization | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:canonical-ingress-route-phase-cleanup-001` | Canonical INGRESS_ROUTE phase cleanup | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:extended-hook-selector-matching-001` | Extended hook selector matching | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:message-datagram-runtime-families-001` | Message and datagram runtime families | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:post-emit-completion-fence-compilation-001` | POST_EMIT completion fence compilation | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:runtime-owned-hook-legality-enforcement-001` | Runtime-owned hook legality enforcement | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:tx-phase-legacy-alias-removal-001` | Remove legacy transaction phase aliases | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |

### Domain: protocol-runtime (16)

| Feature | Title | Impl | Tests | Passing | Planned | Skipped | Reason |
|---|---|---|---:|---:|---:|---:|---|
| `feat:app-framed-message-codec-runtime-001` | App-framed message codec runtime | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:binding-subevent-phase-atom-legality-matrix-001` | Binding subevent phase atom legality matrix | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:compiled-loop-regions-001` | Compiled loop regions | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:dispatch-exchange-family-subevent-atoms-001` | Dispatch exchange family subevent atoms | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:framing-decode-encode-atoms-001` | Framing decode and encode atoms | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:http-stream-atom-chains-001` | HTTP stream atom chains | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:phase-tree-error-branches-001` | Phase tree error branches | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:protocol-anchor-ordering-parity-001` | Protocol anchor ordering parity | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:protocol-fused-segments-001` | Protocol fused segments | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:protocol-phase-tree-plans-001` | Protocol phase tree plans | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:protocol-scope-schemas-001` | Protocol scope schemas | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:sse-lazy-iterator-runtime-001` | SSE lazy iterator runtime | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:sse-session-message-stream-chains-001` | SSE session message stream chains | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:tree-loop-aware-executors-001` | Tree and loop aware executors | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:websocket-wss-atom-chains-001` | WebSocket and WSS atom chains | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:yield-iterator-producer-001` | Yield iterator producer | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |

### Domain: protocol-runtime-governance (10)

| Feature | Title | Impl | Tests | Passing | Planned | Skipped | Reason |
|---|---|---|---:|---:|---:|---:|---|
| `feat:completion-fence-emit-complete-001` | Completion fence emit-complete semantics | `absent` | 1 | 0 | 1 | 0 | no passing linked tests; planned tests: 1 |
| `feat:eventful-protocol-decorator-surface-001` | Eventful protocol decorator surface | `absent` | 1 | 0 | 1 | 0 | no passing linked tests; planned tests: 1 |
| `feat:eventkey-bit-coded-dispatch-001` | EventKey bit-coded dispatch | `absent` | 1 | 0 | 1 | 0 | no passing linked tests; planned tests: 1 |
| `feat:eventkey-hook-bucket-compilation-001` | EventKey hook bucket compilation | `absent` | 1 | 0 | 1 | 0 | no passing linked tests; planned tests: 1 |
| `feat:opchannel-capability-handshake-001` | OpChannel capability handshake | `absent` | 1 | 0 | 1 | 0 | no passing linked tests; planned tests: 1 |
| `feat:owner-dispatch-loop-modes-001` | Owner and dispatch loop modes | `absent` | 1 | 0 | 1 | 0 | no passing linked tests; planned tests: 1 |
| `feat:primary-secondary-subevent-selection-001` | Primary and secondary subevent selection | `absent` | 1 | 0 | 1 | 0 | no passing linked tests; planned tests: 1 |
| `feat:segment-fusion-barrier-policy-001` | Segment fusion barrier policy | `absent` | 1 | 0 | 1 | 0 | no passing linked tests; planned tests: 1 |
| `feat:subevent-handler-dispatch-001` | Subevent handler dispatch | `absent` | 1 | 0 | 1 | 0 | no passing linked tests; planned tests: 1 |
| `feat:two-axis-lifecycle-matrix-001` | Two-axis lifecycle matrix | `absent` | 1 | 0 | 1 | 0 | no passing linked tests; planned tests: 1 |

### Domain: runtime-parity (2)

| Feature | Title | Impl | Tests | Passing | Planned | Skipped | Reason |
|---|---|---|---:|---:|---:|---:|---|
| `feat:rust-protocol-plan-parity-001` | Rust protocol plan parity | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:subevent-transaction-units-001` | Subevent transaction units | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |

### Domain: ssot-origin (1)

| Feature | Title | Impl | Tests | Passing | Planned | Skipped | Reason |
|---|---|---|---:|---:|---:|---:|---|
| `feat:protocol-runtime-profile-pack-001` | Protocol runtime profile pack | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |

### Domain: surface-inventory (12)

| Feature | Title | Impl | Tests | Passing | Planned | Skipped | Reason |
|---|---|---|---:|---:|---:|---:|---|
| `feat:bootstrap-dbschema-runtime-surface-001` | bootstrap_dbschema runtime surface | `partial` | 33 | 32 | 0 | 1 | skipped tests: 1 |
| `feat:ddl-initialization-modes-001` | DDL initialization modes | `partial` | 32 | 31 | 0 | 1 | skipped tests: 1 |
| `feat:ddl-runtime-surface-001` | DDL runtime surface | `partial` | 33 | 32 | 0 | 1 | skipped tests: 1 |
| `feat:defaultsession-concrete-session-class-001` | DefaultSession concrete session class | `partial` | 32 | 31 | 0 | 1 | skipped tests: 1 |
| `feat:engine-session-runtime-surface-001` | Engine session runtime surface | `partial` | 33 | 32 | 0 | 1 | skipped tests: 1 |
| `feat:engine-surface-contract-001` | Engine surface contract and datatype bridge | `partial` | 33 | 32 | 0 | 1 | skipped tests: 1 |
| `feat:engine-surface-plugin-resolution-001` | Engine plugin registration and resolution | `partial` | 33 | 32 | 0 | 1 | skipped tests: 1 |
| `feat:ensure-schemas-runtime-surface-001` | ensure_schemas runtime surface | `partial` | 33 | 32 | 0 | 1 | skipped tests: 1 |
| `feat:multi-engine-interop-runtime-surface-001` | Multi-engine interop runtime surface | `partial` | 33 | 32 | 0 | 1 | skipped tests: 1 |
| `feat:tigrblapp-concrete-facade-class-001` | TigrblApp concrete facade class | `partial` | 14 | 13 | 0 | 1 | skipped tests: 1 |
| `feat:tigrblrouter-concrete-facade-class-001` | TigrblRouter concrete facade class | `partial` | 14 | 13 | 0 | 1 | skipped tests: 1 |
| `feat:wrap-sessionmaker-helper-surface-001` | wrap_sessionmaker helper surface | `partial` | 32 | 31 | 0 | 1 | skipped tests: 1 |

### Domain: transport-dispatch (6)

| Feature | Title | Impl | Tests | Passing | Planned | Skipped | Reason |
|---|---|---|---:|---:|---:|---:|---|
| `feat:default-kernel-identity-001` | Default kernel identity | `partial` | 15 | 14 | 0 | 1 | skipped tests: 1 |
| `feat:ensure-primed-idempotence-001` | ensure_primed idempotence | `partial` | 15 | 14 | 0 | 1 | skipped tests: 1 |
| `feat:kernel-cache-invalidation-contract-001` | Kernel cache invalidation contract | `partial` | 15 | 14 | 0 | 1 | skipped tests: 1 |
| `feat:kernel-prime-opview-cache-001` | Kernel priming and OpView cache lifecycle | `partial` | 15 | 14 | 0 | 1 | skipped tests: 1 |
| `feat:kernel-priming-runtime-parity-001` | Kernel priming runtime parity | `partial` | 15 | 14 | 0 | 1 | skipped tests: 1 |
| `feat:opview-on-demand-cache-reuse-001` | OpView on-demand cache reuse | `partial` | 15 | 14 | 0 | 1 | skipped tests: 1 |

### Domain: unspecified (15)

| Feature | Title | Impl | Tests | Passing | Planned | Skipped | Reason |
|---|---|---|---:|---:|---:|---:|---|
| `feat:bindingspec-event-subevent-schema-001` | BindingSpec event and subevent schema | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:bindingspec-kernelplan-protocol-compilation-001` | BindingSpec KernelPlan protocol compilation | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:derived-runtime-subevent-taxonomy-001` | Derived runtime subevent taxonomy | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:eventful-channel-state-metadata-001` | Eventful channel state metadata | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:first-class-callback-runtime-001` | First-class callback runtime | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:first-class-webhook-delivery-001` | First-class webhook delivery | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:http-rest-jsonrpc-atom-chains-001` | HTTP REST and JSON-RPC atom chains | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:lifespan-runtime-chain-001` | Lifespan runtime chain | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:protocol-runtime-boundary-certification-001` | Protocol runtime boundary certification | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:protocol-runtime-ssot-feature-granularity-001` | Protocol runtime SSOT feature granularity | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:protocol-runtime-test-evidence-suite-001` | Protocol runtime test evidence suite | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:static-file-runtime-chain-001` | Static file runtime chain | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:transport-accept-emit-close-atoms-001` | Transport accept emit close atoms | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:transport-event-registry-001` | Transport event registry | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:webtransport-transport-events-001` | WebTransport transport events | `absent` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |

## Priority: out_of_bounds (21)

### Domain: legacy-feature-id-alias (21)

| Feature | Title | Impl | Tests | Passing | Planned | Skipped | Reason |
|---|---|---|---:|---:|---:|---:|---|
| `feat:gate-009` | Obsolete alias for Gate C conformance and security checkpoint conditions | `partial` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:oas-001` | Obsolete alias for OpenAPI 3.1.0 document emission | `partial` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:oas-002` | Obsolete alias for OpenAPI JSON Schema Draft 2020-12 dialect declaration | `partial` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:oas-003` | Obsolete alias for OpenAPI components.schemas emission | `partial` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:oas-004` | Obsolete alias for OpenAPI request body, response, and parameter emission | `partial` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:oas-006` | Obsolete alias for Mounted OpenAPI JSON and Swagger docs surface | `partial` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:op-001` | Obsolete alias for Static files operator surface | `partial` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:op-002` | Obsolete alias for Cookie request and response round-trip surface | `partial` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:op-003` | Obsolete alias for Streaming response operator surface | `partial` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:op-004` | Obsolete alias for WebSocket route operator surface | `partial` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:op-005` | Obsolete alias for WHATWG SSE event-stream operator surface | `partial` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:op-006` | Obsolete alias for Form and multipart request operator surface | `partial` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:op-007` | Obsolete alias for Uploaded file request operator surface | `partial` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:op-008` | Obsolete alias for Bounded built-in middleware catalog | `partial` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:op-009` | Obsolete alias for Dependency and hook based auth operator surface | `partial` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:op-010` | Obsolete alias for AsyncAPI UI de-scoped while AsyncAPI spec remains in scope | `partial` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:op-011` | Obsolete alias for JSON Schema UI de-scoped while schema bundle remains in scope | `partial` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:op-012` | Obsolete alias for OIDC discovery and docs surface de-scoped from current cycle | `partial` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:rpc-001` | Obsolete alias for JSON-RPC 2.0 runtime surface | `partial` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:rpc-002` | Obsolete alias for OpenRPC 1.2.6 JSON document surface | `partial` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |
| `feat:rpc-003` | Obsolete alias for Lens OpenRPC UI surface | `partial` | 0 | 0 | 0 | 0 | no linked tests; no passing linked tests |

