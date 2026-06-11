from __future__ import annotations

import logging
from typing import Any, Mapping, Optional, Union

from tigrbl_kernel.helpers import _g, _run_chain
from tigrbl_ops_oltp.crud import ops as _crud_ops
from tigrbl_ops_oltp.crud.helpers.model import _coerce_pk_value, _single_pk_name

from .types import AsyncSession, PhaseChains, Session, _Ctx

logger = logging.getLogger(__name__)

_OPVIEW_CACHE_ATTR = "__tigrbl_cached_opviews__"
_LOG_NOISE_REDUCED = False
_NOISY_TIGRBL_LOGGERS = (
    "tigrbl_ops_oltp.crud.helpers.model",
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


async def _crud_result_fallback(ctx: _Ctx, current_result: Any) -> Any:
    alias = str(ctx.get("op") or "").lower()
    if alias not in {"read", "update", "replace"}:
        return current_result

    model = ctx.get("model")
    db = ctx.get("db")
    if not isinstance(model, type) or db is None:
        return current_result

    try:
        pk_name = _single_pk_name(model)
    except Exception:
        return current_result

    payload = ctx.get("payload")
    path_params = ctx.get("path_params")
    ident = None
    if isinstance(path_params, Mapping) and pk_name in path_params:
        ident = path_params.get(pk_name)
    elif isinstance(payload, Mapping) and pk_name in payload:
        ident = payload.get(pk_name)
    if ident is None:
        return current_result

    ident = _coerce_pk_value(model, ident)

    if alias == "read":
        needs_fallback = current_result is None
        if isinstance(current_result, Mapping):
            if pk_name not in current_result:
                needs_fallback = True
            else:
                data_keys = [k for k in current_result.keys() if k != pk_name]
                if data_keys and all(current_result.get(k) is None for k in data_keys):
                    needs_fallback = True
        if not needs_fallback:
            return current_result
        return await _crud_ops.read(model, ident, db)

    if current_result is None and isinstance(payload, Mapping):
        if alias == "update":
            return await _crud_ops.update(model, ident, dict(payload), db)
        return await _crud_ops.replace(model, ident, dict(payload), db)

    return current_result


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
    "_OPVIEW_CACHE_ATTR",
    "_crud_result_fallback",
    "_default_status_for_alias",
    "_maybe_await",
    "_normalize_result_payload",
    "_reduce_log_noise",
    "_rollback_if_owned",
    "_unwrap_ctx_result",
    "logger",
]
