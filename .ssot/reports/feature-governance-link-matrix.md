# Feature-to-Governance Link Matrix

This report is generated from `.ssot/registry.json`.

- `source file`: `.ssot/registry.json`
- `row-selection rule`: Explicit runtime/protocol feature seed set from the prior inventory, filtered to real feat:* rows, with stable row ordering by feature_id.
- `column-selection rule`: Highlighted governance IDs first, then any additional ADR/SPEC IDs directly declared by the selected features through adr_ids or spec_ids.
- `cell semantics`: X means the feature directly declares that ADR or SPEC in its own adr_ids or spec_ids.

The matrix is one logical report rendered as separate ADR and SPEC tables so the Markdown remains readable.

## ADR Matrix

Highlighted ADRs appear first, followed by any additional ADRs directly declared by the selected features.

| feature_id | title | implementation_status | adr:1003 | adr:1008 | adr:1016 | adr:1024 | adr:1052 | adr:1088 | adr:1100 | adr:1120 | adr:1121 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `feat:anon-access-rest-status-parity-001` | Anonymous access and REST create status parity | `implemented` |  |  |  |  |  |  |  |  |  |
| `feat:app-framed-message-codec-runtime-001` | App-framed message codec runtime | `absent` |  |  |  |  |  |  |  |  |  |
| `feat:atom-parity-dep-security-001` | Atom parity dep security | `implemented` |  |  |  |  |  |  |  |  |  |
| `feat:atom-parity-egress-asgi-send-001` | Atom parity egress asgi_send | `implemented` |  |  |  |  |  |  |  |  |  |
| `feat:atom-parity-egress-to-transport-response-001` | Atom parity egress to_transport_response | `implemented` |  |  |  |  |  |  |  |  |  |
| `feat:atom-parity-ingress-transport-extract-001` | Atom parity ingress transport_extract | `implemented` |  |  |  |  |  |  |  |  |  |
| `feat:atom-parity-resolve-assemble-001` | Atom parity resolve assemble | `implemented` |  |  |  |  |  |  |  |  |  |
| `feat:atom-parity-response-error-to-transport-001` | Atom parity response error_to_transport | `implemented` |  |  |  |  |  |  |  |  |  |
| `feat:atom-parity-sys-handler-aggregate-001` | Atom parity sys handler_aggregate | `implemented` |  |  |  |  |  |  |  |  |  |
| `feat:binding-driven-ingress-001` | Binding-driven REST and JSON-RPC ingress materialization | `partial` |  |  |  |  |  |  |  |  |  |
| `feat:binding-subevent-phase-atom-legality-matrix-001` | Binding subevent phase atom legality matrix | `absent` |  |  |  |  |  |  |  |  |  |
| `feat:bindingspec-event-subevent-schema-001` | BindingSpec event and subevent schema | `implemented` |  |  |  |  |  |  |  |  |  |
| `feat:bindingspec-kernelplan-protocol-compilation-001` | BindingSpec KernelPlan protocol compilation | `implemented` |  |  |  |  |  |  |  |  |  |
| `feat:canonical-ingress-route-phase-cleanup-001` | Canonical INGRESS_ROUTE phase cleanup | `implemented` |  |  |  |  |  |  |  |  |  |
| `feat:derived-runtime-subevent-taxonomy-001` | Derived runtime subevent taxonomy | `absent` |  |  |  |  |  |  |  |  |  |
| `feat:dispatch-exchange-family-subevent-atoms-001` | Dispatch exchange family subevent atoms | `absent` |  |  |  |  |  |  |  |  |  |
| `feat:eventful-channel-state-metadata-001` | Eventful channel state metadata | `implemented` |  |  |  |  |  |  |  |  |  |
| `feat:eventkey-hook-bucket-compilation-001` | EventKey hook bucket compilation | `implemented` |  |  |  |  |  |  |  |  |  |
| `feat:eventstreamresponse-concrete-sse-class-001` | EventStreamResponse concrete SSE class | `implemented` |  |  |  |  |  |  |  |  |  |
| `feat:executor-dispatch-removal-001` | Executors do not perform transport matching | `partial` |  |  |  |  |  |  |  |  |  |
| `feat:framing-decode-encode-atoms-001` | Framing decode and encode atoms | `absent` |  |  |  |  |  |  |  |  |  |
| `feat:http-jsonrpc-bindingspec-contract-001` | HttpJsonRpcBindingSpec contract | `implemented` |  |  |  |  |  |  |  |  |  |
| `feat:http-rest-bindingspec-contract-001` | HttpRestBindingSpec contract | `implemented` |  |  |  |  |  |  |  |  |  |
| `feat:http-rest-jsonrpc-atom-chains-001` | HTTP REST and JSON-RPC atom chains | `implemented` |  |  |  |  |  |  |  |  |  |
| `feat:http-stream-atom-chains-001` | HTTP stream atom chains | `implemented` |  |  |  |  |  |  |  |  |  |
| `feat:jsonrpc-20-runtime-surface-001` | JSON-RPC 2.0 runtime surface | `partial` |  |  |  |  |  |  |  |  |  |
| `feat:jsonrpc-batch-framing-001` | JSON-RPC batch framing | `partial` |  |  |  |  |  |  |  |  |  |
| `feat:jsonrpc-endpoint-key-001` | Endpoint-keyed JSON-RPC multiplexing | `partial` |  |  |  |  |  |  |  |  |  |
| `feat:jsonrpc-input-validation-before-persistence-001` | JSON-RPC input validation before persistence | `implemented` |  |  |  |  |  |  |  |  |  |
| `feat:jsonrpc-notification-204-projection-001` | JSON-RPC notification 204 projection | `partial` |  |  |  |  |  |  |  |  |  |
| `feat:jsonrpc-persistence-error-sanitization-001` | JSON-RPC persistence exception response sanitization | `implemented` |  |  |  |  |  |  |  |  |  |
| `feat:kernel-bootstrap-plan-parity-001` | Kernel bootstrap and plan idempotence parity | `partial` |  |  |  |  |  |  |  |  |  |
| `feat:kernel-cache-invalidation-contract-001` | Kernel cache invalidation contract | `partial` |  |  |  |  |  |  |  |  |  |
| `feat:kernelplan-dispatch-ownership-001` | KernelPlan and atoms own transport lookup and matching | `partial` |  |  |  |  |  |  |  |  |  |
| `feat:kernelz-mount-surface-001` | Kernelz mount surface | `partial` |  |  |  |  |  |  |  |  |  |
| `feat:kernelz-uix-surface-001` | Kernelz UIX surface | `absent` |  |  |  |  |  |  |  |  |  |
| `feat:lifespan-runtime-chain-001` | Lifespan runtime chain | `implemented` |  |  |  |  |  |  |  |  |  |
| `feat:message-datagram-runtime-families-001` | Message and datagram runtime families | `absent` |  |  |  |  |  |  |  |  |  |
| `feat:mutualtls-security-docs-runtime-alignment` | Mutual TLS security docs/runtime alignment | `implemented` |  |  |  |  |  |  |  |  |  |
| `feat:operator-sse-event-stream-surface-001` | WHATWG SSE event-stream operator surface | `implemented` |  |  |  |  |  |  |  |  |  |
| `feat:operator-streaming-response-surface-001` | Streaming response operator surface | `implemented` |  |  |  |  |  |  |  |  |  |
| `feat:operator-websocket-route-surface-001` | WebSocket route operator surface | `implemented` |  |  |  |  |  |  |  |  |  |
| `feat:phase-tree-error-branches-001` | Phase tree error branches | `absent` |  |  |  |  |  |  |  |  |  |
| `feat:post-emit-completion-fence-compilation-001` | POST_EMIT completion fence compilation | `absent` |  |  |  |  |  |  |  |  |  |
| `feat:protocol-anchor-ordering-parity-001` | Protocol anchor ordering parity | `absent` |  |  |  |  |  |  |  |  |  |
| `feat:protocol-fused-segments-001` | Protocol fused segments | `absent` |  |  |  |  |  |  |  |  |  |
| `feat:protocol-phase-tree-plans-001` | Protocol phase tree plans | `implemented` |  |  |  |  |  |  |  |  |  |
| `feat:protocol-runtime-boundary-certification-001` | Protocol runtime boundary certification | `absent` |  |  |  |  |  |  |  |  |  |
| `feat:protocol-runtime-profile-pack-001` | Protocol runtime profile pack | `absent` |  |  |  |  |  |  |  |  |  |
| `feat:protocol-runtime-ssot-feature-granularity-001` | Protocol runtime SSOT feature granularity | `absent` |  |  |  |  |  |  |  |  |  |
| `feat:protocol-runtime-test-evidence-suite-001` | Protocol runtime test evidence suite | `absent` |  |  |  |  |  |  |  |  |  |
| `feat:python-asgi-boundary-evidence-001` | Python ASGI boundary evidence | `absent` |  |  |  |  |  |  |  |  |  |
| `feat:python-direct-runtime-microbench-001` | Python direct runtime microbenchmark lane | `absent` |  |  |  |  |  |  |  |  |  |
| `feat:python-runtime-ddl-initialization-boundary-001` | Python runtime DDL initialization boundary | `absent` |  |  |  |  |  |  |  |  |  |
| `feat:python-runtime-performance-baseline-001` | Python executor benchmark baseline | `absent` |  |  |  |  |  |  |  |  |  |
| `feat:rest-create-success-status-001` | REST create success status projection | `partial` |  |  |  |  |  |  |  |  |  |
| `feat:rust-asgi-boundary-evidence-001` | Rust executor under Python ASGI boundary evidence | `absent` |  |  |  |  |  |  |  |  |  |
| `feat:rust-direct-runtime-microbench-001` | Rust direct runtime microbenchmark lane | `absent` |  |  |  |  |  |  |  |  |  |
| `feat:rust-protocol-plan-parity-001` | Rust protocol plan parity | `absent` |  |  |  |  |  |  |  |  |  |
| `feat:rust-runtime-ddl-initialization-boundary-001` | Rust runtime DDL initialization boundary | `absent` |  |  |  |  |  |  |  |  |  |
| `feat:rust-runtime-performance-baseline-001` | Rust executor benchmark baseline | `absent` |  |  |  |  |  |  |  |  |  |
| `feat:sse-event-framing-001` | SSE event framing | `implemented` |  |  |  |  |  |  |  |  |  |
| `feat:sse-lazy-iterator-runtime-001` | SSE lazy iterator runtime | `implemented` |  |  |  |  |  |  |  |  |  |
| `feat:sse-session-message-stream-chains-001` | SSE session message stream chains | `implemented` |  |  |  |  |  |  |  |  |  |
| `feat:static-file-runtime-chain-001` | Static file runtime chain | `implemented` |  |  |  |  |  |  |  |  |  |
| `feat:subevent-transaction-units-001` | Subevent transaction units | `implemented` |  |  |  |  |  |  |  |  |  |
| `feat:transport-accept-emit-close-atoms-001` | Transport accept emit close atoms | `absent` |  |  |  |  |  |  |  |  |  |
| `feat:transport-bypass-removal-001` | Remove non-conforming transport bypasses | `partial` |  |  |  |  |  |  |  |  |  |
| `feat:transport-dispatch-governance-001` | Transport-dispatch governance track setup | `partial` |  |  |  |  |  |  |  |  |  |
| `feat:transport-event-registry-001` | Transport event registry | `absent` |  |  |  |  |  |  |  |  |  |
| `feat:uvicorn-protocol-mode-runtime-parity-001` | Uvicorn protocol-mode runtime parity | `partial` |  |  |  |  |  |  |  |  |  |
| `feat:uvicorn-rest-rpc-semantic-parity-001` | Uvicorn REST and JSON-RPC semantic parity | `partial` |  |  |  |  |  |  |  |  |  |
| `feat:websocket-concrete-runtime-class-001` | WebSocket concrete runtime class | `implemented` |  |  |  |  |  |  |  |  |  |
| `feat:websocket-wss-atom-chains-001` | WebSocket and WSS atom chains | `implemented` |  |  |  |  |  |  |  |  |  |
| `feat:webtransport-bindingspec-contract-001` | WebTransportBindingSpec contract | `implemented` |  |  |  |  |  |  |  |  |  |
| `feat:webtransport-transport-events-001` | WebTransport transport events | `implemented` |  |  |  |  |  |  |  |  |  |
| `feat:yield-iterator-producer-001` | Yield iterator producer | `implemented` |  |  |  |  |  |  |  |  |  |

## SPEC Matrix

Highlighted SPECs appear first, followed by any additional SPECs directly declared by the selected features.

| feature_id | title | implementation_status | spc:1000 | spc:2072 | spc:2087 | spc:2089 | spc:2090 | spc:2092 | spc:2105 | spc:2106 | spc:2107 | spc:2108 | spc:2110 | spc:2113 | spc:2138 | spc:2140 | spc:0614 | spc:2011 | spc:2012 | spc:2013 | spc:2014 | spc:2015 | spc:2016 | spc:2018 | spc:2020 | spc:2021 | spc:2024 | spc:2025 | spc:2041 | spc:2045 | spc:2055 | spc:2056 | spc:2058 | spc:2070 | spc:2071 | spc:2084 | spc:2085 | spc:2086 | spc:2088 | spc:2093 | spc:2097 | spc:2098 | spc:2099 | spc:2100 | spc:2101 | spc:2102 | spc:2103 | spc:2104 | spc:2109 | spc:2114 | spc:2115 | spc:2117 | spc:2119 | spc:2142 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `feat:anon-access-rest-status-parity-001` | Anonymous access and REST create status parity | `implemented` |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:app-framed-message-codec-runtime-001` | App-framed message codec runtime | `absent` |  |  |  |  |  |  |  |  | X | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  | X |
| `feat:atom-parity-dep-security-001` | Atom parity dep security | `implemented` |  |  |  |  | X | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:atom-parity-egress-asgi-send-001` | Atom parity egress asgi_send | `implemented` |  |  |  |  | X | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:atom-parity-egress-to-transport-response-001` | Atom parity egress to_transport_response | `implemented` |  |  |  |  | X | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:atom-parity-ingress-transport-extract-001` | Atom parity ingress transport_extract | `implemented` |  |  |  |  | X | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:atom-parity-resolve-assemble-001` | Atom parity resolve assemble | `implemented` |  |  |  |  | X | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:atom-parity-response-error-to-transport-001` | Atom parity response error_to_transport | `implemented` |  |  |  |  | X | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:atom-parity-sys-handler-aggregate-001` | Atom parity sys handler_aggregate | `implemented` |  |  |  |  | X | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:binding-driven-ingress-001` | Binding-driven REST and JSON-RPC ingress materialization | `partial` |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:binding-subevent-phase-atom-legality-matrix-001` | Binding subevent phase atom legality matrix | `absent` |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  | X |
| `feat:bindingspec-event-subevent-schema-001` | BindingSpec event and subevent schema | `implemented` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X | X |  |  |  |  |  |  |  |  |  | X |
| `feat:bindingspec-kernelplan-protocol-compilation-001` | BindingSpec KernelPlan protocol compilation | `implemented` |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  | X | X |  |  |  |  | X |  |  |  |
| `feat:canonical-ingress-route-phase-cleanup-001` | Canonical INGRESS_ROUTE phase cleanup | `implemented` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  | X |
| `feat:derived-runtime-subevent-taxonomy-001` | Derived runtime subevent taxonomy | `absent` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X | X |  |  |  |  |  |  |  |  |  |  | X |
| `feat:dispatch-exchange-family-subevent-atoms-001` | Dispatch exchange family subevent atoms | `absent` |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  | X |
| `feat:eventful-channel-state-metadata-001` | Eventful channel state metadata | `implemented` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  | X |  |  | X |  |  |  |  |  |  | X |
| `feat:eventkey-hook-bucket-compilation-001` | EventKey hook bucket compilation | `implemented` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X | X | X |
| `feat:eventstreamresponse-concrete-sse-class-001` | EventStreamResponse concrete SSE class | `implemented` |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:executor-dispatch-removal-001` | Executors do not perform transport matching | `partial` |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:framing-decode-encode-atoms-001` | Framing decode and encode atoms | `absent` |  |  |  |  |  |  | X | X | X | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  | X |
| `feat:http-jsonrpc-bindingspec-contract-001` | HttpJsonRpcBindingSpec contract | `implemented` |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:http-rest-bindingspec-contract-001` | HttpRestBindingSpec contract | `implemented` |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:http-rest-jsonrpc-atom-chains-001` | HTTP REST and JSON-RPC atom chains | `implemented` |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X | X |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:http-stream-atom-chains-001` | HTTP stream atom chains | `implemented` |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X | X |  |  |  |  |  |  |
| `feat:jsonrpc-20-runtime-surface-001` | JSON-RPC 2.0 runtime surface | `partial` |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:jsonrpc-batch-framing-001` | JSON-RPC batch framing | `partial` |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:jsonrpc-endpoint-key-001` | Endpoint-keyed JSON-RPC multiplexing | `partial` |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:jsonrpc-input-validation-before-persistence-001` | JSON-RPC input validation before persistence | `implemented` |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  | X |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:jsonrpc-notification-204-projection-001` | JSON-RPC notification 204 projection | `partial` |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:jsonrpc-persistence-error-sanitization-001` | JSON-RPC persistence exception response sanitization | `implemented` |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:kernel-bootstrap-plan-parity-001` | Kernel bootstrap and plan idempotence parity | `partial` |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:kernel-cache-invalidation-contract-001` | Kernel cache invalidation contract | `partial` |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:kernelplan-dispatch-ownership-001` | KernelPlan and atoms own transport lookup and matching | `partial` |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:kernelz-mount-surface-001` | Kernelz mount surface | `partial` |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:kernelz-uix-surface-001` | Kernelz UIX surface | `absent` |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:lifespan-runtime-chain-001` | Lifespan runtime chain | `implemented` |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  | X |  |  |  |  |  |  |  |  |  |  |
| `feat:message-datagram-runtime-families-001` | Message and datagram runtime families | `absent` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  | X | X |  |  |  |  |  |  |  |  |  |  | X |
| `feat:mutualtls-security-docs-runtime-alignment` | Mutual TLS security docs/runtime alignment | `implemented` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:operator-sse-event-stream-surface-001` | WHATWG SSE event-stream operator surface | `implemented` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:operator-streaming-response-surface-001` | Streaming response operator surface | `implemented` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:operator-websocket-route-surface-001` | WebSocket route operator surface | `implemented` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:phase-tree-error-branches-001` | Phase tree error branches | `absent` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X | X |  |  |  | X |  |  |  |
| `feat:post-emit-completion-fence-compilation-001` | POST_EMIT completion fence compilation | `absent` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  | X | X |  |  |  |  |  |  |  | X |
| `feat:protocol-anchor-ordering-parity-001` | Protocol anchor ordering parity | `absent` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  | X | X |  |  | X |
| `feat:protocol-fused-segments-001` | Protocol fused segments | `absent` |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X | X |  |  |  |  |  |  |  | X |
| `feat:protocol-phase-tree-plans-001` | Protocol phase tree plans | `implemented` |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  | X |  |  | X |
| `feat:protocol-runtime-boundary-certification-001` | Protocol runtime boundary certification | `absent` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  | X |  |  |  |  |  |  |  |  |  | X |  |  |  |  |
| `feat:protocol-runtime-profile-pack-001` | Protocol runtime profile pack | `absent` |  |  |  |  |  |  |  |  |  |  |  | X |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |
| `feat:protocol-runtime-ssot-feature-granularity-001` | Protocol runtime SSOT feature granularity | `absent` |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X | X |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |
| `feat:protocol-runtime-test-evidence-suite-001` | Protocol runtime test evidence suite | `absent` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X | X |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |
| `feat:python-asgi-boundary-evidence-001` | Python ASGI boundary evidence | `absent` |  |  |  | X | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:python-direct-runtime-microbench-001` | Python direct runtime microbenchmark lane | `absent` |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:python-runtime-ddl-initialization-boundary-001` | Python runtime DDL initialization boundary | `absent` |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:python-runtime-performance-baseline-001` | Python executor benchmark baseline | `absent` |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:rest-create-success-status-001` | REST create success status projection | `partial` |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:rust-asgi-boundary-evidence-001` | Rust executor under Python ASGI boundary evidence | `absent` |  |  |  | X | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:rust-direct-runtime-microbench-001` | Rust direct runtime microbenchmark lane | `absent` |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:rust-protocol-plan-parity-001` | Rust protocol plan parity | `absent` |  |  |  |  | X | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |
| `feat:rust-runtime-ddl-initialization-boundary-001` | Rust runtime DDL initialization boundary | `absent` |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:rust-runtime-performance-baseline-001` | Rust executor benchmark baseline | `absent` |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:sse-event-framing-001` | SSE event framing | `implemented` |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:sse-lazy-iterator-runtime-001` | SSE lazy iterator runtime | `implemented` |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |
| `feat:sse-session-message-stream-chains-001` | SSE session message stream chains | `implemented` |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X | X |  |  |  |  |  |  |
| `feat:static-file-runtime-chain-001` | Static file runtime chain | `implemented` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  | X |  |  |  |  | X |  |  |  |  |  |
| `feat:subevent-transaction-units-001` | Subevent transaction units | `implemented` |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  | X |  |  |  |  |  |  | X |
| `feat:transport-accept-emit-close-atoms-001` | Transport accept emit close atoms | `absent` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  | X |  |  |  |  |  |  |  |  | X |
| `feat:transport-bypass-removal-001` | Remove non-conforming transport bypasses | `partial` |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  | X |  |  |  |  |  |  | X | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:transport-dispatch-governance-001` | Transport-dispatch governance track setup | `partial` |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  | X | X | X | X |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:transport-event-registry-001` | Transport event registry | `absent` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  | X |  |  |  |  |  |  |  |  |  | X |
| `feat:uvicorn-protocol-mode-runtime-parity-001` | Uvicorn protocol-mode runtime parity | `partial` |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:uvicorn-rest-rpc-semantic-parity-001` | Uvicorn REST and JSON-RPC semantic parity | `partial` |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:websocket-concrete-runtime-class-001` | WebSocket concrete runtime class | `implemented` |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:websocket-wss-atom-chains-001` | WebSocket and WSS atom chains | `implemented` |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  | X |  |  |  |  |  |  |  |
| `feat:webtransport-bindingspec-contract-001` | WebTransportBindingSpec contract | `implemented` |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| `feat:webtransport-transport-events-001` | WebTransport transport events | `implemented` |  |  |  |  |  |  |  |  |  | X |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X |  |  | X |  |  |  |  |  |  |  |  |  | X |
| `feat:yield-iterator-producer-001` | Yield iterator producer | `implemented` |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | X | X |  |  |  |  |  | X |

## Legend

### Highlighted ADRs/SPECs

| ID | Title |
|---|---|
| `adr:1003` | ADR-0003 - Spec-First Authoritative Spec Layer |
| `adr:1008` | ADR-0008 - Atom Catalog and Atom Legality |
| `adr:1016` | ADR-0016 - Kernel Plan Compilation, Packing, Fusion, and Compaction |
| `adr:1024` | ADR-0024 - Runtime Family Model |
| `adr:1052` | tigrbl_core._spec Layer Nature and Authority |
| `adr:1088` | Python/Rust Atom And KernelPlan Parity Certification |
| `adr:1100` | Protocol KernelPlan compilation boundary |
| `adr:1120` | Byte-Oriented Runtime Execution Principles |
| `adr:1121` | Compiled Kernel Plan And Atom Dispatch Layout Boundary |
| `spc:1000` | AppSpec and RouterSpec composition contract |
| `spc:2072` | Mapping plan compilation contract |
| `spc:2087` | Runtime engine session and transaction contract |
| `spc:2089` | Python/Rust request envelope and ASGI boundary contract |
| `spc:2090` | Runtime parity lane governance |
| `spc:2092` | Atom Parity Contract And Evidence Schema |
| `spc:2105` | HTTP REST And JSON-RPC Atom Chain Contract |
| `spc:2106` | HTTP Stream And SSE Atom Chain Contract |
| `spc:2107` | WebSocket And WSS Atom Chain Contract |
| `spc:2108` | WebTransport Atom Chain Contract |
| `spc:2110` | Lifespan Atom Chain Contract |
| `spc:2113` | Binding Subevent Phase Atom Legality Matrix |
| `spc:2138` | Compiled Kernel Plan Packed Layout Contract |
| `spc:2140` | Runtime Execution Conformance And Fuzz Contract |

### Additional Declared ADRs/SPECs

| ID | Title |
|---|---|
| `spc:0614` | Profile evaluation and boundary resolution |
| `spc:2011` | AppSpec, Harness, and Uvicorn Parity |
| `spc:2012` | Status, Auth, and Error Parity |
| `spc:2013` | Transport Ingress Single Dispatch Flow |
| `spc:2014` | Binding-Driven REST and JSON-RPC Materialization |
| `spc:2015` | Endpoint-Keyed JSON-RPC Bindings |
| `spc:2016` | Core Default Endpoint Mappings |
| `spc:2018` | Kernel priming and OpView cache lifecycle |
| `spc:2020` | Operator-surface framing and multipart semantics |
| `spc:2021` | Diagnostics endpoint contracts |
| `spc:2024` | Canonical Transport Routing Tuple and KernelPlan Index Contract |
| `spc:2025` | tigrbl_core._spec Private and Public Export Surface |
| `spc:2041` | Concrete response type surface |
| `spc:2045` | Supported server runner surface |
| `spc:2055` | Canonical transport, exchange, family, and subevent mapping |
| `spc:2056` | Phase-chain projection and emission-completion contract |
| `spc:2058` | Support-level matrix for eventful surfaces |
| `spc:2070` | Transport bypass removal contract |
| `spc:2071` | Mapping dispatch convergence contract |
| `spc:2084` | Tool, test, evidence, and gate taxonomy |
| `spc:2085` | Boundary-scoped test selection and status synchronization |
| `spc:2086` | Runtime DDL and schema readiness lifecycle contract |
| `spc:2088` | Python/Rust runtime performance evidence contract |
| `spc:2093` | Fully Paritable Suite Certification Boundary |
| `spc:2097` | Transport Event Registry Contract |
| `spc:2098` | Derived Runtime Subevent Taxonomy |
| `spc:2099` | BindingSpec Event And Subevent Projection Contract |
| `spc:2100` | Scope Schema Contract |
| `spc:2101` | Kernel Anchor Extension Contract |
| `spc:2102` | Protocol Phase Tree Contract |
| `spc:2103` | Loop Region Contract |
| `spc:2104` | Yield Iterator Producer Contract |
| `spc:2109` | Static File Atom Chain Contract |
| `spc:2114` | Protocol Executor Parity Evidence Contract |
| `spc:2115` | Typed Ok/Err Edge And ErrorCtx Contract |
| `spc:2117` | EventKey And Bit-Coded Dispatch Contract |
| `spc:2119` | Subevent Handler Contract |
| `spc:2142` | XFail Closure Boundary And Proof Contract |
