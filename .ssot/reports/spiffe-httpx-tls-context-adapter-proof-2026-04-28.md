# SPIFFE HTTPX TLS Context Adapter Proof

Run time: 2026-04-28T04:05:49.4143069-05:00

## Scope

This proof covers the `tigrbl_spiffe.tls.adapters.httpx_client_with_tls` helper.
The adapter now obtains the SSL context from the provided TLS helper and passes
that context to `httpx.AsyncClient` through the `verify` argument.

## Changed files

- `pkgs/apps/tigrbl_spiffe/src/tigrbl_spiffe/tls/adapters.py`
- `pkgs/apps/tigrbl_spiffe/tests/test_adapters.py`

## Verification

Command:

```powershell
.\.venv\Scripts\python.exe -m pytest pkgs\apps\tigrbl_spiffe\tests\test_adapters.py -q --basetemp .tmp\pytest-spiffe-tls-adapter
```

Result:

```text
5 passed in 0.85s
```

## Certification impact

This closes a concrete SPIFFE adapter gap where the TLS helper created a
context but the HTTP client did not use it. It does not certify the full SPIFFE
package or strict SVID chain validation; those remain separate proof targets.
