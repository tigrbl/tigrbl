# Runtime Documentation Endpoint Parity Proof

## Scope

This proof covers `feat:runtime-executor-doc-endpoint-parity-001`.

The verified contract is that runtime documentation endpoints remain isolated
from operation routing and expose the expected browser-facing documentation
surfaces for favicon, Swagger UIX, Lens UIX, and custom documentation UI paths.

## Verification

Command:

```powershell
.venv\Scripts\python.exe -m pytest pkgs/core/tigrbl_runtime/tests/test_rust_runtime_demo_docs_surface.py pkgs/core/tigrbl_tests/tests/unit/test_jsonrpc_openrpc.py -q --basetemp .tmp\pytest-runtime-doc-endpoint-proof
```

Result:

```text
25 passed in 10.39s
```

## Linked Tests

- `tst:rust-runtime-demo-favicon-routes`
- `tst:rust-runtime-demo-swagger-uix`
- `tst:rust-runtime-demo-lens-uix`
- `tst:rust-runtime-demo-console-logs`
- `tst:runtime-doc-endpoint-browser-contract`
- `tst:runtime-doc-endpoint-isolation-contract`
- `tst:runtime-doc-custom-ui-path-contract`

## Certification Impact

The feature was already implemented and had passing tests, but the active-line
certification profile still failed this row because no T2 satisfying claim was
linked to the feature. This artifact supports the missing claim edge without
changing runtime behavior or broadening the feature scope.
