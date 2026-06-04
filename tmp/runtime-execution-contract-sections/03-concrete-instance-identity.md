# 03 Concrete Instance Identity

This section proposes the identity graph for semantic objects and concrete
runtime instances.

## Purpose

Runtime safety depends on knowing which app, router, table, operation, atom,
attempt, session, stream, datagram, engine session, transaction, trace, and
replay each event belongs to. These ids are the basis for leakage prevention,
retry parentage, replay safety, trace/qlog correlation, and rollup drillback.

## Proposed ADRs

| ADR | Decision | Why it is needed |
|---|---|---|
| `adr:semantic-and-concrete-runtime-identities` | Tigrbl distinguishes semantic ids from concrete runtime ids. | Prevents conflating stable compiled objects with per-execution instances. |
| `adr:runtime-parentage-identity-graph` | Runtime events must preserve parentage between concrete ids and semantic owners. | Enables trace correlation, leakage checks, replay, and evidence drillback. |

## Proposed SPECs

| SPEC | Scope | Required content |
|---|---|---|
| `spc:semantic-id-schema` | Stable ids for compiled semantic objects. | `app_id`, `router_id`, `table_id`, `op_id`, `atom_id`, `hook_id`, `binding_id`, `runtime_plan_id`, `schema_id`. |
| `spc:concrete-instance-id-schema` | Runtime ids for concrete executions and transport objects. | `attempt_id`, `session_id`, `stream_id`, `datagram_id`, `engine_session_id`, `transaction_id`, `trace_id`, `request_id`, `connection_id`, `client_id`, `replay_id`. |
| `spc:runtime-parentage-graph` | Parent-child identity relationships. | Rules such as `attempt_id -> op_id -> table_id -> router_id -> app_id`; `stream_id -> session_id`; `transaction_id -> engine_session_id -> attempt_id`. |
| `spc:trace-identity-correlation` | Identity fields required in trace/qlog-related events. | Required ids, optional ids, correlation ids, and failure behavior when ids are missing. |

## Proposed Features

| Feature | Description | Implementation direction |
|---|---|---|
| `feat:semantic-ids-app-router-table-op-atom` | Assign semantic ids to compiled app/router/table/op/atom/hook/binding objects. | Add ids during spec normalization and kernel compilation. |
| `feat:concrete-ids-attempt-session-stream-datagram-engine-trace` | Assign concrete runtime ids to attempts, sessions, streams, datagrams, engine sessions, transactions, and traces. | Add id creation and propagation in runtime context/channel state. |
| `feat:runtime-parentage-graph` | Maintain validated parentage across semantic and concrete ids. | Add parent graph projection to runtime plans and traces. |
| `feat:atom-execution-id-correlation` | Link atom execution events to compiled atom ids and operation attempts. | Annotate atom execution trace entries with `atom_id`, `attempt_id`, and `runtime_plan_id`. |

## Proposed Tests

| Test | Valid scenario | Invalid scenario |
|---|---|---|
| `tst:semantic-id-stability-across-transports` | Same compiled app yields stable semantic ids across REST/JSON-RPC/WS bindings. | Semantic ids change based only on transport selector. |
| `tst:concrete-id-uniqueness-within-parent-scope` | Stream ids are unique within a session; attempt ids are unique within runtime execution. | Concrete id collision appears in same parent scope. |
| `tst:attempt-id-links-to-op-table-router-app` | Attempt trace records `attempt_id -> op_id -> table_id -> router_id -> app_id`. | Attempt cannot be traced to semantic owner. |
| `tst:atom-execution-links-to-atom-id-and-runtime-plan` | Atom trace entry records `atom_id`, `attempt_id`, and `runtime_plan_id`. | Atom execution appears only as an unlabeled callable. |
| `tst:replay-id-preserves-original-attempt-id` | Replay record links `replay_id` to `original_attempt_id`. | Replay cannot distinguish original execution from replay. |

## Invariants

- Every concrete runtime event has stable identity and parentage.
- Semantic ids are stable across transports for the same compiled app.
- Concrete ids are unique within their parent scope.
- Cross-scope references must be explicit and validated.
- Trace and replay records must preserve enough identity for drillback.

## Notes

This feature is a prerequisite for no-leakage guarantees. Without explicit
parentage, session leakage, engine-session leakage, and trace misattribution are
hard to detect reliably.
