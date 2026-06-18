# Active Boundary Release Closure Pytest Evidence

Command:

```powershell
uv run pytest pkgs/core/tigrbl_tests/tests/unit/test_docs_security_parity.py pkgs/core/tigrbl_tests/tests/unit/test_openapi_documentation_security_behavior.py pkgs/core/tigrbl_tests/tests/unit/test_openrpc_documentation_security_behavior.py pkgs/core/tigrbl_tests/tests/i9n/test_types_deprecation_exports.py -q
```

Completed at: 2026-06-18T17:59:44-05:00

Result: passed

Summary:

- 5 passed
- 0 failed
- 0 skipped

Covered tests:

- `pkgs/core/tigrbl_tests/tests/unit/test_docs_security_parity.py::test_openapi_and_openrpc_security_are_derived_from_opspec_secdeps`
- `pkgs/core/tigrbl_tests/tests/unit/test_docs_security_parity.py::test_docs_ignore_router_security_dependency_metadata`
- `pkgs/core/tigrbl_tests/tests/unit/test_openapi_documentation_security_behavior.py::test_openapi_docs_cover_app_router_table_and_all_security_schemes`
- `pkgs/core/tigrbl_tests/tests/unit/test_openrpc_documentation_security_behavior.py::test_openrpc_docs_cover_app_router_table_and_all_security_schemes`
- `pkgs/core/tigrbl_tests/tests/i9n/test_types_deprecation_exports.py::test_types_deprecated_exports_only_exist_before_next_minor`
