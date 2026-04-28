# Generated CRUD Auth Policy Proof

## Policy

Generated CRUD operations are public by default unless an application or router
configures security dependencies with `set_auth`, table/router/app
`security_deps`, or operation-level `secdeps`.

Documentation surfaces must make that policy explicit:

- public generated operations emit `x-tigrbl-auth.policy = public-by-default`;
- protected generated operations emit `x-tigrbl-auth.policy = protected`;
- protected OpenAPI and OpenRPC operations retain their concrete security
  requirements and schemes.

## Implementation

- `tigrbl_concrete.system.docs.surface.auth_surface` normalizes the auth policy
  projection.
- OpenAPI operations include `x-tigrbl-auth` beside `x-tigrbl-surface`.
- OpenRPC methods include `x-tigrbl-auth` beside `x-tigrbl-surface`.

## Verification

Command:

```text
uv run --package tigrbl_tests pytest pkgs/core/tigrbl_tests/tests/unit/test_operator_auth_surface_contracts.py pkgs/core/tigrbl_tests/tests/unit/test_jsonrpc_openrpc.py
```

Result:

```text
24 passed, 1 xfailed
```

The expected xfail is the existing authorize-hook rejection status gap for
`feat:operator-auth-dependency-hook-surface-001`; it is unrelated to the
generated CRUD public/protected documentation policy.
