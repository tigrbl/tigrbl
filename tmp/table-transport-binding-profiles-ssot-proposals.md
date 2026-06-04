# Table Transport Binding Profiles SSOT Proposal Matrix

This temporary note proposes ADRs, SPECs, features, and tests related to
`docs/proposals/table-transport-binding-profiles.md`.

The source proposal is still a draft. The identifiers below are proposed slugs
only; they are not registered SSOT entities.

## Proposal Scope

The table transport binding profile proposal defines author-facing table presets
that lower into existing canonical operation targets, binding specs, docs
projection, and runtime exposure policy.

The core design split is:

- canon op selection: which operation verbs are active
- default op bindings: which bindings apply to selected ops
- per-op bindings: which bindings apply to specific ops
- documentation exposure: which generated bindings appear in docs
- runtime exposure: which generated bindings are mounted on network or ASGI surfaces

The proposal should stay explicit that storage, operation family, protocol
binding, docs projection, and network exposure are separate concerns.

## Proposed ADRs

| ADR | Decision | Rationale |
|---|---|---|
| `adr:table-transport-binding-profiles` | Table classes may declare operation-family and transport-binding intent through governed profiles. | Gives users explicit table presets without conflating table storage with transport exposure. |
| `adr:table-profile-axes-are-separate` | Canon op selection, default bindings, per-op bindings, docs exposure, and runtime exposure are separate axes. | Prevents vague config such as `binding_profiles=("jsonrpc",)` from implying too much. |
| `adr:abstract-table-profiles-do-not-mount-transports` | Abstract table profiles such as `CrudTable` and `RealtimeTable` select op-family intent but do not directly mount bindings. | Keeps abstract presets reusable as mixin-style intent. |
| `adr:explicit-opspec-bindings-override-table-defaults` | Explicit `OpSpec.bindings` override table profile defaults. | Preserves local operation authority and avoids broad table defaults overriding intentional op-specific bindings. |
| `adr:docs-exposure-is-not-network-exposure` | Docs exposure and runtime/network exposure are independent. | Allows internal/docs-only/ASGI-only surfaces without publishing public network routes. |
| `adr:asgi-transport-is-exposure-mode-not-table-class` | `ASGITransport` is an in-process exposure/testing mode, not a table subclass. | Prevents an implementation/client mode from becoming a semantic table protocol. |
| `adr:binding-profile-generation-fails-closed` | Generated table bindings must validate op-to-binding compatibility before materialization. | Prevents invalid table presets from silently creating unsupported routes or transports. |
| `adr:webtransport-datagram-profile-is-datagram-specific` | `WebTransportDatagramTable` maps only datagram-suitable operations by default. | Prevents datagram-specific behavior from being projected onto REST, SSE, or request/response semantics. |

## Proposed SPECs

| SPEC | Scope | Required content |
|---|---|---|
| `spc:table-profile-axis-model` | The five-axis model for table profiles. | Canon op selection, blanket default bindings, per-op bindings, docs exposure, runtime exposure, and override rules. |
| `spc:table-class-profile-taxonomy` | Governed table class presets. | `Table`, `CrudTable`, `RestTable`, `JsonRpcTable`, `BulkCrudTable`, `OltpTable`, `OlapTable`, `RealtimeTable`, `StreamTable`, `SseTable`, `EventStreamTable`, `WebSocketTable`, `WebSocketJsonRpcTable`, and WebTransport table variants. |
| `spc:table-profile-op-selection-matrix` | Which canonical ops each table profile selects. | CRUD, query, bulk, OLAP, realtime, file/stream, datagram, checkpoint, and custom behavior. |
| `spc:op-verb-to-default-binding-matrix` | Default-compatible bindings by canonical op. | REST, HTTP JSON-RPC, WS JSON-RPC, HTTP stream, SSE, WS, WebTransport session/stream/datagram compatibility and notes. |
| `spc:table-binding-token-lowering` | Lowering profile tokens to existing binding specs. | `http.rest -> HttpRestBindingSpec`, `ws.jsonrpc -> WsBindingSpec(framing="jsonrpc", subprotocols=("jsonrpc",))`, WebTransport lane token lowering, etc. |
| `spc:table-profile-docs-exposure-policy` | Docs projection policy for generated bindings. | `docs.openapi`, `docs.openrpc`, `docs.declared_surface`, visibility by binding kind, and non-representable transport metadata. |
| `spc:table-profile-runtime-exposure-policy` | Runtime exposure policy. | `network`, `asgi`, `internal`, route/socket/session materialization, and in-process testing behavior. |
| `spc:table-default-binding-compatibility-rules` | Compatibility and override rules. | `DEFAULT_CANON_VERBS`, `__tigrbl_default_bindings__`, `__tigrbl_default_op_bindings__`, explicit `OpSpec.bindings`, validation order, fail-closed behavior. |
| `spc:websocket-jsonrpc-table-profile-contract` | WebSocket JSON-RPC table behavior. | Required `jsonrpc` framing/subprotocol, selected ops, docs projection, runtime exposure, and invalid `ndjson` fallback. |
| `spc:webtransport-table-lane-profile-contract` | WebTransport table variants. | Session, bidi stream, unidi client stream, unidi server stream, datagram profiles, inner framing rules, and op compatibility. |

## Proposed Features

| Feature | Description | Implementation direction |
|---|---|---|
| `feat:table-profile-axis-model` | Add a first-class table profile model with separate axes. | Extend table config/spec normalization to represent op selection, binding defaults, docs exposure, and runtime exposure separately. |
| `feat:default-canon-verbs-table-selection` | Support profile-driven canonical op selection. | Add/normalize `DEFAULT_CANON_VERBS` or equivalent config on table profiles. |
| `feat:table-default-bindings` | Support blanket default bindings for compatible op sets. | Add `__tigrbl_default_bindings__` lowering and compatibility checks. |
| `feat:table-default-op-bindings` | Support per-op default bindings for broad table classes. | Add `__tigrbl_default_op_bindings__` lowering and per-op compatibility checks. |
| `feat:table-profile-class-taxonomy` | Introduce or document governed table profile classes. | Implement importable classes or formal profile names for `CrudTable`, `RestTable`, `JsonRpcTable`, `OltpTable`, realtime/transport variants. |
| `feat:abstract-table-profile-support` | Support abstract operation-family table profiles. | Ensure abstract profiles do not mount transports until mixed with concrete binding profile. |
| `feat:op-binding-compatibility-validation` | Validate generated op/binding combinations before materialization. | Add compile-time checks for default and per-op bindings. |
| `feat:binding-token-lowering` | Lower profile binding tokens to existing `BindingSpec` classes. | Add deterministic lowering helpers for HTTP, WS, WSS, WS JSON-RPC, SSE, stream, and WebTransport lane tokens. |
| `feat:table-docs-exposure-policy` | Separate generated docs projection from runtime exposure. | Add docs policy fields and projection tests for OpenAPI/OpenRPC/declared surface. |
| `feat:table-runtime-exposure-policy` | Separate network, ASGI, and internal materialization. | Add runtime exposure policy and ensure `ASGITransport` remains a mode, not table class. |
| `feat:websocket-jsonrpc-table-profile` | Govern WS/WSS JSON-RPC table defaults. | Generate `WsBindingSpec` with `framing="jsonrpc"` and `subprotocols=("jsonrpc",)`. |
| `feat:webtransport-table-lane-profiles` | Govern WebTransport lane table variants. | Generate `WebTransportBindingSpec` for session, bidi, unidi client, unidi server, and datagram lanes. |
| `feat:custom-op-explicit-binding-only` | Keep `custom` explicit-only. | Reject auto-generated custom ops and require explicit `OpSpec.bindings`. |
| `feat:checkpoint-profile-policy` | Resolve checkpoint's profile scope. | Decide whether checkpoint is universal transport control or realtime-only, then enforce. |

## Proposed Tests

| Test | Valid scenario | Invalid scenario |
|---|---|---|
| `tst:table-profile-axis-model-separates-concerns` | Table profile stores op selection, bindings, docs exposure, and runtime exposure separately. | `binding_profiles=("jsonrpc",)` implicitly enables ops, docs, and network mounting. |
| `tst:crudtable-abstract-selects-ops-without-bindings` | `CrudTable` selects CRUD ops and no default bindings. | `CrudTable` mounts REST/JSON-RPC routes directly. |
| `tst:realtimetable-abstract-selects-ops-without-bindings` | `RealtimeTable` selects realtime ops and no default bindings. | `RealtimeTable` creates WS/WT/SSE bindings without concrete profile. |
| `tst:resttable-lowers-to-http-rest-bindings` | `RestTable` selected CRUD ops lower to `HttpRestBindingSpec`. | `RestTable` generates JSON-RPC bindings. |
| `tst:jsonrpctable-lowers-to-http-jsonrpc-bindings` | `JsonRpcTable` selected CRUD ops lower to `HttpJsonRpcBindingSpec`. | Missing `rpc_method` or REST path is used as RPC identity. |
| `tst:bulkcrudtable-includes-bulk-ops` | `BulkCrudTable` includes CRUD plus bulk ops. | Bulk ops are omitted or bound to incompatible transport. |
| `tst:oltptable-includes-query-and-merge-ops` | `OltpTable` includes `merge`, `count`, `exists`, and bulk ops. | `merge` appears on plain `Table`/`CrudTable` by default. |
| `tst:olaptable-selects-olap-query-ops` | `OlapTable` selects `count`, `exists`, `aggregate`, and `group_by`. | OLAP profile generates CRUD mutation ops by default. |
| `tst:streamtable-op-binding-compatibility` | `StreamTable` binds `tail`, `download`, `append_chunk`, and `checkpoint` to `http.stream`. | `send_datagram` or ordinary CRUD defaults bind to `http.stream` without explicit policy. |
| `tst:ssetable-op-binding-compatibility` | `SseTable` binds `subscribe`, `tail`, and `checkpoint` to `http.sse`. | Upload/download/append_chunk bind to SSE. |
| `tst:websocket-jsonrpc-table-requires-subprotocol` | `WebSocketJsonRpcTable` lowers to `WsBindingSpec(framing="jsonrpc", subprotocols=("jsonrpc",))`. | WS JSON-RPC table omits subprotocol or uses `ndjson` fallback. |
| `tst:webtransport-session-table-selects-session-compatible-ops` | `WebTransportTable` selects `subscribe` and `checkpoint` only by default. | Stream/datagram-only ops bind to session profile. |
| `tst:webtransport-bidi-table-selects-stream-compatible-ops` | Bidi table binds `publish`, `subscribe`, `tail`, `append_chunk`, and `checkpoint`. | `upload`/`download` semantics are ambiguous without explicit lane policy. |
| `tst:webtransport-client-stream-table-selects-upload-ops` | Client stream table binds `upload`, `append_chunk`, and `checkpoint`. | Server-only download/tail bind to client stream. |
| `tst:webtransport-server-stream-table-selects-download-ops` | Server stream table binds `download`, `tail`, and `checkpoint`. | Client-only upload binds to server stream. |
| `tst:webtransport-datagram-table-selects-send-datagram-only` | Datagram table binds only `send_datagram`. | Datagram profile auto-generates CRUD, subscribe, or SSE-like ops. |
| `tst:binding-token-lowering-is-deterministic` | Every profile token lowers to the expected `BindingSpec` shape. | Token lowers differently based on docs/network exposure mode. |
| `tst:explicit-opspec-bindings-override-table-defaults` | Explicit op binding replaces or augments table defaults according to declared policy. | Table default silently overrides explicit op binding. |
| `tst:docs-exposure-does-not-imply-network-mount` | `docs.openrpc` emits docs for JSON-RPC binding without mounting network route when network is disabled. | Docs exposure causes public network route. |
| `tst:network-exposure-does-not-imply-docs-exposure` | Network-mounted binding can be hidden from docs if docs policy excludes it. | Network exposure always appears in OpenAPI/OpenRPC. |
| `tst:asgi-transport-is-not-table-class` | ASGI exposure mode can test generated bindings in-process. | `ASGITransportTable` is accepted as table protocol. |
| `tst:custom-op-remains-explicit-only` | Custom op appears only when explicit `OpSpec` is declared. | Table profile auto-generates `custom`. |
| `tst:checkpoint-profile-policy-is-enforced` | Checkpoint appears only in profiles approved by chosen policy. | Checkpoint silently appears on every profile without accepted rule. |

## Proposed Entity Matrix By Design Axis

| Design axis | ADRs | SPECs | Features | Tests |
|---|---|---|---|---|
| Canon op selection | `adr:table-transport-binding-profiles`; `adr:abstract-table-profiles-do-not-mount-transports` | `spc:table-class-profile-taxonomy`; `spc:table-profile-op-selection-matrix` | `feat:default-canon-verbs-table-selection`; `feat:table-profile-class-taxonomy`; `feat:abstract-table-profile-support` | `tst:crudtable-abstract-selects-ops-without-bindings`; `tst:realtimetable-abstract-selects-ops-without-bindings`; `tst:bulkcrudtable-includes-bulk-ops`; `tst:olaptable-selects-olap-query-ops` |
| Default and per-op bindings | `adr:explicit-opspec-bindings-override-table-defaults`; `adr:binding-profile-generation-fails-closed` | `spc:op-verb-to-default-binding-matrix`; `spc:table-default-binding-compatibility-rules` | `feat:table-default-bindings`; `feat:table-default-op-bindings`; `feat:op-binding-compatibility-validation` | `tst:streamtable-op-binding-compatibility`; `tst:ssetable-op-binding-compatibility`; `tst:explicit-opspec-bindings-override-table-defaults` |
| Binding token lowering | `adr:binding-profile-generation-fails-closed` | `spc:table-binding-token-lowering`; `spc:websocket-jsonrpc-table-profile-contract`; `spc:webtransport-table-lane-profile-contract` | `feat:binding-token-lowering`; `feat:websocket-jsonrpc-table-profile`; `feat:webtransport-table-lane-profiles` | `tst:binding-token-lowering-is-deterministic`; `tst:websocket-jsonrpc-table-requires-subprotocol`; `tst:webtransport-datagram-table-selects-send-datagram-only` |
| Documentation exposure | `adr:docs-exposure-is-not-network-exposure` | `spc:table-profile-docs-exposure-policy` | `feat:table-docs-exposure-policy` | `tst:docs-exposure-does-not-imply-network-mount`; `tst:network-exposure-does-not-imply-docs-exposure` |
| Runtime exposure | `adr:docs-exposure-is-not-network-exposure`; `adr:asgi-transport-is-exposure-mode-not-table-class` | `spc:table-profile-runtime-exposure-policy` | `feat:table-runtime-exposure-policy` | `tst:asgi-transport-is-not-table-class`; `tst:docs-exposure-does-not-imply-network-mount` |
| Open questions closure | `adr:webtransport-datagram-profile-is-datagram-specific` plus future ADRs for alias/checkpoint/security defaults | `spc:webtransport-table-lane-profile-contract`; checkpoint policy SPEC if accepted | `feat:checkpoint-profile-policy`; `feat:custom-op-explicit-binding-only` | `tst:checkpoint-profile-policy-is-enforced`; `tst:custom-op-remains-explicit-only` |

## Proposed Priority Order

| Priority | Work | Reason |
|---|---|---|
| P0 | `adr:table-profile-axes-are-separate`; `spc:table-profile-axis-model`; `feat:table-profile-axis-model`; `tst:table-profile-axis-model-separates-concerns` | This prevents the vague profile config from over-implying operations, docs, and network exposure. |
| P0 | `spc:table-profile-op-selection-matrix`; `feat:default-canon-verbs-table-selection` | Operation selection must be explicit before binding generation. |
| P0 | `spc:op-verb-to-default-binding-matrix`; `feat:op-binding-compatibility-validation` | Binding generation must fail closed before materializing runtime or docs surfaces. |
| P1 | `spc:table-binding-token-lowering`; `feat:binding-token-lowering` | Deterministic lowering connects table presets to existing `BindingSpec` surfaces. |
| P1 | `spc:table-profile-docs-exposure-policy`; `spc:table-profile-runtime-exposure-policy` | Docs and network/ASGI exposure must stay independent. |
| P1 | WebSocket JSON-RPC and WebTransport lane contracts | These are highest-risk transport profiles because framing/lane semantics are easy to overclaim. |
| P2 | Importable table profile classes or aliases | Once semantics are fixed, decide whether classes are concrete API or documented presets. |
| P2 | Checkpoint and EventStream alias decisions | Close open questions after core profile semantics are stable. |

## Notes

- This proposal should reuse existing binding specs instead of creating new
  transport primitives.
- `custom` should remain explicit-only.
- WebSocket JSON-RPC must require `jsonrpc` framing and subprotocol.
- WebTransport datagram should remain datagram-specific by default.
- ASGI exposure is an in-process runtime/testing mode and should not become a
  table class.
