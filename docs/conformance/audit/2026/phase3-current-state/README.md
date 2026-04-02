# Phase 3 audit evidence

This directory contains the evidence bundle captured while producing the Phase 3 authoritative current-state audit.

## Audit command set used for this checkpoint

### Targeted pytest slice

The following focused slice was executed against the restored Phase 2 checkpoint after installing SQLAlchemy as a missing audit dependency:

```bash
pytest -q \
  pkgs/core/tigrbl_base/tests/test_security_base.py \
  pkgs/core/tigrbl_tests/tests/security/test_schemes.py \
  pkgs/core/tigrbl_tests/tests/unit/test_system_docs_builders.py \
  pkgs/core/tigrbl_tests/tests/unit/test_openapi_documentation_security_behavior.py \
  pkgs/core/tigrbl_tests/tests/unit/test_openrpc_documentation_security_behavior.py \
  pkgs/core/tigrbl_tests/tests/unit/test_jsonrpc_openrpc.py \
  pkgs/core/tigrbl_tests/tests/request/test_request_response_conveniences.py \
  pkgs/core/tigrbl_tests/tests/request/test_request_transport_convenience_dot_notation.py \
  pkgs/core/tigrbl_tests/tests/response/test_response_transport_convenience_dot_notation.py \
  pkgs/core/tigrbl_tests/tests/unit/test_stdapi_transport_asgi_wsgi.py
```

Result recorded in `phase3_targeted_pytest.log`:

- 31 passed
- 12 failed
- 8 xfailed

The failing tests all share the same root failure in request-time compilation:

- `pkgs/core/tigrbl_runtime/tigrbl_runtime/runtime/runtime.py:48`
- `AttributeError: 'NoneType' object has no attribute 'kernel_plan'`

### Policy validation

The policy validators were executed both before and after cleanup.

Preserved logs:

- `validate_package_layout.log`
- `validate_doc_pointers.log`
- `lint_claim_language.log`
- `validate_root_clutter_preclean.log`
- `validate_root_clutter.log`

`validate_root_clutter_preclean.log` intentionally captures the test-generated clutter discovered after pytest. The final clean-tree rerun in `validate_root_clutter.log` is the authoritative post-clean validation result for this checkpoint.
