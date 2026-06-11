from __future__ import annotations

import pytest

from tigrbl_runtime import runtime as runtime_api
from tigrbl_runtime.executors.kernel_executor import _run, _run_phase_chain


def test_runtime_api_does_not_export_kernel_planning_shims() -> None:
    for name in ("Kernel", "build_phase_chains", "get_cached_specs", "_default_kernel"):
        with pytest.raises(AttributeError):
            getattr(runtime_api, name)


def test_runtime_executor_methods_remain_runtime_owned() -> None:
    assert _run.__module__ == "tigrbl_runtime.executors.kernel_executor"
    assert _run_phase_chain.__module__ == "tigrbl_runtime.executors.kernel_executor"
