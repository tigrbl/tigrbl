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
    load_packed_kernel_hot_block,
    measure_packed_kernel,
    packed_kernel_measurement,
    plan_labels,
)

__all__ = [
    "Kernel",
    "get_cached_specs",
    "_default_kernel",
    "bind_runtime_executor",
    "build_packed_kernel_measurement_view",
    "build_phase_chains",
    "plan_labels",
    "load_packed_kernel_hot_block",
    "measure_packed_kernel",
    "packed_kernel_measurement",
]


def bind_runtime_executor(kernel_cls: type = Kernel) -> type:
    """Attach legacy runtime executor methods when an explicit bridge is needed."""

    kernel_cls._run = _run
    kernel_cls._run_phase_chain = _run_phase_chain
    return kernel_cls
