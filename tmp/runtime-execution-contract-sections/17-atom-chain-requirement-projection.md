# 17 Atom-Chain Requirement Projection

This section proposes deriving execution requirements from the compiled atom and
hook chain.

## Purpose

Atoms already are capabilities, and the compiled atom/hook chain is the source
of truth for what an operation does. This proposal does not create a parallel
hand-maintained operation capability vector. It derives consequences from the
compiled chain so runtime can reject unsupported combinations early, pack hot
path summaries, classify retry/replay/idempotency, and produce evidence rollups.

## Proposed ADRs

| ADR | Decision | Why it is needed |
|---|---|---|
| `adr:compiled-chain-is-source-of-execution-requirements` | The compiled atom/hook chain is the source of execution requirements. | Prevents drift between atom membership and manually maintained capability vectors. |
| `adr:requirement-projection-is-summary-not-source` | Requirement projection is a derived summary, not the authority. | Allows hot-path and rollup summaries without replacing atom-chain truth. |

## Proposed SPECs

| SPEC | Scope | Required content |
|---|---|---|
| `spc:atom-chain-requirement-projection` | General projection rules. | How to derive requirements from atoms, hooks, phases, transport atoms, and transaction atoms. |
| `spc:transaction-requirement-projection` | Transaction requirements. | Begin/commit/rollback atoms, engine session requirements, transaction ownership, and rejection cases. |
| `spc:channel-family-requirement-projection` | Runtime channel requirements. | Message, stream, datagram, session, send, receive, close, and completion requirements. |
| `spc:idempotency-store-requirement-projection` | Idempotency requirements. | Key lookup/write atoms, key scope, store requirement, and trace preservation. |
| `spc:replay-ledger-requirement-projection` | Replay requirements. | Replay ledger atoms, runtime plan hash compatibility, replay id, and original attempt id. |
| `spc:completion-fence-requirement-projection` | Completion requirements. | Emit atoms, stream close, datagram emit, message send, and completion fence obligations. |

## Proposed Features

| Feature | Description | Implementation direction |
|---|---|---|
| `feat:atom-chain-requirement-projection` | Build derived requirement summary from compiled chain. | Add projection pass after kernel compiles atom/hook chains. |
| `feat:transaction-requirement-from-chain` | Require transaction scope when transaction atoms exist. | Derive engine/session transaction requirements. |
| `feat:channel-requirement-from-chain` | Require channel family support when transport atoms exist. | Derive send/receive/close/datagram/stream requirements. |
| `feat:idempotency-store-requirement-from-chain` | Require idempotency store when idempotency atoms exist. | Connect atom-chain projection to idempotency store availability. |
| `feat:replay-ledger-requirement-from-chain` | Require replay ledger when replay atoms exist. | Connect replay projection to replay identity and plan hash. |
| `feat:projection-hot-path-summary` | Store compact requirement summary in runtime plan. | Add mask/table/metadata for fast rejection without replacing chain. |

## Proposed Tests

| Test | Valid scenario | Invalid scenario |
|---|---|---|
| `tst:transaction-atoms-require-transaction-scope` | Chain with begin/commit atoms requires transaction-capable scope. | Runtime executes commit atom with no transaction support. |
| `tst:datagram-emit-atom-requires-datagram-channel` | Chain with datagram emit requires datagram channel adapter. | Runtime starts execution then discovers no datagram send. |
| `tst:idempotency-atoms-require-idempotency-store` | Idempotency lookup/write atoms require store and key identity. | Idempotency atom runs with no store. |
| `tst:replay-atoms-require-replay-ledger-and-plan-hash` | Replay atoms require ledger and compatible runtime plan id/hash. | Replay proceeds without ledger or plan compatibility check. |
| `tst:streaming-emit-atoms-require-completion-fence` | Stream emit atoms require completion fence semantics. | Stream emit completes without fence metadata. |
| `tst:projection-cannot-contradict-compiled-chain` | Projection summary matches compiled atom/hook chain. | Projection claims requirement absent while chain contains requiring atom. |

## Invariants

- Requirements are derived from compiled atom/hook chain.
- No parallel capability registry for operation atom membership.
- Projection cannot contradict the compiled chain.
- Projection is a summary, not the source of truth.
- Fast rejection and rollup summaries must drill back to compiled chain evidence.

## Notes

This feature is useful because it derives consequences, not membership. It can
say "this compiled chain needs transaction support, datagram send, idempotency
store, replay ledger, and completion fence" without maintaining a separate list
of what atoms belong to the operation.
