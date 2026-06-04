# 13 Unsupported Framing Fail-Closed

This section proposes explicit framing support and fail-closed behavior for
unsupported or ambiguous framing combinations.

## Purpose

Framing tokens are not proof of runtime support. Tigrbl must distinguish
declared vocabulary from implemented behavior and reject unsupported framing
instead of silently downgrading to a nearby framing such as text, JSON, or bytes.

## Proposed ADRs

| ADR | Decision | Why it is needed |
|---|---|---|
| `adr:unsupported-framing-fails-closed` | Unsupported framing combinations fail closed before execution. | Prevents silent fallback and protocol confusion. |
| `adr:framing-token-presence-is-not-runtime-support` | A framing token in a spec vocabulary is not implementation proof. | Keeps docs, kernel, runtime, and tests honest about actual support. |

## Proposed SPECs

| SPEC | Scope | Required content |
|---|---|---|
| `spc:framing-support-matrix-contract` | Current and target support matrix. | Protocol, binding, family, exchange, framing, support status, and fail-closed cases. |
| `spc:websocket-jsonrpc-subprotocol-contract` | WebSocket JSON-RPC support requirements. | Required subprotocol negotiation, request/response framing, batch, error, and unsupported cases. |
| `spc:websocket-ndjson-fail-closed-contract` | WebSocket NDJSON status. | Current unsupported behavior, rejection surface, and future support gate. |
| `spc:webtransport-outer-inner-framing-contract` | WebTransport framing separation. | Outer `webtransport` framing, lane inner framing, allowed/rejected inner framings. |
| `spc:binary-bytes-text-distinction` | Distinction between `binary`, `bytes`, and `text`. | Required media/framing declaration and no implicit collapse. |

## Proposed Features

| Feature | Description | Implementation direction |
|---|---|---|
| `feat:framing-support-matrix` | Publish and enforce framing support by binding/lane. | Add machine-readable support table and runtime/kernel validators. |
| `feat:ws-jsonrpc-subprotocol-required` | Require WebSocket JSON-RPC subprotocol. | Reject WS JSON-RPC framing without negotiated subprotocol. |
| `feat:ws-ndjson-fail-closed` | Keep WS NDJSON unsupported unless explicitly implemented. | Fail closed and preserve current support truth. |
| `feat:wt-datagram-jsonrpc-rejection` | Reject WT datagram JSON-RPC unless app policy supports it. | Validate datagram inner framing. |
| `feat:wt-outer-framing-preserved` | Preserve WebTransport outer framing as `webtransport`. | Reject attempts to treat outer framing as JSON-RPC/text. |
| `feat:binary-bytes-text-explicit-contract` | Require explicit treatment for binary/bytes/text. | Avoid hidden coercion between payload classes. |

## Proposed Tests

| Test | Valid scenario | Invalid scenario |
|---|---|---|
| `tst:ws-jsonrpc-requires-subprotocol` | WS JSON-RPC works only when `jsonrpc` subprotocol is negotiated. | WS JSON-RPC runs with no subprotocol. |
| `tst:ws-ndjson-fails-closed` | WS NDJSON is rejected when unsupported. | WS NDJSON silently becomes text or JSON. |
| `tst:wt-datagram-jsonrpc-rejected-unless-supported` | WT datagram rejects JSON-RPC by default. | Datagram JSON-RPC executes without dedupe/order policy. |
| `tst:wt-outer-framing-cannot-be-app-jsonrpc` | WT outer framing remains `webtransport`. | WT outer framing is interpreted as app JSON-RPC. |
| `tst:binary-bytes-text-do-not-collapse` | Binary/bytes/text require explicit handling. | Runtime coerces between them without declaration. |
| `tst:framing-token-is-not-support-proof` | Token presence alone does not mark support. | Runtime claims support because token exists in schema. |

## Invariants

- No unsupported framing fallback.
- Framing token presence is not implementation proof.
- WebTransport outer framing and app-level inner framing remain separate.
- WebSocket JSON-RPC requires negotiated subprotocol.
- Binary, bytes, and text do not collapse without explicit contract.

## Notes

This section is a guardrail for transport equivalence. Equivalent operation
bindings are valid only when their framing support is implemented and tested.
