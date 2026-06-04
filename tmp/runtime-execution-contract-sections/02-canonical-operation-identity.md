# 02 Canonical Operation Identity

This section proposes the identity contract that makes a Tigrbl operation the
same semantic operation across REST, JSON-RPC, WebSocket, stream, and
WebTransport bindings.

## Purpose

Transport selectors are not semantic identity. REST paths, JSON-RPC methods,
WebSocket paths, and WebTransport lanes are carrier-specific selectors. The
canonical operation id is the semantic center used by runtime plans, docs,
traces, replay, equivalence tests, rollups, and certification.

## Proposed ADRs

| ADR | Decision | Why it is needed |
|---|---|---|
| `adr:canonical-operation-id-is-semantic-identity` | `op_id` is the semantic identity of an operation. | Prevents transport-specific selectors from becoming conflicting operation identities. |
| `adr:transport-selectors-are-op-aliases` | REST method/path, JSON-RPC method, WebSocket path/subprotocol, stream path, and WebTransport lane selectors are aliases to `op_id`. | Allows cross-transport equivalence without conflating selector namespaces. |

## Proposed SPECs

| SPEC | Scope | Required content |
|---|---|---|
| `spc:canonical-operation-id-contract` | Shape and stability of `op_id`. | Naming rules, stability rules, custom op requirements, inheritance behavior, and deprecation behavior. |
| `spc:transport-selector-to-op-id-resolution` | Mapping selectors to `op_id`. | Selector namespace definitions, valid selector aliases, conflict rules, and runtime plan projection. |
| `spc:custom-operation-id-contract` | Identity rules for custom operations. | Required explicit ids, fallback naming rules, and docs/runtime parity. |

## Proposed Features

| Feature | Description | Implementation direction |
|---|---|---|
| `feat:canonical-op-id` | Add stable semantic operation ids to compiled plans. | Add `op_id` to operation metadata and runtime plan payloads. |
| `feat:transport-selector-op-id-aliasing` | Record selector aliases for each operation. | Extend kernel selector indices to retain alias-to-`op_id` mappings. |
| `feat:custom-op-canonical-id` | Require custom operations to have stable ids. | Reject or normalize custom ops missing canonical identity. |
| `feat:docs-runtime-op-id-parity` | Ensure OpenAPI/OpenRPC/docs ids match runtime ids. | Compare generated docs ids to compiled runtime plan ids. |

## Proposed Tests

| Test | Valid scenario | Invalid scenario |
|---|---|---|
| `tst:canonical-op-id-stable-across-rest-jsonrpc-ws` | `Widget.create` resolves to one `op_id` across REST, HTTP JSON-RPC, and WebSocket JSON-RPC. | Transport-specific operation ids differ for the same semantic operation. |
| `tst:custom-op-requires-canonical-op-id` | Custom op declares an explicit stable `op_id`. | Custom op compiles without a canonical id. |
| `tst:openapi-openrpc-runtime-op-id-parity` | OpenAPI operation id and OpenRPC method metadata point to compiled `op_id`. | Docs emit ids that do not match runtime dispatch ids. |
| `tst:transport-selector-aliases-resolve-to-op-id` | Each selector alias resolves to the intended `op_id`. | Selector alias resolves to different operation without explicit policy. |

## Invariants

- One canonical operation id represents one semantic operation.
- Transport selectors are aliases, not identities.
- The same `op_id` may have multiple transport aliases.
- Docs, traces, runtime plans, replay records, and rollups must use the same `op_id`.

## Notes

This is not the same as selector uniqueness. A REST selector and a JSON-RPC
method can both point to the same `op_id` because they live in different
selector namespaces.
