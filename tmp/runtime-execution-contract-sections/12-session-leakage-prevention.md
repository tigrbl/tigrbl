# 12 Session Leakage Prevention

This section proposes isolation rules that prevent state leakage across sessions,
engine sessions, transactions, attempts, app/router/table scopes, and traces.

## Purpose

Leakage prevention protects correctness and security. Runtime state must not move
between clients, sessions, streams, datagrams, operation attempts, engine
sessions, transactions, apps, routers, or tables unless an explicit scoped rule
allows it. This is especially important for long-lived transports and pooled
engine/session resources.

## Proposed ADRs

| ADR | Decision | Why it is needed |
|---|---|---|
| `adr:runtime-state-isolation-by-identity-scope` | Runtime state is isolated by declared identity scope. | Establishes app/router/table/op/attempt/session/engine boundaries. |
| `adr:engine-session-leakage-is-fail-closed` | Engine session reuse without reset or scoped lease is invalid. | Prevents persistence state from leaking between attempts. |
| `adr:cross-session-access-is-invalid` | Cross-session access is rejected unless explicitly governed. | Prevents WebSocket/WebTransport/session state from crossing clients or sessions. |

## Proposed SPECs

| SPEC | Scope | Required content |
|---|---|---|
| `spc:session-isolation-contract` | Client/session/stream/datagram isolation. | Session ownership, close cascade, stream lane immutability, datagram scope, and cross-client rejection. |
| `spc:engine-session-isolation-contract` | Engine session lifecycle and reuse rules. | Lease, checkout, reset, rollback, close, pooling, and contamination checks. |
| `spc:transaction-isolation-contract` | Transaction ownership. | Transaction id, owning engine session, owning attempt, commit/rollback authority, and invalid cross-commit. |
| `spc:app-router-table-state-isolation` | Semantic-scope state boundaries. | App/router/table/operation local state, shared state declarations, and leakage checks. |
| `spc:trace-attribution-isolation` | Trace/qlog attribution isolation. | Required ids, attribution validation, and misattribution handling. |

## Proposed Features

| Feature | Description | Implementation direction |
|---|---|---|
| `feat:no-cross-session-leakage` | Reject events that cross session or client boundaries. | Validate session/client/stream/datagram parentage on receive/send. |
| `feat:no-engine-session-leakage` | Prevent engine session contamination between attempts. | Add engine session lease/reset/rollback checks. |
| `feat:no-transaction-leakage` | Ensure transactions are committed or rolled back only by owning attempt. | Track `transaction_id -> engine_session_id -> attempt_id`. |
| `feat:no-app-router-table-state-leakage` | Prevent semantic-scope state leakage. | Scope state containers and validate cross-scope references. |
| `feat:session-close-cascades-owned-streams` | Closing session closes or invalidates owned streams. | Enforce close cascade in runtime state machine. |
| `feat:attempt-scoped-state-reset` | Clear attempt-scoped runtime state on terminal outcome. | Add terminal-state cleanup and tests. |

## Proposed Tests

| Test | Valid scenario | Invalid scenario |
|---|---|---|
| `tst:wt-stream-session-a-cannot-mutate-session-b` | Session A stream mutates only session A state. | Session A stream mutates session B state. |
| `tst:closed-session-rejects-payload` | Closed session rejects incoming stream/datagram/message payload. | Closed session accepts payload. |
| `tst:stream-id-lane-metadata-change-rejected` | Stream id keeps immutable lane metadata. | Reused stream id changes lane/direction/framing. |
| `tst:engine-session-not-reused-without-reset-or-lease` | Pooled engine session is reset/leased before reuse. | Attempt B sees transaction/session state from attempt A. |
| `tst:transaction-not-committed-by-other-operation` | Owning attempt commits or rolls back its transaction. | Different operation commits transaction. |
| `tst:trace-qlog-attribution-scope-check` | Trace/qlog events validate session and engine-session ids. | Trace/qlog event is attributed to wrong session or engine session. |

## Invariants

- No cross-session leakage.
- No engine-session leakage.
- No transaction leakage.
- No app/router/table state leakage.
- No cross-client access.
- Session close cascades to owned streams.
- Engine session close or rollback clears attempt-scoped state.

## Notes

This feature depends on concrete instance identity. Without parentage ids,
leakage prevention becomes heuristic instead of enforceable.
