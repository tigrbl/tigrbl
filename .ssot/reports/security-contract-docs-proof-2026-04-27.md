# Security Contract Documentation Proof

## Context

- Date: 2026-04-27
- Scope: generated OpenAPI/OpenRPC security metadata and pre-transaction security dependency execution
- Command path: `.venv/Scripts/python.exe`

## Executed Checks

```text
.venv\Scripts\python.exe -m pytest pkgs/core/tigrbl_tests/tests/unit/test_docs_security_parity.py pkgs/core/tigrbl_tests/tests/unit/test_openapi_documentation_security_behavior.py pkgs/core/tigrbl_tests/tests/unit/test_openrpc_documentation_security_behavior.py -q
```

Result:

```text
4 passed in 0.82s
```

```text
.venv\Scripts\python.exe -m pytest pkgs/core/tigrbl_tests/tests/test_secdeps_execute_in_pre_tx.py -q
```

Result:

```text
5 passed in 0.10s
```

## Findings

- OpenAPI security requirements are emitted from `OpSpec.secdeps`.
- OpenRPC method security requirements are emitted from `OpSpec.secdeps`.
- OpenAPI and OpenRPC security schemes cover HTTP Basic, HTTP Bearer, API key, OAuth2, OpenID Connect, and mutual TLS dependencies.
- Router route metadata is not treated as the source of truth for operation security; operation specs remain the canonical source.
- Security dependencies execute before transaction begin and abort handler execution on failure.

## Remaining Gap

Generated operations without security dependencies remain public. That keeps the unauthenticated REST and JSON-RPC read issues open until the project chooses and implements one explicit policy: generated CRUD protected by default, or generated CRUD public by default with contract-level public operation declarations.
