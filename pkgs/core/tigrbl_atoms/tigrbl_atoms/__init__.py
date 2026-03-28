from __future__ import annotations

from importlib import import_module
from typing import Any

from .fallback import native_atoms_enabled
from .native import register_native_atom, register_native_callback, register_native_hook

_LAZY_EXPORTS = {
    "PHASE_SEQUENCE": "types",
    "INGRESS_PHASES": "types",
    "HANDLER_PHASES": "types",
    "EGRESS_PHASES": "types",
    "HookPhase": "types",
    "HookPhases": "types",
    "VALID_HOOK_PHASES": "types",
    "StepFn": "types",
    "HookPredicate": "types",
}

__all__ = [
    "PHASE_SEQUENCE",
    "INGRESS_PHASES",
    "HANDLER_PHASES",
    "EGRESS_PHASES",
    "HookPhase",
    "HookPhases",
    "VALID_HOOK_PHASES",
    "StepFn",
    "HookPredicate",
    "native_atoms_enabled",
    "register_native_atom",
    "register_native_callback",
    "register_native_hook",
]


def __getattr__(name: str) -> Any:
    module_name = _LAZY_EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(name)
    module = import_module(f"{__name__}.{module_name}")
    value = getattr(module, name)
    globals()[name] = value
    return value
