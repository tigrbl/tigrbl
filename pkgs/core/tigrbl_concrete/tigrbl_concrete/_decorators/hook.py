"""Hook-related decorators for Tigrbl v3."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping, Sequence, Union

from tigrbl_core.config.constants import HOOK_DECLS_ATTR
from tigrbl_concrete._concrete import Hook
from tigrbl_runtime.runtime.exceptions import InvalidHookPhaseError
from tigrbl_atoms import HookPhase, HookPhases


def hook_ctx(
    ops: Union[str, Iterable[str]] = "*",
    *,
    phase: str | HookPhase | Enum,
    bindings: str | Sequence[str] | None = None,
    framing: str | Sequence[str] | None = None,
    exchange: str | None = None,
    family: str | Sequence[str] | None = None,
    subevents: str | Sequence[str] | None = None,
    selector: Mapping[str, Any] | None = None,
):
    """Declare a ctx-only hook for one/many ops at a given phase."""

    phase_value = phase.value if isinstance(phase, Enum) else phase
    try:
        normalized_phase = HookPhase(phase_value)
    except ValueError as exc:
        raise InvalidHookPhaseError(
            phase=str(phase_value),
            allowed_phases=tuple(p.value for p in HookPhases),
        ) from exc

    def deco(fn):
        from .op import _ensure_cm, _unwrap

        cm = _ensure_cm(fn)
        f = _unwrap(cm)
        f.__tigrbl_ctx_only__ = True
        lst = getattr(f, HOOK_DECLS_ATTR, [])
        merged_selector = dict(selector or {})
        if bindings is not None:
            merged_selector["bindings"] = bindings
        if exchange is not None:
            merged_selector["exchange"] = exchange
        if framing is not None:
            merged_selector["framing"] = framing
        if family is not None:
            merged_selector["family"] = family
        if subevents is not None:
            merged_selector["subevents"] = subevents
        lst.append(
            Hook(
                phase=normalized_phase,
                fn=f,
                ops=ops,
                bindings=_seqify_strings(merged_selector.get("bindings")),
                framing=_seqify_strings(merged_selector.get("framing")),
                exchange=merged_selector.get("exchange"),
                family=_seqify_strings(merged_selector.get("family")),
                subevents=_seqify_strings(merged_selector.get("subevents")),
            )
        )
        setattr(f, HOOK_DECLS_ATTR, lst)
        return cm

    return deco


def _seqify_strings(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    return tuple(str(item) for item in value)


__all__ = ["hook_ctx", "HOOK_DECLS_ATTR"]
