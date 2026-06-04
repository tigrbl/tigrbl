# 10 Transport Delivery Guarantees

This section proposes the transport delivery and ordering guarantee matrix for
request, message, stream, session, and datagram families.

## Purpose

Transport delivery guarantees define what Tigrbl promises after it accepts or
observes a transport event. They must be family-scoped because HTTP requests,
WebSocket messages, streams, sessions, and datagrams have different ordering and
delivery semantics. Runtime must not silently upgrade weak guarantees.

## Proposed ADRs

| ADR | Decision | Why it is needed |
|---|---|---|
| `adr:transport-delivery-guarantees-are-family-scoped` | Delivery and ordering guarantees are declared by runtime family and lane. | Prevents datagrams, streams, messages, and requests from being treated as interchangeable. |
| `adr:runtime-cannot-upgrade-weak-transport-guarantees` | Runtime cannot claim stronger delivery than the transport/family supports. | Prevents local send completion from being presented as peer delivery or semantic success. |

## Proposed SPECs

| SPEC | Scope | Required content |
|---|---|---|
| `spc:request-delivery-guarantee` | HTTP request/response and HTTP JSON-RPC request semantics. | One accepted request maps to one operation attempt or one batch with item attempts. |
| `spc:message-delivery-guarantee` | WebSocket/message semantics. | Per-connection message ordering, receive/send behavior, close handling, and subprotocol limits. |
| `spc:stream-ordering-guarantee` | HTTP stream and WebTransport stream semantics. | Ordered chunks within stream, independent stream ordering, completion, abort, and reset handling. |
| `spc:session-lifecycle-guarantee` | Session-scoped transports such as WebTransport. | Session open/accept/ready/close, owned streams/datagrams, and close cascade. |
| `spc:datagram-best-effort-guarantee` | Datagram semantics. | Best-effort, unordered delivery, duplicate/drop behavior, id requirement, and app-level dedupe rules. |
| `spc:send-completion-vs-peer-delivery` | Completion semantics. | Runtime send completion, stream close, peer ack, application ack, failure, and trace wording. |

## Proposed Features

| Feature | Description | Implementation direction |
|---|---|---|
| `feat:transport-delivery-guarantee-matrix` | Publish the guarantee matrix across transport families. | Add kernel/runtime contract table and docs. |
| `feat:request-one-attempt-guarantee` | Bind each accepted request to one operation attempt, or one batch with item attempts. | Add attempt identity and batch item attempt rules. |
| `feat:websocket-per-connection-ordering` | Enforce/order WebSocket messages per connection. | Add connection-scoped ordering and close-state checks. |
| `feat:webtransport-per-stream-ordering` | Enforce ordering within a WebTransport stream only. | Add stream-scoped sequence/transition checks. |
| `feat:datagram-best-effort-policy` | Treat datagrams as unordered best-effort by default. | Reject stronger assumptions unless app framing declares them. |
| `feat:send-completion-fence-policy` | Separate local send completion from peer/application delivery. | Normalize completion fence trace/result fields. |

## Proposed Tests

| Test | Valid scenario | Invalid scenario |
|---|---|---|
| `tst:http-request-one-operation-attempt` | Accepted HTTP request maps to one attempt id. | Request produces multiple attempts without batch semantics. |
| `tst:websocket-message-ordering-per-connection` | WebSocket messages preserve per-connection order. | Message from later receive executes before earlier receive without policy. |
| `tst:wt-stream-ordering-per-stream` | WebTransport chunks preserve order within one stream. | Chunk sequence on one stream is reordered without declaration. |
| `tst:wt-no-cross-stream-ordering-assumption` | Independent WebTransport streams do not assume relative ordering. | Runtime depends on cross-stream order for correctness. |
| `tst:datagram-unordered-best-effort` | Datagram path records unordered best-effort delivery semantics. | Runtime treats datagram as ordered/reliable by default. |
| `tst:send-completion-does-not-claim-peer-delivery` | Runtime reports local send completion distinctly from peer delivery. | Runtime claims peer delivery from local send completion. |

## Invariants

- Transport family limits must be explicit.
- Runtime cannot upgrade weak delivery guarantees silently.
- Requests are unary unless explicitly batch/stream.
- WebSocket ordering is per connection.
- Stream ordering is per stream, not across streams.
- Datagrams are unordered and best effort unless app framing adds stronger guarantees.
- Completion fences must state what completed.

## Notes

This section constrains cross-transport equivalence. An operation can bind to a
transport only when the operation semantics can compose with that transport's
delivery guarantees.
