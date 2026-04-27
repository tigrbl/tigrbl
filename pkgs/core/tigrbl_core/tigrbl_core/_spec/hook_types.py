from __future__ import annotations

from enum import Enum
from typing import Any, Awaitable, Callable, Tuple

from tigrbl_typing.phases import normalize_phase


class HookPhase(str, Enum):
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


HookPhases: Tuple[HookPhase, ...] = tuple(HookPhase)
StepFn = Callable[[Any], Awaitable[Any] | Any]
HookPredicate = Callable[[Any], bool]

__all__ = ["HookPhase", "HookPhases", "StepFn", "HookPredicate"]
