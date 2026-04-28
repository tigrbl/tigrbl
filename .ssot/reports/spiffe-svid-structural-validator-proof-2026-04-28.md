# SPIFFE SVID Structural Validator Proof

Run time: 2026-04-28T06:05:08.4734926-05:00

## Scope

This proof covers the `tigrbl_spiffe.identity.svid_validator.SvidValidator`
structural validation contract.

The validator now fails closed for unsupported SVID kinds, non-byte material,
malformed X.509 PEM and DER material, malformed JWT tokens, JWT `alg: none`,
expired JWT tokens, not-yet-valid JWT tokens, and JWT audience mismatches when
the caller supplies expected audiences.

This is structural validation evidence. It does not claim full cryptographic
chain validation or signature verification; those remain separate production
trust-bundle targets.

## Changed Files

- `pkgs/apps/tigrbl_spiffe/src/tigrbl_spiffe/identity/svid_validator.py`
- `pkgs/apps/tigrbl_spiffe/tests/test_svid_validator.py`
- `pkgs/apps/tigrbl_spiffe/tests/test_e2e_flow.py`

## Verification

Command:

```powershell
.\.venv\Scripts\python.exe -m pytest pkgs\apps\tigrbl_spiffe\tests\test_svid_validator.py -q --basetemp .tmp\pytest-spiffe-svid-validator
```

Result:

```text
10 passed in 0.30s
```

Command:

```powershell
.\.venv\Scripts\python.exe -m pytest pkgs\apps\tigrbl_spiffe\tests -q --basetemp .tmp\pytest-spiffe-package-slice
```

Result:

```text
24 passed in 0.85s
```

## Certification Impact

This closes a concrete SPIFFE extension hardening gap by replacing placeholder
token acceptance with deterministic structural checks and focused regression
coverage. Full SPIFFE package certification still requires separate trust-bundle,
chain validation, and production adapter evidence.
