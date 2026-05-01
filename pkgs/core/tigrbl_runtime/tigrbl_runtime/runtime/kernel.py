"""Compatibility wrapper for runtime kernel APIs.

Canonical kernel planning now lives in ``tigrbl_kernel``.
Runtime execution stays in ``tigrbl_runtime.executors``.
"""

from ..executors.kernel_executor import _run, _run_phase_chain

from tigrbl_kernel import (
    Kernel,
    _default_kernel,
    build_packed_kernel_measurement_view,
    build_phase_chains,
    get_cached_specs,
    measure_packed_kernel,
    packed_kernel_measurement,
    plan_labels,
)

__all__ = [
    "Kernel",
    "get_cached_specs",
    "_default_kernel",
    "build_packed_kernel_measurement_view",
    "build_phase_chains",
    "plan_labels",
    "measure_packed_kernel",
    "packed_kernel_measurement",
]


Kernel._run = _run
Kernel._run_phase_chain = _run_phase_chain
