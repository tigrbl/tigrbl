from __future__ import annotations

from enum import Enum
from typing import Literal, Tuple

PHASE_ALIASES = {
    "END_TX": "TX_COMMIT",
    "ON_END_TX_ERROR": "ON_TX_COMMIT_ERROR",
    "ON_ROLLBACK": "TX_ROLLBACK",
}


def normalize_phase(name: str | None) -> str | None:
    if name is None:
        return None
    return PHASE_ALIASES.get(str(name), str(name))

HookPhase = Literal[
    "PRE_TX_BEGIN",
    "START_TX",
    "PRE_HANDLER",
    "HANDLER",
    "POST_HANDLER",
    "PRE_COMMIT",
    "TX_COMMIT",
    "POST_COMMIT",
    "POST_RESPONSE",
    "ON_ERROR",
    "ON_PRE_TX_BEGIN_ERROR",
    "ON_START_TX_ERROR",
    "ON_PRE_HANDLER_ERROR",
    "ON_HANDLER_ERROR",
    "ON_POST_HANDLER_ERROR",
    "ON_PRE_COMMIT_ERROR",
    "ON_TX_COMMIT_ERROR",
    "ON_POST_COMMIT_ERROR",
    "ON_POST_RESPONSE_ERROR",
    "TX_ROLLBACK",
]

Phase = Literal[
    "INGRESS_BEGIN",
    "INGRESS_PARSE",
    "INGRESS_ROUTE",
    "PRE_TX_BEGIN",
    "START_TX",
    "PRE_HANDLER",
    "HANDLER",
    "POST_HANDLER",
    "PRE_COMMIT",
    "TX_COMMIT",
    "POST_COMMIT",
    "EGRESS_SHAPE",
    "EGRESS_FINALIZE",
    "POST_RESPONSE",
    "ON_ERROR",
    "ON_PRE_TX_BEGIN_ERROR",
    "ON_START_TX_ERROR",
    "ON_PRE_HANDLER_ERROR",
    "ON_HANDLER_ERROR",
    "ON_POST_HANDLER_ERROR",
    "ON_PRE_COMMIT_ERROR",
    "ON_TX_COMMIT_ERROR",
    "ON_POST_COMMIT_ERROR",
    "ON_POST_RESPONSE_ERROR",
    "TX_ROLLBACK",
]


class PHASE(str, Enum):
    PRE_TX_BEGIN = "PRE_TX_BEGIN"
    START_TX = "START_TX"
    PRE_HANDLER = "PRE_HANDLER"
    HANDLER = "HANDLER"
    POST_HANDLER = "POST_HANDLER"
    PRE_COMMIT = "PRE_COMMIT"
    TX_COMMIT = "TX_COMMIT"
    END_TX = "TX_COMMIT"
    POST_COMMIT = "POST_COMMIT"
    POST_RESPONSE = "POST_RESPONSE"
    ON_ERROR = "ON_ERROR"
    ON_PRE_TX_BEGIN_ERROR = "ON_PRE_TX_BEGIN_ERROR"
    ON_START_TX_ERROR = "ON_START_TX_ERROR"
    ON_PRE_HANDLER_ERROR = "ON_PRE_HANDLER_ERROR"
    ON_HANDLER_ERROR = "ON_HANDLER_ERROR"
    ON_POST_HANDLER_ERROR = "ON_POST_HANDLER_ERROR"
    ON_PRE_COMMIT_ERROR = "ON_PRE_COMMIT_ERROR"
    ON_TX_COMMIT_ERROR = "ON_TX_COMMIT_ERROR"
    ON_END_TX_ERROR = "ON_TX_COMMIT_ERROR"
    ON_POST_COMMIT_ERROR = "ON_POST_COMMIT_ERROR"
    ON_POST_RESPONSE_ERROR = "ON_POST_RESPONSE_ERROR"
    TX_ROLLBACK = "TX_ROLLBACK"
    ON_ROLLBACK = "TX_ROLLBACK"

    @classmethod
    def _missing_(cls, value: object):
        normalized = normalize_phase(str(value)) if value is not None else None
        if normalized != value:
            return cls(normalized)
        return None


HOOK_PHASES: Tuple[HookPhase, ...] = tuple(p.value for p in PHASE)
PHASES: Tuple[Phase, ...] = (
    "INGRESS_BEGIN",
    "INGRESS_PARSE",
    "INGRESS_ROUTE",
    "PRE_TX_BEGIN",
    "START_TX",
    "PRE_HANDLER",
    "HANDLER",
    "POST_HANDLER",
    "PRE_COMMIT",
    "TX_COMMIT",
    "POST_COMMIT",
    "EGRESS_SHAPE",
    "EGRESS_FINALIZE",
    "POST_RESPONSE",
    "ON_ERROR",
    "ON_PRE_TX_BEGIN_ERROR",
    "ON_START_TX_ERROR",
    "ON_PRE_HANDLER_ERROR",
    "ON_HANDLER_ERROR",
    "ON_POST_HANDLER_ERROR",
    "ON_PRE_COMMIT_ERROR",
    "ON_TX_COMMIT_ERROR",
    "ON_POST_COMMIT_ERROR",
    "ON_POST_RESPONSE_ERROR",
    "TX_ROLLBACK",
)

__all__ = [
    "PHASE",
    "PHASES",
    "HOOK_PHASES",
    "Phase",
    "HookPhase",
    "PHASE_ALIASES",
    "normalize_phase",
]
