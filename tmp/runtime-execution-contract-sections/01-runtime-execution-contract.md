# 01 Runtime Execution Contract

This section proposes the first governing slice for a formal Tigrbl runtime
execution contract. It defines the canonical lifecycle model that `tigrbl_kernel`
plans and `tigrbl_runtime` enforces.

## Purpose

Tigrbl needs one published state model for operation attempts, runtime channels,
engine sessions, transactions, completion fences, retries, replay, and traces.
Without this, runtime behavior can be correct locally but uncertifiable globally:
REST, JSON-RPC, WebSocket, streams, WebTransport, and datagrams can drift into
different meanings for "received", "executed", "committed", "emitted", and
"completed".

## Proposed ADRs

| ADR | Decision | Why it is needed |
|---|---|---|
| `adr:runtime-execution-contract-authority` | The runtime execution contract is the authoritative interpretation of operation lifecycle semantics. | Prevents lifecycle rules from being scattered across protocol adapters, tests, and docs. |
| `adr:kernel-runtime-state-ownership` | `tigrbl_kernel` owns state-machine shape and legality; `tigrbl_runtime` owns concrete state transitions and side effects. | Keeps planning and execution separate while still making runtime behavior provable. |

## Proposed SPECs

| SPEC | Scope | Required content |
|---|---|---|
| `spc:runtime-execution-state-machine` | Canonical runtime state table. | Runtime object types, legal states, legal transitions, terminal states, fail-closed states, and transition metadata. |
| `spc:operation-attempt-lifecycle` | One operation attempt from receipt to terminal outcome. | `received`, `resolved`, `planned`, `executing`, `committed`, `emitted`, `completed`, `failed`, `aborted`, and parent ids. |
| `spc:engine-session-transaction-lifecycle` | Engine session and transaction state. | Engine session acquisition, transaction begin, flush, commit, rollback, close, lease/reset rules, and error handling. |
| `spc:completion-fence-semantics` | Meaning of runtime completion fences. | Difference between runtime send completion, emit completion, stream close, peer delivery, and failure. |

## Proposed Features

| Feature | Description | Implementation direction |
|---|---|---|
| `feat:runtime-execution-contract` | Publish and enforce the common runtime execution lifecycle. | Add kernel-level lifecycle definitions and runtime validators. |
| `feat:operation-attempt-state-machine` | Track each operation attempt through legal state transitions. | Add attempt state metadata to runtime context and trace. |
| `feat:engine-session-transaction-state-machine` | Track engine sessions and transactions as first-class lifecycle objects. | Wrap engine/session acquisition and transaction atoms with state checks. |
| `feat:runtime-completion-fence-contract` | Make response, stream, datagram, and message completion semantics explicit. | Normalize completion fence metadata across protocol adapters. |

## Proposed Tests

| Test | Valid scenario | Invalid scenario |
|---|---|---|
| `tst:runtime-execution-state-machine-valid-transitions` | REST create follows `received -> resolved -> executing -> committed -> emitted -> completed`. | None for this test. |
| `tst:runtime-execution-state-machine-invalid-transitions` | None for this test. | Datagram attempts to transition through `stream.close`; closed session receives payload. |
| `tst:operation-attempt-side-effect-parentage` | Each persistence side effect links to one `attempt_id`. | Side effect is emitted without an operation attempt. |
| `tst:engine-session-transaction-lifecycle-contract` | Engine session starts, transaction commits, and session closes under one attempt. | Transaction from one attempt is committed by another attempt. |
| `tst:completion-fence-observed-before-emitted-result` | Stream/message/datagram result reports completion fence before terminal success. | Runtime claims peer delivery when it only observed local send completion. |

## Invariants

- No undocumented lifecycle transition is valid.
- Every emitted result has a prior resolved operation.
- Every side effect belongs to one operation attempt id.
- Engine session and transaction state cannot outlive or cross their scoped lease.
- Completion success must state what completed: runtime send, stream close, peer ack, or application ack.

## Notes

This should be the first implementation slice because retry, replay, idempotency,
trace/qlog correlation, transport guarantees, and rollups all depend on a stable
runtime state model.
