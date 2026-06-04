# 15 Runtime Compaction

This section proposes loss-aware compaction for runtime plans, traces, and
evidence.

## Purpose

Runtime traces and evidence can become large. Compaction reduces representation
size while preserving enough identity, state, and failure information to support
debugging, replay, rollup, and certification. Compaction must be loss-aware and
must declare truncation.

## Proposed ADRs

| ADR | Decision | Why it is needed |
|---|---|---|
| `adr:runtime-compaction-is-loss-aware` | Runtime compaction must preserve declared semantics and disclose loss. | Prevents compact summaries from hiding failures or unsupported states. |
| `adr:compacted-evidence-must-preserve-drillback` | Compacted evidence must drill back to raw trace/evidence or declare truncation. | Keeps rollups and release claims auditable. |

## Proposed SPECs

| SPEC | Scope | Required content |
|---|---|---|
| `spc:runtime-plan-compaction-contract` | Compaction of runtime plans. | Shared segment refs, hot section summaries, atom-chain summaries, and plan hash preservation. |
| `spc:trace-compaction-contract` | Compaction of trace events. | Phase summaries, attempt summaries, preserved ids, error preservation, and order preservation. |
| `spc:evidence-compaction-contract` | Compaction of evidence artifacts. | Raw evidence refs, summary schema, pass/fail counts, unsupported states, and provenance. |
| `spc:compaction-truncation-declaration` | How truncation/loss is represented. | Truncated fields, omitted rows, limits, reason, and impact. |
| `spc:failure-transition-preservation` | Required failure preservation. | Failed transitions, error classes, terminal states, and state-machine violations. |

## Proposed Features

| Feature | Description | Implementation direction |
|---|---|---|
| `feat:runtime-plan-compaction` | Compact runtime plan representation while preserving ids and plan hash. | Use packed sections and shared references. |
| `feat:trace-compaction` | Compact atom/phase/attempt traces into summaries. | Add trace summary emitters and drillback refs. |
| `feat:evidence-compaction` | Compact test/evidence artifacts for release use. | Generate evidence summaries with raw artifact refs. |
| `feat:loss-aware-compaction` | Declare truncation and omitted content. | Add `truncated`, `omitted_count`, and impact fields. |
| `feat:compaction-drillback` | Preserve ability to inspect raw data. | Store raw refs or declare unavailable raw evidence. |

## Proposed Tests

| Test | Valid scenario | Invalid scenario |
|---|---|---|
| `tst:atom-events-compact-to-phase-summary` | Atom trace compacts to phase summary with atom ids and counts. | Atom failures disappear from summary. |
| `tst:phase-summary-compacts-to-attempt-summary` | Phase summaries roll into attempt summary with terminal state. | Attempt summary omits failed phase. |
| `tst:compaction-preserves-failure-transition` | Failed lifecycle transition remains visible after compaction. | Compaction reports success-only summary. |
| `tst:compaction-declares-truncation` | Truncated trace declares omitted count and reason. | Truncation occurs silently. |
| `tst:compacted-rollup-drills-back-to-raw-evidence` | Summary contains raw trace/evidence ref. | Summary has no drillback and no truncation declaration. |

## Invariants

- Compaction is loss-aware.
- Every rollup can point back to raw trace or evidence, or declare truncation.
- Failure transitions must be preserved.
- Runtime plan identity/hash must survive compaction.
- Compaction must not convert unsupported/partial/failed states into supported states.

## Notes

Compaction is not rollup. Compaction reduces representation size; rollup
interprets support and certification meaning from compiled plans and evidence.
