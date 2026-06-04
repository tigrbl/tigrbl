# 08 Trace And Qlog Correlation

This section proposes trace and qlog correlation rules for runtime and transport
evidence.

## Purpose

Trace and qlog data are useful only if they can be tied to runtime identities and
state transitions. Qlog or packet-level evidence can show transport behavior,
but it is not by itself semantic success. Tigrbl needs a correlation contract
that links transport evidence to sessions, streams, datagrams, attempts, and
runtime transitions.

## Proposed ADRs

| ADR | Decision | Why it is needed |
|---|---|---|
| `adr:trace-qlog-correlation-is-evidence-not-success` | Qlog and transport traces are correlation evidence, not proof of semantic success by themselves. | Prevents transport-level observations from overstating operation completion. |
| `adr:transport-events-map-to-runtime-transitions` | Transport events must map to runtime state transitions through a declared projection. | Makes trace/qlog usable for lifecycle and leakage checks. |

## Proposed SPECs

| SPEC | Scope | Required content |
|---|---|---|
| `spc:runtime-trace-event-schema` | Common runtime trace schema. | Required ids, event type, state transition, atom id, op id, attempt id, timestamps, and status. |
| `spc:qlog-correlation-schema` | Mapping qlog-compatible events to runtime ids. | Transport ids, connection ids, stream ids, session ids, correlation limits, and unavailable-data behavior. |
| `spc:webtransport-trace-correlation` | WebTransport-specific trace mapping. | Session, stream, datagram, qlog stream id, runtime stream id, and attempt correlation. |
| `spc:completion-fence-trace-contract` | Trace requirements around completion fences. | Emit start, emit completion, send failure, stream close, and peer/application ack distinctions. |
| `spc:transport-evidence-causality` | Causal ordering of transport and runtime events. | Ordering rules, partial order, dropped events, truncation, and clock/source limitations. |

## Proposed Features

| Feature | Description | Implementation direction |
|---|---|---|
| `feat:runtime-trace-schema` | Normalize runtime trace events. | Add canonical trace event fields to runtime/context trace emission. |
| `feat:qlog-correlation` | Correlate qlog-compatible transport events to runtime identities where possible. | Add correlation adapters and explicit "not available" states. |
| `feat:webtransport-session-stream-datagram-trace` | Trace WebTransport session/stream/datagram events with parentage. | Extend current WebTransport trace with operation attempt and runtime plan ids. |
| `feat:completion-fence-trace` | Trace completion fence semantics. | Emit trace events for local send completion, stream close, failure, and app ack. |
| `feat:transport-evidence-rollup` | Roll up transport evidence into runtime evidence summaries. | Add rollup format that keeps transport evidence distinct from semantic success. |

## Proposed Tests

| Test | Valid scenario | Invalid scenario |
|---|---|---|
| `tst:wt-stream-event-links-session-stream-attempt` | WebTransport stream event records session id, stream id, and attempt id. | Stream event cannot be attributed to operation attempt. |
| `tst:qlog-stream-id-correlates-to-runtime-stream-id` | Qlog stream id maps to runtime `stream_id` where qlog data is available. | Qlog event is uncorrelated but reported as correlated. |
| `tst:trace-emitted-result-requires-completion-fence` | Result emission trace includes completion fence state. | Runtime trace claims emitted success without completion evidence. |
| `tst:qlog-is-not-treated-as-semantic-success` | Qlog send observation is recorded as transport evidence only. | Qlog send is treated as operation success. |
| `tst:trace-causal-order-within-concrete-instance` | Trace preserves causal order for one attempt/session/stream. | Trace order violates lifecycle state machine. |

## Invariants

- Trace is causally ordered within a concrete instance.
- Qlog and transport evidence are correlation data, not semantic success by themselves.
- Trace events must carry enough identity to tie back to operation, attempt, session, stream, datagram, engine session, and plan where applicable.
- Completion fence traces must state what completed.
- Missing qlog data must be declared, not inferred.

## Notes

This is especially important for WebTransport and stream work. Transport
handshake, stream, and datagram evidence can diagnose delivery problems, but the
runtime still owns semantic operation success.
