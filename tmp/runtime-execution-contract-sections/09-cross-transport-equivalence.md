# 09 Cross-Transport Equivalence

This section proposes a semantic equivalence program for operations bound to
multiple transports.

## Purpose

Cross-transport equivalence does not mean byte-for-byte equality. It means that
the same canonical operation, when validly bound to multiple transports, produces
equivalent semantic effects: normalized result, error meaning, persistence
effect, idempotency behavior, retry/replay policy, and trace shape.

## Proposed ADRs

| ADR | Decision | Why it is needed |
|---|---|---|
| `adr:cross-transport-equivalence-is-semantic-not-bytewise` | Equivalence compares semantic outcomes, not raw wire bytes. | REST, JSON-RPC, WebSocket, streams, and WebTransport have different envelopes. |
| `adr:transport-bindings-require-composable-runtime-plan` | An operation can bind to a transport only when op semantics and transport semantics compose into a complete runtime plan. | Prevents unsupported or underspecified stream/datagram bindings from being treated as valid. |

## Proposed SPECs

| SPEC | Scope | Required content |
|---|---|---|
| `spc:cross-transport-equivalence-corpus` | Golden corpus of operations and valid transport bindings. | CRUD, custom op, error cases, bulk, stream/tail, file transfer, realtime, and datagram cases. |
| `spc:semantic-result-normalization` | Result comparison rules. | Normalized result, error code/class, persistence effect, trace shape, idempotency, and retry/replay fields. |
| `spc:transport-binding-equivalence-rules` | When bindings are equivalent, partial, or not comparable. | Transport families, framing requirements, completion policy, and equivalence exclusions. |
| `spc:stream-create-completion-policy` | Create/update over stream semantics. | Input completion, commit point, abort behavior, chunk ledger, retry/replay policy. |
| `spc:datagram-op-equivalence-boundary` | Datagram operation boundaries. | Operations valid over datagram, required dedupe/order/idempotency policy, and fail-closed cases. |

## Proposed Features

| Feature | Description | Implementation direction |
|---|---|---|
| `feat:cross-transport-equivalence-corpus` | Build golden operation corpus for cross-transport tests. | Add fixture app with canonical ops and declared transport bindings. |
| `feat:rest-jsonrpc-ws-jsonrpc-equivalence` | Prove unary operation equivalence across REST, HTTP JSON-RPC, and WS JSON-RPC. | Compare create/read/update/delete/list and custom op outcomes. |
| `feat:http-stream-op-binding-policy` | Define when HTTP stream can bind to mutating/read operations. | Require completion, abort, chunk, and commit semantics. |
| `feat:webtransport-stream-op-binding-policy` | Define WebTransport stream operation binding rules. | Require lane, stream framing, completion, and retry/replay semantics. |
| `feat:datagram-op-binding-policy` | Define which ops can bind to datagram. | Require best-effort, dedupe, ordering, and idempotency rules or reject. |
| `feat:equivalence-trace-comparison` | Compare trace shape across equivalent transport executions. | Normalize trace events by `op_id`, attempt state, atom ids, and completion semantics. |

## Proposed Tests

| Test | Valid scenario | Invalid scenario |
|---|---|---|
| `tst:rest-jsonrpc-ws-create-equivalence` | REST, HTTP JSON-RPC, and WS JSON-RPC create produce equivalent normalized result and persistence effect. | One transport accepts invalid input or returns different semantic error. |
| `tst:rest-jsonrpc-error-equivalence` | Validation/persistence errors normalize across REST and JSON-RPC. | JSON-RPC hides error or REST emits incompatible error meaning. |
| `tst:http-stream-create-requires-completion-policy` | HTTP stream create commits only under declared completion policy. | Partial stream abort commits without policy. |
| `tst:wt-stream-create-requires-completion-policy` | WebTransport stream create declares input complete and commit point. | WebTransport stream commits on ambiguous chunk boundary. |
| `tst:datagram-create-rejected-without-order-dedupe-policy` | Datagram create is rejected unless app declares order/dedupe/idempotency policy. | Datagram create duplicates side effects. |
| `tst:equivalent-ops-have-equivalent-trace-shape` | Equivalent executions share comparable attempt/atom/completion trace shape. | Trace shape hides missing atom or completion fence. |

## Invariants

- Equivalence is semantic, not bytewise.
- Same canonical `op_id` plus equivalent input should produce equivalent normalized results where binding is declared equivalent.
- Stream and datagram bindings require complete transport semantics before they can be equivalent to unary bindings.
- Unsupported transport bindings must fail closed.
- Equivalence tests must compare result, error, persistence effect, idempotency, retry/replay, and trace.

## Notes

A create operation can use HTTP stream or WebTransport stream, but only with
declared stream framing, input completion, commit, abort, retry, and replay
semantics. Datagram create is not valid by default because datagrams are
unordered and best effort.
