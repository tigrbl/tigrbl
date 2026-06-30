from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType


STABLE_RFC = "stable-rfc"
ACTIVE_DRAFT = "active-draft"
INVALID_LOCAL = "invalid-local"

H11 = "h11"
H2 = "h2"
H3 = "h3"
H2_WS = "h2+ws"
H3_WS = "h3+ws"
H2_WT = "h2+wt"
H3_WT = "h3+wt"
H3_WT_WS = "h3+wt+ws"

_H3_BINDING_PROJECTIONS = frozenset({H3, H3_WS, H3_WT})


class BindingStackError(ValueError):
    """Raised when a Tigrbl binding stack projection is invalid."""


@dataclass(frozen=True)
class BindingStackProjection:
    stack: str
    valid: bool
    maturity: str
    binding_profile: str
    source: str
    requires_runtime_capability: bool
    notes: tuple[str, ...] = ()

    @property
    def is_stable_rfc(self) -> bool:
        return self.valid and self.maturity == STABLE_RFC

    @property
    def is_active_draft(self) -> bool:
        return self.valid and self.maturity == ACTIVE_DRAFT


_BINDING_STACKS = {
    H11: BindingStackProjection(H11, True, STABLE_RFC, "http-body", "RFC 9112", False),
    H2: BindingStackProjection(H2, True, STABLE_RFC, "http2-stream", "RFC 9113", False),
    H3: BindingStackProjection(H3, True, STABLE_RFC, "http3-quic-stream", "RFC 9114 over RFC 9000", False),
    H2_WS: BindingStackProjection(H2_WS, True, STABLE_RFC, "websocket-message-session", "RFC 8441", False),
    H3_WS: BindingStackProjection(H3_WS, True, STABLE_RFC, "websocket-message-session", "RFC 9220", False),
    H3_WT: BindingStackProjection(
        H3_WT,
        True,
        ACTIVE_DRAFT,
        "webtransport-lane",
        "draft-ietf-webtrans-http3-15",
        True,
        ("Project WT streams/datagrams as WebTransport lanes, not WebSocket frames.",),
    ),
    H2_WT: BindingStackProjection(
        H2_WT,
        True,
        ACTIVE_DRAFT,
        "webtransport-h2-capsule-lane",
        "draft-ietf-webtrans-http2-14",
        True,
        ("Project H2 WT fallback lanes through capsule-backed runtime capability.",),
    ),
    H3_WT_WS: BindingStackProjection(
        H3_WT_WS,
        False,
        INVALID_LOCAL,
        "invalid-nested-binding",
        "local taxonomy rejection",
        False,
        ("Bind H3 WebTransport and H3 WebSocket as separate projections.",),
    ),
}

BINDING_STACK_PROJECTIONS = MappingProxyType(_BINDING_STACKS)


def normalize_binding_stack(stack: str) -> str:
    if not isinstance(stack, str):
        raise BindingStackError("binding stack must be a string")
    return stack.strip().lower().replace(" ", "")


def classify_binding_stack(stack: str) -> BindingStackProjection:
    normalized = normalize_binding_stack(stack)
    try:
        return BINDING_STACK_PROJECTIONS[normalized]
    except KeyError as exc:
        raise BindingStackError(f"unknown binding stack: {stack!r}") from exc


def require_binding_stack(stack: str, *, allow_draft: bool = True) -> BindingStackProjection:
    projection = classify_binding_stack(stack)
    if not projection.valid:
        raise BindingStackError(f"invalid binding stack: {projection.stack}")
    if projection.requires_runtime_capability and not allow_draft:
        raise BindingStackError(f"binding stack requires draft runtime capability: {projection.stack}")
    return projection


def binding_stack_maturity(stack: str) -> str:
    return classify_binding_stack(stack).maturity


def compose_h3_binding_projections(*stacks: str) -> tuple[str, ...]:
    normalized = tuple(normalize_binding_stack(stack) for stack in stacks)
    if H3_WT_WS in normalized:
        raise BindingStackError("h3+wt+ws cannot be projected as one Tigrbl binding stack")
    unknown = tuple(stack for stack in normalized if stack not in _H3_BINDING_PROJECTIONS)
    if unknown:
        raise BindingStackError(f"not an H3 binding projection: {unknown[0]}")
    if len(set(normalized)) != len(normalized):
        raise BindingStackError("duplicate H3 binding projections are not allowed")
    return normalized
