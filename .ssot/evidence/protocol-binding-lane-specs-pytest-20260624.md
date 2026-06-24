# Protocol Binding Lane Specs Pytest Evidence

Date: 2026-06-24

Commit under test: 24bf4d5d Add protocol binding lane specs

Focused command:

```powershell
uv run pytest pkgs/core/tigrbl_core/tests/test_protocol_binding_appspec_schema.py pkgs/core/tigrbl_kernel/tests/test_protocol_binding_dispatch_contract.py pkgs/core/tigrbl_kernel/tests/test_compile_plan.py pkgs/core/tigrbl_tests/tests/unit/runtime/test_bindingspec_kernelplan_protocol_compilation_contract.py pkgs/core/tigrbl_tests/tests/unit/runtime/test_webtransport_lane_framing_policy.py pkgs/core/tigrbl_tests/tests/unit/runtime/test_unsupported_framing_fail_closed_contract.py pkgs/core/tigrbl_tests/tests/unit/runtime/test_framing_matrix_ssot_conformance.py pkgs/core/tigrbl_tests/tests/unit/runtime/test_runtime_frame_codec_contract.py pkgs/core/tigrbl_tests/tests/unit/runtime/test_binding_token_lowering_contract.py pkgs/core/tigrbl_tests/tests/unit/runtime/test_canonical_bindingspec_framing_policy.py pkgs/core/tigrbl_tests/tests/unit/runtime/test_contract_classification_consumption_policy.py pkgs/core/tigrbl_tests/tests/unit/runtime/test_session_leakage_prevention_contract.py --tb=short -q
```

Result: 178 passed in 0.81s.

Core/kernel command:

```powershell
uv run pytest pkgs/core/tigrbl_core/tests pkgs/core/tigrbl_kernel/tests --tb=short -q
```

Result: 687 passed in 2.74s.

Known unrelated runtime drift guard failure not included in this evidence scope:
`stream.resume.request` is currently unsupported by contract classification.
