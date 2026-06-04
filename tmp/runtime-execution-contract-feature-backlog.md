# Runtime Execution Contract Feature Backlog

This temporary note captures the proposed feature backlog for closing the current
Tigrbl atoms, kernel, runtime, and transport semantics gaps. It intentionally
does not treat `dispatch uniqueness` or a hand-maintained `op/engine capability
vector` as settled requirements. The narrower goals are compile-time selector
collision control and derived requirements from the compiled atom/hook chain.

## 1. Runtime Execution Contract

Feature: one canonical state model for operation attempts, runtime channels,
engine sessions, completion fences, retries, replay, and trace.

Valid scenarios:

- REST create enters `received -> resolved -> executing -> committed -> emitted`.
- WebTransport stream create enters `session.open -> stream.open -> chunks.received -> input.complete -> executing -> emitted -> stream.close`.

Invalid scenarios:

- Closed session receives payload.
- Datagram moves through `stream.close`.
- Operation commits after runtime marked failed.

Invariants:

- No undocumented lifecycle transition.
- Every emitted result has a prior resolved operation.
- Every side effect belongs to one operation attempt id.

Ownership:

- `tigrbl_kernel` owns the canonical state table.
- `tigrbl_runtime` enforces the state table.

## 2. Canonical Operation Identity

Feature: every operation gets a stable canonical operation id independent of
transport.

Valid scenarios:

- `Widget.create` over REST, HTTP JSON-RPC, and WebSocket JSON-RPC all resolve
  to the same canonical operation id.

Invalid scenarios:

- Same semantic operation has unrelated ids per transport.
- Custom operation has no canonical id.
- Generated docs use one id while runtime dispatch uses another.

Invariants:

- One canonical operation id per semantic operation.
- Transport selectors are aliases, not identities.

## 3. Concrete Instance Identity

Feature: runtime-created objects and semantic objects get stable ids that make
parentage, isolation, trace correlation, replay, and rollup possible.

Valid scenarios:

- Runtime records semantic ids such as `app_id`, `router_id`, `table_id`,
  `op_id`, `atom_id`, `hook_id`, `binding_id`, `runtime_plan_id`, and
  `schema_id`.
- Runtime records concrete ids such as `attempt_id`, `session_id`, `stream_id`,
  `datagram_id`, `engine_session_id`, `transaction_id`, `trace_id`,
  `request_id`, `connection_id`, `client_id`, and `replay_id`.
- Every concrete id points back to its semantic owner where applicable, for
  example `attempt_id -> op_id -> table_id -> router_id -> app_id`.

Invalid scenarios:

- Stream event cannot be tied to operation attempt.
- Retry cannot identify original attempt.
- Replay cannot distinguish original execution from replayed or audit-only execution.
- Engine transaction cannot be tied to the operation attempt that opened it.
- Atom execution cannot be tied to the compiled atom id in the runtime plan.

Invariants:

- Every concrete runtime event has stable identity and parentage.
- Semantic ids are stable across transports for the same compiled app.
- Concrete ids are unique within their parent scope.
- Cross-scope references must be explicit and validated.

## 4. Idempotency Contract

Feature: idempotency classes per operation and per transport framing.

Valid scenarios:

- Create with idempotency key dedupes.
- Delete twice follows declared stable behavior.
- Append chunk dedupes by stream and chunk identity.

Invalid scenarios:

- Duplicate create on retry.
- Datagram replay creates duplicate effect.
- Idempotency key is accepted but not stored.

Invariants:

- Idempotency behavior must be declared before execution.
- Unsafe operations cannot be retried after side effects unless key-backed.

## 5. Determinism Contract

Feature: declare whether operations and atoms are deterministic, engine-dependent,
time-dependent, random, or externally dependent.

Valid scenarios:

- Read with same state and plan returns same normalized result.
- Deterministic projection serializes fields in stable order.

Invalid scenarios:

- Same operation, plan, and state return different normalized output without a
  declared nondeterministic source.

Invariants:

- Deterministic operation replay is meaningful.
- Nondeterminism must be explicit in trace.

## 6. Retry Policy

Feature: compile retry policy from operation semantics, atom chain, transaction
state, transport delivery, and idempotency.

Valid scenarios:

- Read retries after transient transport failure.
- Create retries only before commit or with idempotency key.
- Webhook delivery retries using an idempotency key.

Invalid scenarios:

- Retry committed create without idempotency key.
- Retry partial stream import without chunk ledger.

Invariants:

- Retry cannot widen side effects.
- Retry state must link to original attempt id.

## 7. Runtime Replay

Feature: support replay modes: semantic replay, dry replay, audit replay, and
trace replay.

Valid scenarios:

- Replay read.
- Replay create only with idempotency key and same input.
- Audit replay reconstructs trace without mutation.

Invalid scenarios:

- Replay mutating operation with no idempotency policy.
- Replay under different runtime plan without declaring plan drift.

Invariants:

- Replay must preserve `original_attempt_id`, runtime plan id, and replay mode.

## 8. Trace And Qlog Correlation

Feature: normalize runtime trace, transport events, and qlog-compatible transport
evidence.

Valid scenarios:

- WebTransport stream event maps to session id, stream id, and operation attempt.
- Qlog packet or stream event can be correlated with runtime transition where available.

Invalid scenarios:

- Trace says operation emitted result but transport has no completion fence.
- Qlog stream id cannot map to runtime stream id.

Invariants:

- Trace is causally ordered within a concrete instance.
- Qlog and transport evidence are correlation data, not semantic success by themselves.

## 9. Cross-Transport Equivalence

Feature: prove that equivalent bindings of the same operation have equivalent
semantic results.

Valid scenarios:

- REST create, HTTP JSON-RPC create, and WebSocket JSON-RPC create normalize to
  the same operation result and persistence effect.
- WebTransport stream create is valid if stream completion and commit policy are declared.

Invalid scenarios:

- REST create validates a required field but WebSocket JSON-RPC silently accepts it.
- HTTP stream create commits partial chunks after abort without policy.

Invariants:

- Same canonical operation id plus equivalent input produces equivalent normalized
  result, errors, persistence effect, idempotency behavior, and trace shape.

## 10. Transport Delivery Guarantees

Feature: publish and enforce delivery and ordering guarantees per family:
request, message, stream, session, and datagram.

Valid scenarios:

- HTTP request is one operation attempt.
- WebSocket messages are ordered per connection.
- WebTransport streams are ordered per stream.
- WebTransport datagrams are unordered and best effort.

Invalid scenarios:

- Treating datagram as ordered stream.
- Assuming cross-stream ordering in WebTransport.
- Claiming peer delivery when runtime only observed send completion.

Invariants:

- Transport family limits must be explicit.
- Runtime cannot upgrade weak delivery guarantees silently.

## 11. ASGI Transport Projection

Feature: define how ASGI `scope`, `receive`, and `send` project into Tigrbl
transport events.

Valid scenarios:

- `websocket.receive -> message.received`.
- `webtransport.stream.receive -> stream.chunk.received`.
- HTTP body stream projects to request or stream chunks depending on binding.

Invalid scenarios:

- ASGI message type bypasses kernel event taxonomy.
- Server-specific metadata becomes canonical without projection rules.

Invariants:

- Tigrbl semantics sit above ASGI.
- ASGI details are inputs to projection, not the semantic contract.

## 12. Session Leakage Prevention

Feature: isolate state by app, router, table, operation, attempt, client, session,
stream, datagram, engine session, transaction, and trace identity.

Valid scenarios:

- WebTransport stream belongs to one WebTransport session.
- Retry belongs to one original attempt.
- Trace events cannot cross session boundaries.
- Engine session belongs to one request/attempt scope unless explicitly pooled
  and checked out under a new scoped lease.
- Transaction state belongs to one engine session and operation attempt.
- Atom-local state is scoped to its operation attempt unless explicitly declared
  as app, router, table, or session state.

Invalid scenarios:

- Stream from session A mutates session B.
- Closed session receives payload.
- Reused stream id changes lane metadata.
- Engine session from attempt A is reused by attempt B without reset or lease.
- Transaction from one operation is committed by another operation.
- Trace or qlog events are attributed to the wrong session or engine session.
- App/router/table scoped state leaks into another app/router/table.

Invariants:

- No cross-session leakage.
- No engine-session leakage.
- No transaction leakage.
- No app/router/table state leakage.
- No cross-client access.
- Session close cascades to owned streams.
- Engine session close/rollback clears attempt-scoped state.

## 13. Unsupported Framing Fail-Closed

Feature: every framing support decision is explicit.

Valid scenarios:

- WebSocket `jsonrpc` requires negotiated subprotocol.
- WebSocket `ndjson` fails closed if unsupported.
- WebTransport datagram rejects `jsonrpc` unless explicitly supported.

Invalid scenarios:

- Unsupported `ndjson` becomes text.
- WebTransport outer framing becomes app JSON-RPC.
- Binary, bytes, and text collapse without declaration.

Invariants:

- No unsupported framing fallback.
- Framing token presence is not implementation proof.

## 14. Explicit Route And Selector Precedence

Feature: compile-time selector collision and shadowing control.

This replaces the broader and less precise phrase `dispatch uniqueness`.

Rationale:

- The goal is not that every selector is globally unique across all protocols.
  REST paths, JSON-RPC methods, WebSocket paths, and WebTransport lanes are
  different selector namespaces.
- The goal is that, inside a selector namespace and precedence scope, the
  compiler can prove there is exactly one intended semantic resolution or an
  explicit override policy.
- This prevents accidental shadowing when apps, routers, tables, inherited
  specs, generated defaults, and custom operations compose.
- This also keeps the hot path simple: request selectors resolve through a
  precomputed table instead of dynamic precedence checks.

Valid scenarios:

- Two routes may share shape only with explicit override or shadow policy.
- Nested router precedence is visible in compiled plan.
- REST `GET /widgets/{id}` and JSON-RPC `Widget.read` may both point to the
  same `op_id` because they are different selector namespaces.
- A router may intentionally override a table default only when the override is
  declared and appears in the compiled plan.

Invalid scenarios:

- Later router silently shadows earlier operation.
- REST selector and JSON-RPC method resolve to different semantic operations unintentionally.
- Generated CRUD default claims a REST path that a custom operation already owns.
- Two inherited specs compile to the same WebSocket path without an explicit
  shadow policy.

Invariants:

- No hidden route precedence.
- Ambiguity fails at compile time unless explicitly governed.
- Selector resolution is precomputed and visible in the runtime plan.
- A selector collision is allowed only when it resolves to the same `op_id` or
  has an explicit override policy.

## 15. Runtime Compaction

Feature: compact runtime plans, traces, and evidence into stable summaries.

Valid scenarios:

- Atom events roll up to phase summary.
- Phases roll up to operation attempt.
- Attempts roll up to route, app, and release evidence.

Invalid scenarios:

- Compaction drops failure transition.
- Rollup claims idempotency without preserving idempotency key evidence.

Invariants:

- Compaction is loss-aware.
- Every rollup can point back to raw trace or evidence, or declare truncation.

## 16. Runtime Rollup

Feature: structured aggregation for certification and operational summaries.

Rationale:

- Runtime rollup turns raw execution detail into a trustworthy summary without
  rereading every atom event, transport event, trace entry, or evidence file.
- It lets the project answer support questions from compiled truth: which apps,
  routers, tables, operations, transports, framings, retry modes, replay modes,
  and lifecycle transitions are actually available.
- It is also the bridge from runtime evidence to SSOT/release evidence. A release
  should be able to claim support from rollups backed by raw traces and tests,
  not from prose.
- Rollup is separate from compaction: compaction reduces representation size;
  rollup preserves meaning at a higher level.

Valid scenarios:

- The app can state that it supports transactional CRUD over REST and JSON-RPC,
  WebSocket JSON-RPC for create/read, WebTransport stream tail, and WebTransport
  datagram send only.
- A trace rollup states that operation attempt `attempt_id=...` executed atom
  ids A/B/C, opened engine session E, committed transaction T, emitted response
  R, and completed under runtime plan P.
- A release rollup states which operations have idempotency proof, retry proof,
  replay proof, cross-transport equivalence proof, and fail-closed framing proof.

Invalid scenarios:

- Release claims transport support because a binding token exists.
- Engine support inferred from package name.
- Rollup says an app is replay-safe when only read operations were tested.
- Rollup merges successful and failed attempts without preserving failure counts.

Invariants:

- Rollups derive from compiled plans plus test evidence, not prose.
- Rollups must preserve enough identity to drill back to raw evidence.
- Rollups must distinguish supported, unsupported, fail-closed, partial, and
  untested states.

## 17. Atom-Chain Requirement Projection

Feature: derive execution requirements from the compiled atom and hook chain.

This should not become a redundant hand-maintained operation capability vector.
Atoms already are capabilities, and hooks/atoms are chained during compilation.
The useful work is to project requirements from what the kernel actually compiled.

Rationale:

- This is not a second capability model that documents which atoms belong to an
  operation. The compiled chain already answers that.
- Projection is about deriving consequences from the chain: transaction needed,
  engine session needed, stream send needed, datagram send needed, idempotency
  store needed, replay ledger needed, completion fence needed, trace emission
  needed, and so on.
- It catches mismatches before execution. For example, a compiled chain that
  includes transaction commit cannot run against an engine/session scope that
  cannot commit or roll back.
- It gives hot-path dispatch a compact requirement summary while preserving the
  atom chain as the source of truth.
- It gives rollup and certification a stable explanation of why an operation
  was considered supported, unsupported, retry-safe, replay-safe, or fail-closed.

Valid scenarios:

- If a chain includes transaction begin/commit atoms, require a transaction-capable engine.
- If a chain includes datagram emit atom, require a datagram-capable channel adapter.
- If a chain includes idempotency lookup/write atoms, require an idempotency
  store and preserve idempotency key identity in trace.
- If a chain includes replay ledger atoms, require replay identity and plan hash
  compatibility.
- If a chain includes streaming emit atoms, require stream ordering and completion
  fence semantics.

Invalid scenarios:

- Hand-maintained operation capability vector drifts from atom chain.
- Engine docs say unsupported while runtime executes anyway.
- Runtime starts execution before discovering that the channel cannot emit the
  required transport family.
- Runtime retries a mutating chain that has no idempotency or replay-safe atoms.

Invariants:

- Requirements are derived from compiled atom/hook chain.
- No parallel capability registry for operation atom membership.
- Projection cannot contradict the compiled chain.
- Projection is a summary, not the source of truth.

Benefits:

- Fast rejection before execution.
- Better hot-path packing.
- Retry and idempotency classification.
- Evidence rollup derived from compiled truth.
