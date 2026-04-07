"""Base runtime hook wrapper for Tigrbl v3."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from tigrbl_core._spec.hook_spec import HookSpec
from tigrbl_atoms import HookPhase, StepFn


@dataclass(frozen=True, slots=True)
class HookBase(HookSpec):
    """Base hook bound to a phase and one or more ops."""

    phase: HookPhase
    fn: StepFn
    order: int = 0
    when: Optional[object] = None
    name: Optional[str] = None
    description: Optional[str] = None


__all__ = ["HookBase"]
