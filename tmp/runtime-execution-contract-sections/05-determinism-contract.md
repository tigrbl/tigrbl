# 05 Determinism Contract

This section proposes determinism classes for operations and atoms.

## Purpose

Determinism makes replay, cross-transport equivalence, trace comparison, and
certification meaningful. The contract is not that all operations are
deterministic. The contract is that nondeterminism is declared and visible.

## Proposed ADRs

| ADR | Decision | Why it is needed |
|---|---|---|
| `adr:determinism-classes-are-runtime-contract` | Operations and atoms declare determinism classes. | Prevents replay/equivalence tests from assuming stability where none exists. |
| `adr:nondeterminism-must-be-trace-visible` | Runtime-visible nondeterministic inputs must be recorded or declared opaque. | Makes replay and debugging honest. |

## Proposed SPECs

| SPEC | Scope | Required content |
|---|---|---|
| `spc:operation-determinism-classes` | Operation-level determinism classes. | Classes such as `deterministic`, `engine_dependent`, `time_dependent`, `random`, `external_io_dependent`, `nondeterministic_declared`. |
| `spc:atom-determinism-metadata` | Atom-level determinism metadata. | Atom class, nondeterministic inputs, output stability, trace requirements, and replay behavior. |
| `spc:normalized-result-determinism` | Stable normalized result rules. | Field ordering, serialization canonicalization, error normalization, and transport-independent result comparison. |
| `spc:nondeterministic-source-trace-contract` | Trace visibility for nondeterministic sources. | Required trace fields for time, random values, generated ids, external calls, and opaque sources. |

## Proposed Features

| Feature | Description | Implementation direction |
|---|---|---|
| `feat:determinism-classification` | Classify operations by determinism behavior. | Derive from op metadata, atom metadata, engine behavior, and transport behavior. |
| `feat:atom-determinism-metadata` | Add determinism metadata to atom contracts. | Extend atom registration/projection with determinism fields. |
| `feat:stable-normalized-output` | Ensure comparable stable normalized outputs. | Canonicalize result serialization and error projection for equivalence/replay tests. |
| `feat:nondeterminism-trace-annotation` | Trace nondeterministic sources. | Add trace annotations for generated ids, timestamps, external calls, random values, or opaque nondeterminism. |

## Proposed Tests

| Test | Valid scenario | Invalid scenario |
|---|---|---|
| `tst:read-same-state-same-plan-same-normalized-result` | Same read input, engine state, and runtime plan produce same normalized result. | Same conditions produce different result without declaration. |
| `tst:deterministic-projection-stable-field-order` | Deterministic projection serializes fields in stable order. | Field order varies and breaks normalized comparison. |
| `tst:nondeterministic-atom-requires-trace-annotation` | Timestamp/random/external atom marks nondeterministic source in trace. | Nondeterministic atom runs without trace annotation. |
| `tst:undeclared-nondeterminism-fails-contract` | Contract test rejects undeclared nondeterministic output. | Runtime accepts drift as deterministic behavior. |

## Invariants

- Deterministic operation replay is meaningful.
- Nondeterminism must be explicit in trace or declared opaque.
- Cross-transport equivalence must compare normalized semantic results, not raw bytes.
- Generated ids, timestamps, random values, and external IO cannot be hidden inside deterministic claims.

## Notes

This feature does not forbid nondeterministic operations. It gives them names,
classes, and trace obligations so retry, replay, and equivalence tests can make
valid claims.
