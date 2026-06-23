# Proposal Draft: Table Transport Binding Profiles

Status: proposal draft

This draft is not an accepted ADR, SPEC, feature row, or release claim. It proposes a table taxonomy for making Tigrbl table intent explicit across canonical operation selection, transport binding defaults, documentation projection, and runtime exposure. The current repo already has canonical op targets, concrete operation packs, and protocol binding specs. This proposal names table presets that can lower into those existing surfaces without treating storage, operation family, protocol binding, and network exposure as the same concern.

## Problem

The current `Table` surface is convenient but too implicit when users need to reason about which canonical operations are active and which protocol bindings are generated for those operations.

The vague shape:

```python
table_config = {"binding_profiles": ("jsonrpc",)}
```

does not say whether default canonical operations are active, which operations receive JSON-RPC bindings, whether REST is disabled, whether docs are emitted, or whether the surface is mounted over a network transport. Table configuration should make those decisions explicit.

## Design Axes

This proposal separates five decisions.

| Axis | Question | Proposed configuration role |
| --- | --- | --- |
| Canon op selection | Which canonical op verbs are active on this table? | `DEFAULT_CANON_VERBS` or equivalent table config |
| Default op bindings | Which bindings are applied to every selected op? | `__tigrbl_default_bindings__` |
| Per-op bindings | Which bindings are applied to specific op verbs? | `__tigrbl_default_op_bindings__` |
| Documentation exposure | Which generated bindings are visible in docs payloads? | docs exposure policy |
| Runtime exposure | Are generated bindings mounted on network or ASGI surfaces? | network / ASGI exposure policy |

`__tigrbl_default_bindings__` is a blanket projection rule for the selected canonical verbs. It should be used only when the selected op set is compatible with every default binding. Broader table classes should use `__tigrbl_default_op_bindings__` instead.

## Canonical Ops In Scope

The currently recognized canonical operation targets are:

| Family | Canon ops |
| --- | --- |
| OLTP CRUD | `create`, `read`, `update`, `replace`, `merge`, `delete`, `list`, `clear` |
| OLTP query | `count`, `exists` |
| OLTP bulk | `bulk_create`, `bulk_update`, `bulk_replace`, `bulk_merge`, `bulk_delete` |
| OLAP | `aggregate`, `group_by` |
| Realtime | `publish`, `subscribe`, `tail`, `upload`, `download`, `append_chunk`, `send_datagram`, `checkpoint` |
| Custom | `custom` |

`custom` is a valid operation target but is not auto-generated as a default canonical operation. It should be declared explicitly.

## Proposed Table Classes

The following table classes are proposed as author-facing presets. Abstract rows define op-family intent without directly mounting a transport. Concrete rows select both operations and default bindings.

| Table class | Status | Default bindings | Canon ops selected |
| --- | --- | --- | --- |
| `Table` | concrete default | `http.rest`, `http.jsonrpc` | `create`, `read`, `update`, `replace`, `delete`, `list`, `clear` |
| `CrudTable` | abstract | none | `create`, `read`, `update`, `replace`, `delete`, `list`, `clear` |
| `RestTable` | concrete | `http.rest` | `create`, `read`, `update`, `replace`, `delete`, `list`, `clear` |
| `JsonRpcTable` | concrete | `http.jsonrpc` | `create`, `read`, `update`, `replace`, `delete`, `list`, `clear` |
| `RestBulkCrudTable` | concrete | `http.rest` | `create`, `read`, `update`, `replace`, `delete`, `list`, `bulk_create`, `bulk_update`, `bulk_replace`, `bulk_delete` |
| `JsonRpcBulkCrudTable` | concrete | `http.jsonrpc` | `create`, `read`, `update`, `replace`, `delete`, `list`, `bulk_create`, `bulk_update`, `bulk_replace`, `bulk_delete` |
| `OltpTable` | concrete | `http.rest`, `http.jsonrpc` | `create`, `read`, `update`, `replace`, `merge`, `delete`, `list`, `clear`, `count`, `exists`, `bulk_create`, `bulk_update`, `bulk_replace`, `bulk_merge`, `bulk_delete` |
| `OlapTable` | concrete | `http.rest`, `http.jsonrpc` | `count`, `exists`, `aggregate`, `group_by` |
| `RealtimeTable` | abstract | none | `publish`, `subscribe`, `tail`, `upload`, `download`, `append_chunk`, `send_datagram`, `checkpoint` |
| `StreamTable` | concrete | `http.stream` | `tail`, `download`, `append_chunk`, `checkpoint` |
| `SseTable` | concrete | `http.sse` | `subscribe`, `tail`, `checkpoint` |
| `EventStreamTable` | concrete alias/subclass | `http.sse` | `subscribe`, `tail`, `checkpoint` |
| `WebSocketTable` | concrete | `ws` or `wss` | `publish`, `subscribe`, `tail`, `upload`, `download`, `append_chunk`, `checkpoint` |
| `WebSocketJsonRpcTable` | concrete | `ws` or `wss` with `jsonrpc` framing and `jsonrpc` subprotocol | `create`, `read`, `update`, `replace`, `delete`, `list`, `clear`, `publish`, `subscribe`, `tail`, `checkpoint` |
| `WebTransportTable` | concrete | `webtransport.session` | `subscribe`, `checkpoint` |
| `WebTransportBidiTable` | concrete | `webtransport.bidi_stream` | `publish`, `subscribe`, `tail`, `append_chunk`, `checkpoint` |
| `WebTransportClientStreamTable` | concrete | `webtransport.unidi_client_stream` | `upload`, `append_chunk`, `checkpoint` |
| `WebTransportServerStreamTable` | concrete | `webtransport.unidi_server_stream` | `download`, `tail`, `checkpoint` |
| `WebTransportDatagramTable` | concrete | `webtransport.datagram` | `send_datagram` |

## Table to Op Mapping

### CRUD and OLTP Tables

| Table class | `create` | `read` | `update` | `replace` | `merge` | `delete` | `list` | `clear` | `count` | `exists` | Bulk ops |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Table` | yes | yes | yes | yes | no | yes | yes | yes | no | no | no |
| `CrudTable` | yes | yes | yes | yes | no | yes | yes | yes | no | no | no |
| `RestTable` | yes | yes | yes | yes | no | yes | yes | yes | no | no | no |
| `JsonRpcTable` | yes | yes | yes | yes | no | yes | yes | yes | no | no | no |
| `RestBulkCrudTable` | yes | yes | yes | yes | no | yes | yes | yes | no | no | `bulk_create`, `bulk_update`, `bulk_replace`, `bulk_delete` |
| `JsonRpcBulkCrudTable` | yes | yes | yes | yes | no | yes | yes | yes | no | no | `bulk_create`, `bulk_update`, `bulk_replace`, `bulk_delete` |
| `OltpTable` | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | `bulk_create`, `bulk_update`, `bulk_replace`, `bulk_merge`, `bulk_delete` |

### OLAP Tables

| Table class | `count` | `exists` | `aggregate` | `group_by` |
| --- | --- | --- | --- | --- |
| `OlapTable` | yes | yes | yes | yes |

### Realtime Tables

| Table class | `publish` | `subscribe` | `tail` | `upload` | `download` | `append_chunk` | `send_datagram` | `checkpoint` |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `RealtimeTable` | yes | yes | yes | yes | yes | yes | yes | yes |
| `StreamTable` | no | no | yes | no | yes | yes | no | yes |
| `SseTable` | no | yes | yes | no | no | no | no | yes |
| `EventStreamTable` | no | yes | yes | no | no | no | no | yes |
| `WebSocketTable` | yes | yes | yes | yes | yes | yes | no | yes |
| `WebSocketJsonRpcTable` | yes | yes | yes | no | no | no | no | yes |
| `WebTransportTable` | no | yes | no | no | no | no | no | yes |
| `WebTransportBidiTable` | yes | yes | yes | no | no | yes | no | yes |
| `WebTransportClientStreamTable` | no | no | no | yes | no | yes | no | yes |
| `WebTransportServerStreamTable` | no | no | yes | no | yes | no | no | yes |
| `WebTransportDatagramTable` | no | no | no | no | no | no | yes | no |

## Op Verb to Transport Binding Mapping

This table describes proposed default-compatible bindings by canonical op. Explicit `OpSpec.bindings` should be allowed to override these defaults.

| Canon op | Default-compatible bindings | Notes |
| --- | --- | --- |
| `create` | `http.rest`, `http.jsonrpc`, `ws.jsonrpc` | Unary mutation |
| `read` | `http.rest`, `http.jsonrpc`, `ws.jsonrpc` | Unary member read |
| `update` | `http.rest`, `http.jsonrpc`, `ws.jsonrpc` | Unary member mutation |
| `replace` | `http.rest`, `http.jsonrpc`, `ws.jsonrpc` | Unary member replacement |
| `merge` | `http.rest`, `http.jsonrpc` | Explicit OLTP table only |
| `delete` | `http.rest`, `http.jsonrpc`, `ws.jsonrpc` | Unary member deletion |
| `list` | `http.rest`, `http.jsonrpc`, `ws.jsonrpc` | Unary collection read |
| `clear` | `http.rest`, `http.jsonrpc`, `ws.jsonrpc` | Unary collection deletion |
| `count` | `http.rest`, `http.jsonrpc` | OLTP/OLAP query |
| `exists` | `http.rest`, `http.jsonrpc` | OLTP/OLAP query |
| `bulk_create` | `http.rest`, `http.jsonrpc` | Bulk collection mutation |
| `bulk_update` | `http.rest`, `http.jsonrpc` | Bulk mutation |
| `bulk_replace` | `http.rest`, `http.jsonrpc` | Bulk replacement |
| `bulk_merge` | `http.rest`, `http.jsonrpc` | Bulk upsert-like mutation |
| `bulk_delete` | `http.rest`, `http.jsonrpc` | Bulk deletion |
| `aggregate` | `http.rest`, `http.jsonrpc` | OLAP query |
| `group_by` | `http.rest`, `http.jsonrpc` | OLAP grouped query |
| `publish` | `http.rest`, `http.jsonrpc`, `ws`, `webtransport.bidi_stream` | REST/RPC are control-plane fallback bindings; realtime bindings are primary |
| `subscribe` | `http.sse`, `ws`, `ws.jsonrpc`, `webtransport.session`, `webtransport.bidi_stream` | Long-lived/eventful binding preferred |
| `tail` | `http.stream`, `http.sse`, `ws`, `ws.jsonrpc`, `webtransport.bidi_stream`, `webtransport.unidi_server_stream` | Server-to-client stream shape |
| `upload` | `http.stream`, `ws`, `webtransport.unidi_client_stream` | Client-to-server stream shape |
| `download` | `http.stream`, `ws`, `webtransport.unidi_server_stream` | Server-to-client stream shape |
| `append_chunk` | `http.stream`, `ws`, `webtransport.bidi_stream`, `webtransport.unidi_client_stream` | Chunked client contribution |
| `send_datagram` | `webtransport.datagram` | Datagram-specific; do not default to SSE or ordinary REST |
| `checkpoint` | `http.rest`, `http.jsonrpc`, `http.stream`, `http.sse`, `ws`, `webtransport.session`, `webtransport.bidi_stream`, `webtransport.unidi_client_stream`, `webtransport.unidi_server_stream` | Control/checkpoint op that may accompany multiple transport families |
| `custom` | explicit only | No default binding; must be declared by `OpSpec` |

## Binding Token Lowering

Proposed table tokens should lower to the existing binding specs.

| Proposed token | Binding spec |
| --- | --- |
| `http.rest` | `HttpRestBindingSpec` |
| `https.rest` | `HttpRestBindingSpec` |
| `http.jsonrpc` | `HttpJsonRpcBindingSpec` |
| `https.jsonrpc` | `HttpJsonRpcBindingSpec` |
| `http.stream` | `HttpStreamBindingSpec` |
| `https.stream` | `HttpStreamBindingSpec` |
| `http.sse` | `SseBindingSpec` |
| `https.sse` | `SseBindingSpec` |
| `ws` | `WsBindingSpec` |
| `wss` | `WsBindingSpec` |
| `ws.jsonrpc` | `WsBindingSpec` with `framing="jsonrpc"` and `subprotocols=("jsonrpc",)` |
| `wss.jsonrpc` | `WsBindingSpec` with `framing="jsonrpc"` and `subprotocols=("jsonrpc",)` |
| `webtransport.session` | `WebTransportBindingSpec(profile="session")` |
| `webtransport.bidi_stream` | `WebTransportBindingSpec(profile="bidi_stream")` |
| `webtransport.unidi_client_stream` | `WebTransportBindingSpec(profile="unidi_client_stream")` |
| `webtransport.unidi_server_stream` | `WebTransportBindingSpec(profile="unidi_server_stream")` |
| `webtransport.datagram` | `WebTransportBindingSpec(profile="datagram")` |

## Documentation and Runtime Exposure

Bindings should not automatically imply public network exposure. Generated bindings should pass through a separate exposure policy.

| Exposure | Meaning |
| --- | --- |
| `docs.openapi` | Include REST, HTTP stream, and SSE HTTP surfaces in OpenAPI where representable |
| `docs.openrpc` | Include JSON-RPC method surfaces in OpenRPC |
| `docs.declared_surface` | Include non-OpenAPI/OpenRPC transport metadata for WebSocket and WebTransport |
| `network` | Mount externally reachable routes, sockets, or sessions |
| `asgi` | Expose through the ASGI application for in-process clients and tests |
| `internal` | Materialize handlers and specs without mounting a public surface |

`ASGITransport` should not become a table subclass. It is an in-process client/runtime exposure mode over the ASGI app, not a table protocol.

## Compatibility Rules

1. `DEFAULT_CANON_VERBS` selects active canonical op verbs.
2. `__tigrbl_default_bindings__` applies the same binding set to every selected op.
3. `__tigrbl_default_op_bindings__` applies bindings per op and should be preferred for broad realtime tables.
4. Explicit `OpSpec.bindings` override table defaults.
5. Binding generation must validate op-to-binding compatibility before materializing routes, RPC methods, stream endpoints, socket handlers, or WebTransport lanes.
6. WebSocket JSON-RPC must require `jsonrpc` framing and the `jsonrpc` subprotocol.
7. WebTransport datagram ops must remain datagram-specific; they should not be silently projected onto request-response or SSE surfaces.
8. Docs exposure should be derived from generated bindings, but docs exposure must remain separate from network mounting.

## Open Questions

- Should `CrudTable` and `RealtimeTable` be importable abstract classes or only documented mixin-style base classes?
- Should `EventStreamTable` be a separate class or a public alias for `SseTable`?
- Should `WebSocketJsonRpcTable` include CRUD defaults by default, or should it stay realtime-only unless mixed with `CrudTable`?
- Should `checkpoint` be a universal transport control op or remain limited to explicit realtime table classes?
- Should HTTPS/WSS variants be selected by table class, router/app configuration, or deployment-layer configuration?
