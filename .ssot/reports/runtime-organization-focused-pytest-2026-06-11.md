# Runtime Organization Focused Verification

Date: 2026-06-11

Scope:
- `pkgs/core/tigrbl_runtime/tigrbl_runtime/channel/asgi.py`
- `pkgs/core/tigrbl_runtime/tigrbl_runtime/channel/_asgi_*.py`
- `pkgs/core/tigrbl_runtime/tigrbl_runtime/executors/types.py`
- `pkgs/core/tigrbl_runtime/tigrbl_runtime/executors/ctx/*.py`
- `pkgs/core/tigrbl_runtime/tigrbl_runtime/executors/invoke.py`
- `pkgs/core/tigrbl_runtime/tigrbl_runtime/executors/_invoke_support.py`
- `pkgs/core/tigrbl_runtime/tigrbl_runtime/executors/packed.py`
- `pkgs/core/tigrbl_kernel/tigrbl_kernel/packed_access.py`
- `pkgs/core/tigrbl_kernel/tigrbl_kernel/packed_selectors.py`
- `pkgs/core/tigrbl_atoms/tigrbl_atoms/packed_inputs.py`
- `pkgs/core/tigrbl_atoms/tigrbl_atoms/atoms/transport/websocket_unary.py`

Commands:
- `uv run ruff check` on all touched runtime organization files.
- `uv run ruff check pkgs/core/tigrbl_runtime/tigrbl_runtime/executors/packed.py pkgs/core/tigrbl_kernel/tigrbl_kernel/packed_access.py pkgs/core/tigrbl_kernel/tigrbl_kernel/packed_selectors.py pkgs/core/tigrbl_atoms/tigrbl_atoms/packed_inputs.py pkgs/core/tigrbl_atoms/tigrbl_atoms/atoms/transport/websocket_unary.py pkgs/core/tigrbl_kernel/tests/test_kernelplan_executor_ownership_contract.py pkgs/core/tigrbl_atoms/tests/test_kernelplan_executor_atom_ownership_contract.py pkgs/core/tigrbl_tests/tests/unit/runtime/test_kernelplan_executor_runtime_shim_contract.py`
- `uv run pytest pkgs/core/tigrbl_runtime/tests/test_channel_runtime_surface.py pkgs/core/tigrbl_runtime/tests/test_ctx_promote_compat.py pkgs/core/tigrbl_runtime/tests/test_phase_context_assignment.py pkgs/core/tigrbl_runtime/tests/test_typed_error_edges.py pkgs/core/tigrbl_runtime/tests/test_packed_websocket_contracts.py pkgs/core/tigrbl_runtime/tests/test_packed_hot_run_dispatch.py pkgs/core/tigrbl_tests/tests/unit/runtime/test_kernelplan_executor_runtime_shim_contract.py pkgs/core/tigrbl_tests/tests/unit/runtime/test_packed_executor_hot_path_contract.py pkgs/core/tigrbl_tests/tests/unit/runtime/test_webtransport_session_multiplexing_policy.py pkgs/core/tigrbl_tests/tests/unit/runtime/test_transport_delivery_guarantees_contract.py pkgs/core/tigrbl_tests/tests/unit/runtime/test_session_leakage_prevention_contract.py`
- `uv run pytest pkgs/core/tigrbl_kernel/tests/test_kernelplan_executor_ownership_contract.py pkgs/core/tigrbl_atoms/tests/test_kernelplan_executor_atom_ownership_contract.py pkgs/core/tigrbl_tests/tests/unit/runtime/test_kernelplan_executor_runtime_shim_contract.py pkgs/core/tigrbl_tests/tests/unit/runtime/test_packed_executor_hot_path_contract.py`
- `rg -n "from tigrbl_runtime|import tigrbl_runtime" pkgs/core/tigrbl_kernel/tigrbl_kernel pkgs/core/tigrbl_atoms/tigrbl_atoms`

Results:
- Ruff: passed.
- Focused packed ownership pytest: 32 passed.
- Pytest: 71 passed, 1 xfailed.
- Reverse dependency search: no atoms/kernel imports of `tigrbl_runtime`.
