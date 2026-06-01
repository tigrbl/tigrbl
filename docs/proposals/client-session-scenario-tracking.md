# Proposal Draft: Client Session Scenario Tracking for Tigrbl

Status: proposal draft

This draft is not an accepted ADR, SPEC, feature row, or release claim. It proposes a repo-grounded tracking model for client session scenarios in Tigrbl transport work. The main goal is to track client behavior honestly across long-lived transports without mixing transport-internal structure into the public tracking surface.

## Problem

The current repo already distinguishes long-lived transport behavior from one-shot request behavior:

- `SSE`, `WebSocket`, and `WebTransport` have explicit long-lived loop or session semantics in conformance and runtime tests.
- ordinary REST and ordinary HTTP JSON-RPC are explicitly one-shot and should not be treated as session scenarios by default.

That distinction is useful, but it is still easy to blur two different concerns:

- the lifecycle of one client session
- the scheduling relationship between multiple client sessions

This proposal separates those concerns so that the tracked scenarios stay stable, testable, and understandable.

## Scope

Track client session scenarios for long-lived or session-shaped transport surfaces:

- `http.sse`
- `https.sse`
- `ws`
- `wss`
- `webtransport`

Do not place these into the same scenario bucket unless later governance explicitly expands them:

- ordinary `http.rest`
- ordinary `https.rest`
- ordinary `http.jsonrpc`
- ordinary `https.jsonrpc`

Those unary request-response surfaces remain important, but they are not session scenarios in this proposal.

## Proposal Shape

Track scenarios on two axes.

### Axis 1: Client Topology Scenario

This axis answers: how many clients are active, and how are they scheduled relative to each other?

#### 1. `single_client`

One client opens one session and drives it through its lifecycle.

This is the baseline scenario and should exist for every tracked session-capable transport.

#### 2. `sequential_clients`

Client A runs to completion. Only after A is done does client B run.

This proves that session state is not leaked across clients while avoiding overlap or concurrency concerns.

#### 3. `interleaved_clients`

Client A and client B are both active, but they alternate work in a bounded loop.

Example:

1. A sends one unit
2. B sends one unit
3. A sends one unit
4. B sends one unit

This is not arbitrary concurrency. It is controlled alternation and should be tracked separately from unconstrained concurrent traffic.

#### 4. `concurrent_clients`

Many clients are active at once and may send whenever they want.

This is the unconstrained multi-client scenario. It is the correct place to track fairness, bounded buffering, rate budgets, and scheduler pressure.

### Axis 2: Per-Session Lifecycle Scenario

This axis answers: what happened inside an individual client session?

#### Required lifecycle scenarios

- `session_opened`
- `session_accepted`
- `session_ready`
- `payload_received`
- `payload_emitted`
- `session_closed`
- `session_disconnected`
- `session_cancelled`
- `session_rejected`

#### Liveness scenarios

- `session_heartbeat_sent`
- `session_heartbeat_missed`
- `session_idle_timeout`
- `session_max_duration_reached`

These matter most for `SSE`, `WebSocket`, and `WebTransport`, where the repo already treats session liveness as a real transport concern.

#### Flow-control and budget scenarios

- `session_backpressure_applied`
- `session_buffer_limit_hit`
- `session_rate_budget_hit`
- `session_fairness_yield`

These are especially important in `interleaved_clients` and `concurrent_clients`.

#### Integrity and isolation scenarios

- `session_cross_client_leak_rejected`
- `session_cross_session_payload_rejected`
- `session_post_close_payload_rejected`
- `session_metadata_conflict_rejected`

These scenarios map directly to the fail-closed behavior already present in WebTransport runtime tests.

## Transport-Specific Expectations

### SSE

Track:

- open
- ready
- event emission
- heartbeat
- disconnect detection
- idle timeout
- close

SSE should participate in:

- `single_client`
- `sequential_clients`
- `interleaved_clients`
- `concurrent_clients`

### WebSocket

Track:

- connect/open
- accept
- inbound message handling
- outbound message handling
- heartbeat
- cancellation on close
- bounded buffering
- close

WebSocket should participate in:

- `single_client`
- `sequential_clients`
- `interleaved_clients`
- `concurrent_clients`

### WebTransport

Track:

- open
- accept
- ready
- stream activity
- datagram activity
- substream fairness
- close
- post-close rejection
- cross-session rejection

WebTransport should participate in:

- `single_client`
- `sequential_clients`
- `interleaved_clients`
- `concurrent_clients`

WebTransport is the strongest current example of why multi-client topology and per-session lifecycle must remain separate.

## Public Tracking Surface

The public tracking surface should stay client-centric.

Recommended fields:

- `scenario_kind`
- `client_id`
- `session_id`
- `transport`
- `subevent`
- `stream_id`
- `datagram_id`
- `framing`
- `opened_at`
- `closed_at`
- `error_kind`

Optional but useful fields:

- `close_code`
- `close_reason`
- `path`
- `op_alias`
- `peer_addr`
- `auth_subject`

## Explicit Exclusion: `lane`

`lane` should not be part of the public tracking surface in this proposal.

Reason:

- it is runtime-internal structure
- it leaks transport-specific internal modeling into a client-facing scenario taxonomy
- `stream_id` and `datagram_id` are sufficient public identifiers for the scenarios this proposal wants to track

This does not forbid the runtime from using internal lane classification. It only keeps that detail out of the proposal's public scenario model.

## Scenario Matrix

| Scenario kind | One active client at a time | Overlap allowed | Ordering is controlled | Many clients may fire arbitrarily |
|---|---|---|---|---|
| `single_client` | yes | no | yes | no |
| `sequential_clients` | yes | no | yes | no |
| `interleaved_clients` | no | yes | yes | no |
| `concurrent_clients` | no | yes | no | yes |

## Minimum Required Coverage

At minimum, the repo should be able to prove:

1. one `single_client` scenario for each tracked transport
2. one `sequential_clients` scenario proving isolation across sessions
3. one `interleaved_clients` scenario proving bounded alternation behavior
4. one `concurrent_clients` scenario proving no collapse under uncontrolled multi-client firing

Within each of those, the repo should capture at least:

- open or accept
- payload activity
- close or disconnect
- one rejection or fail-closed path where applicable

## Non-Goals

- Do not invent a new public `lane` taxonomy for scenario tracking.
- Do not collapse client topology and transport lifecycle into one flat enum.
- Do not treat unary REST or unary HTTP JSON-RPC as session scenarios by default.
- Do not imply that provisional WebTransport support is already a mature release claim.

## Suggested Next Slice

1. Add one repo-owned tracking note or spec table defining `scenario_kind`.
2. Add scenario-oriented tests for `single_client`, `sequential_clients`, `interleaved_clients`, and `concurrent_clients`.
3. Reuse existing transport/runtime truth surfaces for lifecycle event names and fail-closed behavior.
4. Keep `stream_id` and `datagram_id`, but omit `lane` from the public scenario model.
5. Add SSOT ADR, SPEC, feature, claim, test, and evidence rows before treating this proposal as accepted support.
