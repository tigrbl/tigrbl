from __future__ import annotations

from importlib import import_module
from typing import Any, Dict, List, Mapping

try:  # pragma: no cover - additive optional integration
    _runtime_rust = import_module("tigrbl_runtime.rust")
    ExecutionBackend = _runtime_rust.ExecutionBackend
    RustBackendConfig = _runtime_rust.RustBackendConfig
except Exception:  # pragma: no cover
    ExecutionBackend = RustBackendConfig = None

from .rust_compile import (
    build_rust_kernel,
    build_rust_parity_snapshot,
    normalize_rust_spec,
)
from .rust_plan import RustPlan

_LAZY_EXPORTS = {
    "Kernel": "core",
    "OpView": "models",
    "PackedKernel": "models",
    "SchemaIn": "models",
    "SchemaOut": "models",
}

_default_kernel = None


def _kernel():
    global _default_kernel
    if _default_kernel is None:
        kernel_cls = __getattr__("Kernel")
        _default_kernel = kernel_cls()
    return _default_kernel


def __getattr__(name: str) -> Any:
    module_name = _LAZY_EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(name)
    module = import_module(f"{__name__}.{module_name}")
    value = getattr(module, name)
    globals()[name] = value
    return value


def get_cached_specs(model: type) -> Mapping[str, Any]:
    return _kernel().get_specs(model)


def build_phase_chains(model: type, alias: str) -> Dict[str, List[Any]]:
    return _kernel()._build_op(model, alias)


def build_kernel_plan(app: Any):
    return _kernel().kernel_plan(app)


def build_packed_kernel(app: Any):
    return _kernel().kernel_plan(app).packed


def plan_labels(model: type, alias: str) -> list[str]:
    return _kernel().plan_labels(model, alias)


__all__ = [
    "ExecutionBackend",
    "Kernel",
    "RustBackendConfig",
    "RustPlan",
    "OpView",
    "PackedKernel",
    "SchemaIn",
    "SchemaOut",
    "build_kernel_plan",
    "build_rust_kernel",
    "build_rust_parity_snapshot",
    "build_packed_kernel",
    "get_cached_specs",
    "build_phase_chains",
    "normalize_rust_spec",
    "plan_labels",
    "segment_fusion",
    "transport_atoms",
    "transport_events",
    "webtransport_events",
]

_default_kernel = _kernel()
