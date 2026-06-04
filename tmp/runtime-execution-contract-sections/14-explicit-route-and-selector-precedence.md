# 14 Explicit Route And Selector Precedence

This section proposes compile-time selector collision and shadowing control.

## Purpose

The goal is not global `dispatch uniqueness`. REST paths, JSON-RPC methods,
WebSocket paths, stream paths, and WebTransport lanes are separate selector
namespaces. The goal is to prevent accidental ambiguity and hidden shadowing
inside a namespace and precedence scope.

## Proposed ADRs

| ADR | Decision | Why it is needed |
|---|---|---|
| `adr:selector-namespaces-and-shadowing-control` | Selectors are governed by namespace and explicit shadowing policy. | Prevents accidental collisions while allowing intended overrides. |
| `adr:compiled-selector-resolution-is-authoritative` | Compiled selector resolution tables are runtime authority. | Keeps hot-path dispatch deterministic and inspectable. |

## Proposed SPECs

| SPEC | Scope | Required content |
|---|---|---|
| `spc:selector-namespace-contract` | Selector namespaces. | REST method/path, JSON-RPC method/endpoint, WS path/subprotocol, stream path, WT lane/session selectors. |
| `spc:selector-collision-policy` | Collision rules. | Same namespace same selector same op allowed, different op requires override, missing policy fails compile. |
| `spc:route-shadowing-declaration-contract` | Explicit shadow/override metadata. | Policy fields, precedence owner, previous owner, replacement owner, and traceability. |
| `spc:nested-router-precedence-contract` | Nested app/router/table precedence. | Precedence order, inherited specs, generated defaults, custom ops, and conflict behavior. |
| `spc:compiled-selector-resolution-table` | Runtime plan selector table. | Selector-to-`op_id`, namespace, precedence source, shadow policy, and diagnostics. |

## Proposed Features

| Feature | Description | Implementation direction |
|---|---|---|
| `feat:selector-namespace-model` | Model selector namespaces explicitly. | Extend kernel dispatch metadata and diagnostics. |
| `feat:compile-time-selector-collision-check` | Detect selector collisions before runtime. | Add compile checks for route/path/method/rpc/ws selectors. |
| `feat:explicit-shadow-policy` | Allow only declared shadowing/override. | Add spec metadata and compile diagnostics. |
| `feat:nested-router-precedence-visibility` | Show precedence source in compiled plan. | Include app/router/table/op source metadata. |
| `feat:selector-resolution-hot-table` | Precompute runtime dispatch tables. | Keep hot path table-driven with no dynamic precedence guessing. |

## Proposed Tests

| Test | Valid scenario | Invalid scenario |
|---|---|---|
| `tst:rest-jsonrpc-selectors-are-separate-namespaces` | REST `GET /widgets/{id}` and JSON-RPC `Widget.read` both point to same `op_id`. | Compiler treats cross-namespace aliases as collision. |
| `tst:same-selector-same-op-id-allowed` | Duplicate selector resolves to same `op_id` under allowed composition. | Same semantic op is rejected only due to duplicate alias. |
| `tst:same-selector-different-op-id-requires-override` | Same selector different op compiles only with explicit override. | Different op silently claims same selector. |
| `tst:generated-crud-cannot-shadow-custom-op-silently` | CRUD default collision with custom op fails or requires declaration. | Generated default shadows custom op. |
| `tst:nested-router-precedence-visible-in-plan` | Compiled plan shows source and precedence of selected op. | Runtime chooses route with no visible source. |
| `tst:ambiguous-selector-fails-compile` | Ambiguous selector fails at compile time. | Runtime resolves ambiguity dynamically. |

## Invariants

- No hidden route precedence.
- Ambiguity fails at compile time unless explicitly governed.
- Selector resolution is precomputed and visible in the runtime plan.
- A selector collision is allowed only when it resolves to the same `op_id` or has explicit override policy.
- Selector namespaces are separate and must not be flattened.

## Notes

This feature supports hot-path throughput by moving selector resolution and
precedence checks into compilation instead of per-request runtime logic.
