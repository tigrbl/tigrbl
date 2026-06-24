from __future__ import annotations

import logging
from typing import Any, Mapping, Optional, Union

from tigrbl_kernel.helpers import _g, _run_chain

from .types import AsyncSession, PhaseChains, Session, _Ctx

logger = logging.getLogger(__name__)

_LOG_NOISE_REDUCED = False
_NOISY_TIGRBL_LOGGERS = (
    "tigrbl_core._spec.column_spec",
)


def _reduce_log_noise() -> None:
    global _LOG_NOISE_REDUCED
    if _LOG_NOISE_REDUCED:
        return
    _LOG_NOISE_REDUCED = True
    for logger_name in _NOISY_TIGRBL_LOGGERS:
        target_logger = logging.getLogger(logger_name)
        if target_logger.getEffectiveLevel() <= logging.INFO:
            target_logger.setLevel(logging.WARNING)


def _default_status_for_alias(alias: Any, target: Any = None) -> int:
    verb = target if isinstance(target, str) and target else alias
    return 201 if verb in {"create", "bulk_create"} else 200


def _normalize_result_payload(payload: Any) -> Any:
    if (
        isinstance(payload, (str, int, float, bool, bytes, bytearray))
        or payload is None
    ):
        return payload
    if hasattr(payload, "status_code") and hasattr(payload, "body"):
        return payload
    if isinstance(payload, Mapping):
        return {str(k): _normalize_result_payload(v) for k, v in payload.items()}
    if isinstance(payload, (list, tuple, set)):
        return [_normalize_result_payload(v) for v in payload]

    model_dump = getattr(payload, "model_dump", None)
    if callable(model_dump):
        try:
            return _normalize_result_payload(model_dump())
        except Exception:
            pass

    obj_dict = getattr(payload, "__dict__", None)
    if isinstance(obj_dict, dict):
        data = {
            k: v
            for k, v in obj_dict.items()
            if not k.startswith("_") and not callable(v)
        }
        if data:
            return _normalize_result_payload(data)

    return str(payload)


def _unwrap_ctx_result(value: Any) -> Any:
    """Return user-facing payload when runtime atoms return context objects."""
    current = value
    for _ in range(8):
        if current is None or isinstance(
            current, (str, int, float, bool, Mapping, list, tuple, set)
        ):
            return current

        direct = getattr(current, "result", None)
        if direct is not None and direct is not current:
            current = direct
            continue

        payload = getattr(current, "response_payload", None)
        if payload is not None and payload is not current:
            current = payload
            continue

        response = getattr(current, "response", None)
        if response is not None:
            response_result = getattr(response, "result", None)
            if response_result is not None and response_result is not current:
                current = response_result
                continue

        bag = getattr(current, "bag", None)
        if isinstance(bag, Mapping) and bag.get("result") is not None:
            nested = bag.get("result")
            if nested is not current:
                current = nested
                continue

        return current

    return current


async def _maybe_await(value: Any) -> Any:
    if hasattr(value, "__await__"):
        return await value
    return value


async def _rollback_if_owned(
    db: Union[Session, AsyncSession, None],
    owns_tx: bool,
    *,
    phases: Optional[PhaseChains],
    ctx: Any,
) -> None:
    if not owns_tx or db is None:
        return
    if not _g(phases, "TX_ROLLBACK"):
        try:
            await _maybe_await(db.rollback())
        except Exception:  # pragma: no cover
            logger.exception("Rollback failed", exc_info=True)
    try:
        await _run_chain(ctx, _g(phases, "TX_ROLLBACK"), phase="TX_ROLLBACK")
    except Exception:  # pragma: no cover
        pass


__all__ = [
    "_default_status_for_alias",
    "_maybe_await",
    "_normalize_result_payload",
    "_reduce_log_noise",
    "_rollback_if_owned",
    "_unwrap_ctx_result",
    "logger",
]
