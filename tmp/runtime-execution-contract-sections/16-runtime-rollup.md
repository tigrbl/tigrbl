# 16 Runtime Rollup

This section proposes structured runtime rollups for support claims, operational
summaries, and release/certification evidence.

## Purpose

Runtime rollup turns raw execution detail into support statements that can be
audited. It answers which apps, routers, tables, operations, transports,
framings, retry modes, replay modes, idempotency modes, and lifecycle transitions
are actually supported, unsupported, fail-closed, partial, or untested.

## Proposed ADRs

| ADR | Decision | Why it is needed |
|---|---|---|
| `adr:runtime-rollup-derives-support-claims` | Runtime support claims must derive from compiled plans plus evidence. | Prevents release/support claims from being prose-only. |
| `adr:rollup-separates-support-fail-closed-partial-untested` | Rollups must distinguish support states. | Avoids reporting fail-closed or untested surfaces as supported. |

## Proposed SPECs

| SPEC | Scope | Required content |
|---|---|---|
| `spc:runtime-rollup-schema` | Common rollup schema. | Scope, ids, support state, evidence refs, plan refs, test refs, and status. |
| `spc:operation-support-rollup` | Operation-level support. | Op id, transports, framings, retry/replay/idempotency support, and test evidence. |
| `spc:transport-support-rollup` | Transport/framing support. | Family, exchange, framing, lane, support status, fail-closed status, and proof. |
| `spc:retry-replay-idempotency-rollup` | Reliability support rollup. | Retry class, replay modes, idempotency class, proof gaps, and unsupported cases. |
| `spc:release-evidence-rollup` | Release/certification rollup. | Feature ids, claim ids, test ids, evidence ids, raw refs, and release status. |
| `spc:rollup-state-classification` | Support state vocabulary. | `supported`, `unsupported`, `fail_closed`, `partial`, `untested`, `blocked`, `deprecated`. |

## Proposed Features

| Feature | Description | Implementation direction |
|---|---|---|
| `feat:runtime-rollup` | Add base runtime rollup generation. | Generate rollups from compiled plans, traces, tests, and evidence refs. |
| `feat:operation-support-rollup` | Summarize support by operation. | Include op id, bindings, semantics, tests, and gaps. |
| `feat:transport-framing-rollup` | Summarize transport/framing support. | Include supported/fail-closed/unsupported surfaces. |
| `feat:retry-replay-idempotency-rollup` | Summarize reliability semantics. | Report retry, replay, and idempotency proof per op/transport. |
| `feat:release-certification-rollup` | Feed SSOT/release evidence. | Connect rollups to claims, tests, evidence, and release status. |
| `feat:rollup-drillback` | Preserve drillback to raw proof. | Store raw trace/evidence/test refs. |

## Proposed Tests

| Test | Valid scenario | Invalid scenario |
|---|---|---|
| `tst:rollup-derived-from-compiled-plan-and-tests` | Rollup support state comes from plan and passing tests. | Rollup claims support from docs/prose only. |
| `tst:rollup-distinguishes-supported-unsupported-failclosed-partial-untested` | Rollup separates each support state. | Unsupported or fail-closed is reported as supported. |
| `tst:rollup-preserves-attempt-and-plan-identities` | Rollup contains `runtime_plan_id` and relevant attempt ids or evidence refs. | Rollup cannot drill back to source. |
| `tst:rollup-does-not-claim-replay-safe-from-read-only-proof` | Replay-safe claim requires replay tests, not only read tests. | Rollup overclaims replay safety. |
| `tst:release-rollup-links-to-evidence` | Release rollup links features/claims/tests/evidence. | Release support claim has no evidence link. |

## Invariants

- Rollups derive from compiled plans plus test evidence, not prose.
- Rollups must preserve enough identity to drill back to raw evidence.
- Rollups must distinguish supported, unsupported, fail-closed, partial, and untested states.
- Rollups cannot overclaim from narrower tests.
- Release/certification rollups must link to evidence and raw refs.

## Notes

Rollup is the primary answer surface for "what does this build support?" It is
also the bridge from runtime proof to SSOT claims and release certification.
