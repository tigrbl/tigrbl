# 04 Idempotency Contract

This section proposes the idempotency contract for operations, transports,
retries, replay, streams, and datagrams.

## Purpose

Idempotency is the rule that duplicate execution or duplicate delivery does not
create wider side effects than declared. It is not a property of HTTP alone and
it is not implied by operation name. Tigrbl must declare idempotency per
operation, per transport framing where needed, and per runtime policy.

## Proposed ADRs

| ADR | Decision | Why it is needed |
|---|---|---|
| `adr:idempotency-is-declared-runtime-semantics` | Idempotency is a declared runtime semantic, not an inferred behavior. | Prevents accidental stability from being certified as guaranteed behavior. |
| `adr:idempotency-keys-govern-unsafe-retry` | Unsafe mutating retries require idempotency keys or equivalent ledgers. | Prevents retry/replay from duplicating side effects. |

## Proposed SPECs

| SPEC | Scope | Required content |
|---|---|---|
| `spc:operation-idempotency-classes` | Classification of operation idempotency. | Classes such as `always_idempotent`, `key_idempotent`, `not_idempotent`, `stream_ledger_idempotent`, `transport_defined`. |
| `spc:idempotency-key-store-contract` | Key storage and lookup semantics. | Key scope, payload hash binding, response replay, expiration, collision handling, and trace fields. |
| `spc:stream-chunk-idempotency-contract` | Stream/chunk dedupe semantics. | Chunk ids, ordering, partial upload/import behavior, abort behavior, and ledger requirements. |
| `spc:datagram-idempotency-boundary` | Datagram duplicate/replay policy. | Datagram ids, best-effort delivery, duplicate handling, ordering absence, and rejection rules. |

## Proposed Features

| Feature | Description | Implementation direction |
|---|---|---|
| `feat:idempotency-classification` | Assign idempotency class to compiled operations. | Derive from op semantics, atom chain, and explicit spec metadata. |
| `feat:idempotency-key-dedupe` | Deduplicate key-backed mutating attempts. | Add key lookup/store atoms and runtime trace evidence. |
| `feat:delete-stable-idempotency` | Declare stable behavior for repeated delete where supported. | Define response/error semantics for already-deleted resources. |
| `feat:stream-chunk-idempotency` | Support idempotency for chunked streams. | Add chunk ledger identity and partial-stream policies. |
| `feat:datagram-idempotency-policy` | Define datagram duplicate/replay policy. | Reject or dedupe datagram effects unless declared by app framing. |

## Proposed Tests

| Test | Valid scenario | Invalid scenario |
|---|---|---|
| `tst:create-idempotency-key-dedupes` | Repeating create with same key and payload returns stored result without duplicate row. | Duplicate row is created. |
| `tst:create-without-key-is-not-retried-after-commit` | Runtime refuses after-commit retry for unkeyed create. | Runtime re-executes committed create. |
| `tst:delete-idempotency-declared-stable` | Repeated delete follows declared stable response behavior. | Repeated delete behavior differs across transports without declaration. |
| `tst:append-chunk-dedupes-by-stream-chunk-id` | Duplicate chunk id is ignored or returns stored chunk result. | Duplicate chunk mutates stream/import twice. |
| `tst:datagram-replay-rejected-without-policy` | Datagram replay fails closed when no dedupe/order policy is declared. | Datagram replay silently creates duplicate effect. |

## Invariants

- Idempotency behavior must be declared before execution.
- Unsafe operations cannot be retried after side effects unless key-backed or ledger-backed.
- Idempotency keys must bind to operation id, payload identity, and scope.
- Stream idempotency needs chunk identity and completion/abort policy.
- Datagram idempotency must account for unordered best-effort delivery.

## Notes

This is tightly coupled to retries and replay. A retry policy that ignores
idempotency is unsafe; a replay policy that ignores idempotency is only audit
replay, not semantic replay.
