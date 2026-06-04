# 06 Retry Policy

This section proposes the retry policy contract for operation attempts, transport
failures, engine failures, idempotency, stream ledgers, and webhook delivery.

## Purpose

Retry behavior must be derived from runtime semantics, not from generic optimism.
Some retries are safe, some are safe only before commit, some require an
idempotency key, and some require a stream/chunk ledger. The goal is to prevent
retry from widening side effects while still allowing fast recovery from
transient failures.

## Proposed ADRs

| ADR | Decision | Why it is needed |
|---|---|---|
| `adr:retry-safety-derived-from-runtime-semantics` | Retry safety is derived from operation lifecycle, atom chain, transport delivery, transaction state, and idempotency. | Prevents retry rules from being hand-waved per adapter or handler. |
| `adr:retry-cannot-widen-side-effects` | Retry must not create more side effects than the original declared attempt. | Establishes the fail-closed rule for mutating operations. |

## Proposed SPECs

| SPEC | Scope | Required content |
|---|---|---|
| `spc:retry-classification-contract` | Retry classes for operations and attempts. | Classes such as `retry_safe`, `retry_before_commit`, `retry_with_idempotency_key`, `retry_with_ledger`, and `never_retry`. |
| `spc:retry-attempt-parentage` | Parentage between original attempts and retry attempts. | Required `attempt_id`, `original_attempt_id`, retry sequence, cause, and terminal state fields. |
| `spc:post-commit-retry-policy` | Rules after commit or side-effect completion. | When retry is rejected, when idempotency key replay is allowed, and when audit-only replay is required. |
| `spc:stream-retry-chunk-ledger-contract` | Retry safety for streamed input/output. | Chunk identity, chunk ordering, partial completion, abort handling, and ledger requirements. |

## Proposed Features

| Feature | Description | Implementation direction |
|---|---|---|
| `feat:retry-policy-classification` | Compile retry class into operation/runtime plan metadata. | Derive from op semantics, atom-chain projection, idempotency policy, and transport family. |
| `feat:retry-parentage` | Preserve retry attempt identity and parentage. | Add retry metadata to runtime context, trace, and rollup. |
| `feat:read-retry-safe` | Mark read-only deterministic attempts as retry-safe where engine/session state permits. | Add tests for transient failure retry without mutation. |
| `feat:create-retry-with-idempotency-key` | Allow create retry after side-effect risk only with idempotency key. | Connect idempotency key store to retry handling. |
| `feat:stream-retry-chunk-ledger` | Allow stream retry only with chunk ledger and completion policy. | Add chunk ledger metadata for HTTP stream and WebTransport stream. |
| `feat:webhook-idempotent-retry` | Make webhook retry use explicit idempotency identity. | Align webhook delivery retry with idempotency and trace contracts. |

## Proposed Tests

| Test | Valid scenario | Invalid scenario |
|---|---|---|
| `tst:read-retry-after-transient-failure` | Read attempt retries after transient transport failure and returns same normalized result. | Retry mutates state or loses original attempt parentage. |
| `tst:create-retry-before-commit-only` | Create retries before commit when runtime can prove no side effect happened. | Runtime retries after commit without idempotency key. |
| `tst:create-retry-after-commit-requires-idempotency-key` | Create after commit uses idempotency key to return stored result. | Duplicate row is created on retry. |
| `tst:partial-stream-import-retry-requires-chunk-ledger` | Partial stream retry is allowed only when chunk ledger exists. | Runtime replays partial stream without ledger. |
| `tst:retry-links-to-original-attempt-id` | Retry trace records `original_attempt_id` and retry sequence. | Retry attempt appears as unrelated execution. |

## Invariants

- Retry cannot widen side effects.
- Retry state must link to the original attempt id.
- Mutating after-commit retry requires idempotency key or equivalent ledger.
- Stream retry requires chunk identity and completion/abort policy.
- Retry classification must be visible in compiled runtime plan metadata.

## Notes

Retry depends on sections 1, 3, and 4: runtime lifecycle, concrete identity, and
idempotency. Without those, retry safety cannot be certified.
