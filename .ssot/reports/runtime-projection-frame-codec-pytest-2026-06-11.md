# Runtime Projection And Frame Codec Pytest Evidence

Date: 2026-06-11

Command:

```powershell
uv run pytest pkgs/core/tigrbl_tests/tests/unit/runtime/test_runtime_frame_codec_contract.py pkgs/core/tigrbl_tests/tests/unit/runtime/test_asgi_transport_projection_contract.py pkgs/core/tigrbl_tests/tests/unit/runtime/test_session_leakage_prevention_contract.py pkgs/core/tigrbl_kernel/tests/test_protocol_policy_ownership.py pkgs/core/tigrbl_atoms/tests/test_kernelplan_executor_atom_ownership_contract.py pkgs/core/tigrbl_runtime/tests/test_kernel_bridge.py pkgs/core/tigrbl_tests/tests/unit/runtime/test_kernelplan_executor_runtime_shim_contract.py pkgs/core/tigrbl_tests/tests/unit/runtime/test_events_stages.py pkgs/core/tigrbl_tests/tests/unit/runtime/test_events_runtime_behavior.py
```

Result: 62 passed in 0.56s.

Coverage:

- Runtime frame codec T0/T1/T2 contract assertions.
- ASGI transport projection contract assertions.
- WebTransport session leakage prevention contract assertions.
- Kernel protocol policy ownership assertions.
- Atom executor ownership assertions.
- Runtime compatibility shim assertions.
- Runtime event compatibility assertions.
