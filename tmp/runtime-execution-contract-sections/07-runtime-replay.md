# 07 Runtime Replay

This section proposes runtime replay modes and the compatibility rules that keep
replay from becoming accidental re-execution.

## Purpose

Replay is useful for debugging, audit, recovery, deterministic verification, and
cross-transport equivalence. But replay is dangerous if mutating operations can
run again without idempotency, if runtime plan drift is ignored, or if replay
records lose their parentage. Tigrbl needs explicit replay modes.

## Proposed ADRs

| ADR | Decision | Why it is needed |
|---|---|---|
| `adr:runtime-replay-modes` | Runtime replay has distinct modes: semantic replay, dry replay, audit replay, and trace replay. | Prevents audit reconstruction from being confused with safe semantic execution. |
| `adr:replay-plan-compatibility-required` | Replay must validate runtime plan compatibility or declare drift. | Prevents stale traces from being replayed under different semantics silently. |

## Proposed SPECs

| SPEC | Scope | Required content |
|---|---|---|
| `spc:runtime-replay-mode-contract` | Replay mode taxonomy and required metadata. | Mode names, mutation rules, required ids, plan hash behavior, and terminal outcomes. |
| `spc:semantic-replay-contract` | Replay that may execute semantics. | Allowed operation classes, idempotency requirements, deterministic requirements, and state preconditions. |
| `spc:audit-replay-contract` | Replay that reconstructs evidence without mutation. | Trace reconstruction, identity preservation, evidence output, and mutation prohibition. |
| `spc:runtime-plan-hash-replay-compatibility` | Runtime plan compatibility. | Runtime plan id/hash, schema version, atom chain compatibility, and drift declaration rules. |
| `spc:replay-parentage-contract` | Parentage between replay and original execution. | `replay_id`, `original_attempt_id`, `runtime_plan_id`, replay cause, and replay mode fields. |

## Proposed Features

| Feature | Description | Implementation direction |
|---|---|---|
| `feat:runtime-replay-modes` | Add explicit replay mode handling. | Runtime API and trace fields distinguish semantic, dry, audit, and trace replay. |
| `feat:semantic-replay` | Execute replay only when semantics are safe. | Require deterministic/idempotent or key-backed operation contract. |
| `feat:dry-replay` | Run validation/planning without side effects. | Use runtime plan and atom-chain metadata while suppressing mutation. |
| `feat:audit-replay` | Reconstruct trace/evidence without execution. | Rehydrate trace and rollup records without handlers or engine mutation. |
| `feat:trace-replay` | Replay trace order for diagnostics. | Preserve causal ordering and state transition checks. |
| `feat:replay-plan-hash-check` | Reject or mark drift when runtime plan differs. | Compare `runtime_plan_id`/hash and atom-chain/schema versions. |

## Proposed Tests

| Test | Valid scenario | Invalid scenario |
|---|---|---|
| `tst:read-semantic-replay` | Deterministic read replays under same plan and state. | Replay output differs without declared nondeterminism. |
| `tst:create-replay-requires-idempotency-key` | Create semantic replay succeeds only with matching idempotency key. | Create replay duplicates row. |
| `tst:audit-replay-does-not-mutate` | Audit replay reconstructs trace and evidence without touching engine state. | Audit replay executes handler or mutates persistence. |
| `tst:replay-under-different-plan-requires-drift-declaration` | Replay under changed plan is rejected or marked as drift. | Runtime silently replays under different atom chain or schema. |
| `tst:replay-preserves-original-attempt-id` | Replay record links to `original_attempt_id`. | Replay appears as unrelated operation attempt. |

## Invariants

- Replay must preserve `original_attempt_id`, `replay_id`, runtime plan id, and replay mode.
- Semantic replay is allowed only when operation semantics permit it.
- Audit replay and trace replay must not mutate.
- Plan drift must be rejected or explicitly declared.
- Replay cannot hide nondeterministic sources.

## Notes

Replay is separate from retry. Retry is part of live failure recovery; replay is
post-facto or explicit re-execution/reconstruction under a replay mode.
