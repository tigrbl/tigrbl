# Security Contract Auth Policy Parity Pytest Evidence

Date: 2026-05-06

Command:

```powershell
uv run pytest pkgs/core/tigrbl_tests/tests/unit/test_security_contract_auth_policy_parity.py
```

Result:

```text
4 passed in 1.14s
```

Covered regression tests:

- `test_openapi_generated_crud_declares_public_default_auth_surface`
- `test_openrpc_generated_methods_declare_public_default_auth_surface`
- `test_rest_generated_read_matches_auth_policy`
- `test_jsonrpc_generated_read_matches_auth_policy`

Verified behavior:

- Generated CRUD operations with no configured auth remain public and declare `x-tigrbl-auth.policy == "public-by-default"`.
- Generated REST reads with configured bearer auth reject unauthenticated requests with `401` or `403`.
- Generated JSON-RPC reads with configured bearer auth return a JSON-RPC error instead of data for unauthenticated requests.
- Protected generated OpenAPI/OpenRPC operations declare protected security metadata.
