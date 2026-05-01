# KernelPlan Executor Ownership Placement Pytest

Date: 2026-04-30

Command:

```powershell
$env:UV_CACHE_DIR='E:\swarmauri_github\tigrbl\.uv-cache'; uv run pytest pkgs/core/tigrbl_kernel/tests/test_kernelplan_executor_ownership_contract.py pkgs/core/tigrbl_atoms/tests/test_kernelplan_executor_atom_ownership_contract.py pkgs/core/tigrbl_tests/tests/unit/runtime/test_kernelplan_executor_runtime_shim_contract.py
```

Result:

- `6 passed in 0.27s`

Covered proof points:

- kernel compilers emit declarative execution artifacts for protocol chains, callback metadata, subevent handler tables, transaction-unit tables, transport segments, and fusion barriers
- atom-owned protocol, callback, channel, and transaction helpers execute concrete step behavior
- runtime protocol and helper surfaces delegate to atom-owned implementations
- packed executor source avoids imports of runtime shadow-compiler helper modules
