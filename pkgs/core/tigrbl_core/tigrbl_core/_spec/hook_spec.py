"""Hook specification for Tigrbl v3."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Tuple

from .binding_spec import Exchange
from .hook_types import HookPhase, HookPredicate, StepFn

from .serde import SerdeMixin


@dataclass(frozen=True, slots=True)
class HookSpec(SerdeMixin):
    phase: HookPhase
    fn: StepFn
    ops: str | Tuple[str, ...] = "*"
    bindings: Tuple[str, ...] = ()
    framing: Tuple[str, ...] = ()
    exchange: Optional[Exchange] = None
    family: Tuple[str, ...] = ()
    subevents: Tuple[str, ...] = ()
    order: int = 0
    when: Optional[HookPredicate] = None
    name: Optional[str] = None
    description: Optional[str] = None

    @classmethod
    def collect(cls, owner: type) -> tuple["HookSpec", ...]:
        hooks: list[HookSpec] = []
        for hook in getattr(owner, "HOOKS", ()) or ():
            if isinstance(hook, HookSpec):
                hooks.append(hook)
            elif isinstance(hook, dict):
                hooks.append(cls(**hook))
        for _, attr in vars(owner).items():
            attr = getattr(attr, "__func__", attr)
            for item in tuple(getattr(attr, "__tigrbl_hook_decls__", ()) or ()):
                if isinstance(item, HookSpec):
                    hooks.append(item)
                elif isinstance(item, dict):
                    hooks.append(cls(**item))
            declared = getattr(attr, "__tigrbl_hook_spec__", None)
            if isinstance(declared, HookSpec):
                hooks.append(declared)
            elif isinstance(declared, dict):
                hooks.append(cls(**declared))
        return tuple(hooks)


_RUNTIME_OWNED_PHASES = frozenset(
    {
        "INGRESS_BEGIN",
        "INGRESS_PARSE",
        "INGRESS_ROUTE",
        "INGRESS_DISPATCH",
        "EGRESS_SHAPE",
        "EGRESS_FINALIZE",
        "EMIT",
        "POST_EMIT",
    }
)
_EXCHANGE_ALIASES = {
    "event_stream": "server_stream",
    "sse": "server_stream",
    "stream": "server_stream",
}


def _as_tuple(value: Any) -> tuple[str, ...]:
    if value in (None, "", ()):
        return ()
    if isinstance(value, str):
        return (value,)
    return tuple(str(item) for item in value)


def _hook_phase_value(value: Any) -> str:
    return str(getattr(value, "value", value))


def _normalize_exchange(value: Any) -> str | None:
    if value in (None, ""):
        return None
    token = str(value)
    return _EXCHANGE_ALIASES.get(token, token)


def validate_hook_legality(hook: HookSpec) -> None:
    phase = _hook_phase_value(getattr(hook, "phase", None))
    if phase in _RUNTIME_OWNED_PHASES:
        if phase == "POST_EMIT":
            raise ValueError(f"{phase} is a runtime-owned completion fence, not a hook phase")
        raise ValueError(f"{phase} is a runtime-owned canonical phase, not a hook phase")
    try:
        HookPhase(phase)
    except ValueError as exc:
        raise ValueError(f"{phase} is not a governed hook phase") from exc


def validate_hook_selector_legality(selector: dict[str, Any]) -> None:
    phase = selector.get("phase")
    if phase is not None:
        validate_hook_legality(HookSpec(phase=phase, fn=lambda _ctx: None))  # type: ignore[arg-type]


def matches_hook_selector(hook: HookSpec, metadata: dict[str, Any]) -> bool:
    validate_hook_legality(hook)
    hook_ops = getattr(hook, "ops", "*")
    if hook_ops != "*":
        op = metadata.get("op") or metadata.get("alias") or metadata.get("method")
        if op not in _as_tuple(hook_ops):
            return False

    bindings = _as_tuple(getattr(hook, "bindings", ()))
    if bindings and str(metadata.get("binding")) not in bindings:
        return False

    hook_exchange = _normalize_exchange(getattr(hook, "exchange", None))
    metadata_exchange = _normalize_exchange(metadata.get("exchange"))
    if hook_exchange is not None and metadata_exchange != hook_exchange:
        return False

    families = _as_tuple(getattr(hook, "family", ()))
    if families and str(metadata.get("family")) not in families:
        return False

    subevents = _as_tuple(getattr(hook, "subevents", ()))
    if subevents and str(metadata.get("subevent")) not in subevents:
        return False

    framings = _as_tuple(getattr(hook, "framing", ()))
    if framings and str(metadata.get("framing")) not in framings:
        return False

    return True


# Backwards compatibility alias
OpHook = HookSpec

__all__ = [
    "HookSpec",
    "OpHook",
    "matches_hook_selector",
    "validate_hook_legality",
    "validate_hook_selector_legality",
]
