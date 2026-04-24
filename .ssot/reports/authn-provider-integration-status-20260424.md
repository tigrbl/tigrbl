# AuthN Provider Integration Status Evidence - 2026-04-24

## Scope

- Boundary: `bnd:authn-provider-integration-status-001`
- Feature: `feat:authn-provider-missing-credentials-status-001`
- Test file: `pkgs/core/tigrbl_tests/tests/i9n/test_authn_provider_integration.py`
- Focused case: `test_authn_unauthorized_errors`

## Result

Command:

```powershell
$env:UV_CACHE_DIR='.uv-cache'; uv run pytest -q pkgs/core/tigrbl_tests/tests/i9n/test_authn_provider_integration.py
```

Outcome:

```text
2 passed in 0.27s
```

The missing-credential request now returns `403 Forbidden`, while the wrong bearer token path still returns `401 Unauthorized`.
