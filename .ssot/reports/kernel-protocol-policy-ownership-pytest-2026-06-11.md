# Kernel Protocol Policy Ownership Pytest - 2026-06-11

Command:

```powershell
uv run pytest pkgs/core/tigrbl_kernel/tests/test_protocol_policy_ownership.py pkgs/core/tigrbl_tests/tests/unit/runtime/test_kernelplan_executor_runtime_shim_contract.py pkgs/core/tigrbl_runtime/tests/test_kernel_bridge.py pkgs/core/tigrbl_tests/tests/protocol/test_protocol_runtime_governance_contracts.py pkgs/core/tigrbl_tests/tests/unit/runtime/test_protocol_anchor_ordering_parity_contract.py pkgs/core/tigrbl_tests/tests/unit/runtime/test_dispatch_exchange_family_subevent_atoms_contract.py pkgs/core/tigrbl_tests/tests/unit/runtime/test_loop_ownership_mode_contract.py pkgs/core/tigrbl_tests/tests/unit/runtime/test_events_stages.py pkgs/core/tigrbl_tests/tests/unit/runtime/test_events_runtime_behavior.py pkgs/core/tigrbl_tests/tests/parity/test_hook_runtime_stage_parity.py pkgs/core/tigrbl_runtime/tests/test_channel_runtime_surface.py pkgs/core/tigrbl_tests/tests/unit/runtime/test_webtransport_session_multiplexing_policy.py pkgs/core/tigrbl_tests/tests/unit/runtime/test_transport_delivery_guarantees_contract.py pkgs/core/tigrbl_tests/tests/unit/runtime/test_session_leakage_prevention_contract.py
```

Result:

```text
99 passed, 1 xfailed in 0.99s
```

Additional dependency verification:

```powershell
uv run pytest pkgs/core/tigrbl_atoms/tests/test_declared_dependency_imports.py pkgs/core/tigrbl_kernel/tests/test_declared_dependency_imports.py pkgs/core/tigrbl_runtime/tests/test_declared_dependency_imports.py
```

Result:

```text
3 passed in 0.52s
```
