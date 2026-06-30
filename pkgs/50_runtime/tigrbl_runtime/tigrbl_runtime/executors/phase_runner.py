from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Mapping, MutableMapping, Optional, Union

from tigrbl_atoms.atoms.sys._db import _in_transaction
from tigrbl_atoms.types import build_error_ctx, error_phase_for, select_error_edge
from tigrbl_kernel.helpers import _g, _run_chain
from tigrbl_typing.status import create_standardized_error, to_rpc_error_payload

from ..config.constants import CTX_SKIP_PERSIST_FLAG
from ._invoke_support import (
    _default_status_for_alias as _default_status_for_alias,
    _maybe_await as _maybe_await,
    _normalize_result_payload as _normalize_result_payload,
    _reduce_log_noise as _reduce_log_noise,
    _rollback_if_owned as _rollback_if_owned,
    _unwrap_ctx_result as _unwrap_ctx_result,
    logger as logger,
)
from .types import AsyncSession, PhaseChains, Request, Session, _Ctx


async def _invoke(
    *,
    request: Optional[Request],
    db: Union[Session, AsyncSession, None],
    phases: Optional[PhaseChains],
    ctx: Optional[MutableMapping[str, Any]] = None,
) -> Any:
    """Execute an operation through explicit phases with strict write policies."""

    _reduce_log_noise()

    ctx = _Ctx.ensure(request=request, db=db, seed=ctx)
    if getattr(ctx, "app", None) is None and getattr(ctx, "router", None) is not None:
        ctx.app = ctx.router
    if getattr(ctx, "op", None) is None and getattr(ctx, "method", None) is not None:
        ctx.op = ctx.method
    env = ctx.get("env")
    op_name = getattr(ctx, "op", None) or getattr(ctx, "method", None)
    if env is None:
        ctx["env"] = SimpleNamespace(method=op_name)
    elif getattr(env, "method", None) in (None, "", "unknown"):
        try:
            setattr(env, "method", op_name)
        except Exception:
            ctx["env"] = SimpleNamespace(method=op_name)
    if getattr(ctx, "model", None) is None:
        obj = getattr(ctx, "obj", None)
        if obj is not None:
            ctx.model = type(obj)
    skip_persist: bool = bool(ctx.get(CTX_SKIP_PERSIST_FLAG) or ctx.get("skip_persist"))
    skip_ingress: bool = bool(ctx.get("skip_ingress"))
    skip_egress: bool = bool(ctx.get("skip_egress"))
    skip_post_commit: bool = bool(ctx.get("skip_post_commit"))
    if not callable(ctx.get("rpc_error_builder")):
        ctx["rpc_error_builder"] = lambda exc: to_rpc_error_payload(
            create_standardized_error(exc)
        )

    existed_tx_before = _in_transaction(db) if db is not None else False

    async def _run_phase(
        name: str,
        *,
        allow_flush: bool,
        allow_commit: bool,
        in_tx: bool,
        require_owned_for_commit: bool = True,
        nonfatal: bool = False,
        owns_tx_for_phase: Optional[bool] = None,
    ) -> None:
        chain = _g(phases, name)
        if not chain:
            return

        owns_tx_now = bool(owns_tx_for_phase)
        if owns_tx_for_phase is None:
            owns_tx_now = not existed_tx_before

        del allow_flush, allow_commit, require_owned_for_commit
        ctx.phase = name
        ctx.owns_tx = owns_tx_now

        try:
            await _run_chain(ctx, chain, phase=name)
        except Exception as exc:
            edge = select_error_edge(
                name,
                rollback_required=bool(in_tx and owns_tx_now),
            )
            build_error_ctx(
                ctx,
                exc,
                failed_phase=name,
                err_target=edge.target,
                rollback_required=edge.target.kind == "rollback",
            )
            if in_tx:
                await _rollback_if_owned(db, owns_tx_now, phases=phases, ctx=ctx)
            err_name = error_phase_for(name)
            try:
                await _run_chain(
                    ctx, _g(phases, err_name) or _g(phases, "ON_ERROR"), phase=err_name
                )
            except Exception:  # pragma: no cover
                pass
            if nonfatal:
                logger.exception("%s failed (nonfatal): %s", name, exc)
                return
            raise create_standardized_error(exc)

    if not skip_ingress:
        await _run_phase(
            "INGRESS_BEGIN", allow_flush=False, allow_commit=False, in_tx=False
        )
        await _run_phase(
            "INGRESS_PARSE", allow_flush=False, allow_commit=False, in_tx=False
        )
        await _run_phase(
            "INGRESS_ROUTE", allow_flush=False, allow_commit=False, in_tx=False
        )
    await _run_phase("PRE_TX_BEGIN", allow_flush=False, allow_commit=False, in_tx=False)

    if not skip_persist:
        await _run_phase(
            "START_TX",
            allow_flush=False,
            allow_commit=False,
            in_tx=False,
            require_owned_for_commit=False,
        )

    await _run_phase(
        "PRE_HANDLER", allow_flush=True, allow_commit=False, in_tx=not skip_persist
    )

    await _run_phase(
        "HANDLER", allow_flush=True, allow_commit=False, in_tx=not skip_persist
    )

    await _run_phase(
        "POST_HANDLER", allow_flush=True, allow_commit=False, in_tx=not skip_persist
    )

    await _run_phase(
        "PRE_COMMIT", allow_flush=False, allow_commit=False, in_tx=not skip_persist
    )

    if not skip_persist:
        # If this invocation started outside a transaction, the runtime owns the
        # commit decision even when the backend uses implicit/autobegin semantics.
        owns_tx_for_commit = not existed_tx_before
        await _run_phase(
            "TX_COMMIT",
            allow_flush=True,
            allow_commit=True,
            in_tx=True,
            require_owned_for_commit=False,
            owns_tx_for_phase=owns_tx_for_commit,
        )

    from types import SimpleNamespace as _NS

    if ctx.get("result") is None:
        fallback = (
            ctx.get("obj")
            or ctx.get("objs")
            or (
                ctx.get("temp", {}).get("egress", {}).get("result")
                if isinstance(ctx.get("temp"), Mapping)
                else None
            )
        )
        if fallback is not None:
            ctx["result"] = fallback

    serializer = ctx.get("response_serializer")
    current_result = ctx.get("result")
    temp = ctx.get("temp") if isinstance(ctx, Mapping) else None
    rpc_error = temp.get("rpc_error") if isinstance(temp, Mapping) else None
    response_state = getattr(ctx, "response", None)
    if current_result is None and response_state is not None:
        current_result = getattr(response_state, "result", None)
    if current_result is None:
        current_result = getattr(ctx, "obj", None)

    current_result = _unwrap_ctx_result(current_result)

    if isinstance(rpc_error, Mapping):
        ctx["result"] = None
    elif callable(serializer):
        try:
            ctx["result"] = serializer(current_result)
        except Exception:
            logger.exception("response serialization failed", exc_info=True)
    else:
        ctx["result"] = _normalize_result_payload(current_result)

    if getattr(ctx, "status_code", None) is None:
        ctx.status_code = _default_status_for_alias(
            getattr(ctx, "op", None), getattr(ctx, "target", None)
        )

    response_obj = getattr(ctx, "response", None)
    if response_obj is None:
        ctx.response = _NS(result=ctx.get("result"))
    else:
        setattr(response_obj, "result", ctx.get("result"))

    if not skip_post_commit:
        await _run_phase(
            "POST_COMMIT", allow_flush=True, allow_commit=False, in_tx=False
        )

    if not skip_egress:
        await _run_phase(
            "POST_RESPONSE",
            allow_flush=False,
            allow_commit=False,
            in_tx=False,
            nonfatal=True,
        )

        await _run_phase(
            "EGRESS_SHAPE", allow_flush=False, allow_commit=False, in_tx=False
        )
        await _run_phase(
            "EGRESS_FINALIZE", allow_flush=False, allow_commit=False, in_tx=False
        )
    if ctx.get("result") is not None and getattr(ctx, "response", None) is not None:
        setattr(ctx.response, "result", ctx.get("result"))

    release = None
    if isinstance(temp, Mapping):
        release = temp.pop("__sys_db_release__", None)
    if callable(release):
        release()

    if skip_egress:
        result_source = ctx.get("result")
        if result_source is None and getattr(ctx, "response", None) is not None:
            result_source = getattr(ctx.response, "result", None)
        result = _unwrap_ctx_result(result_source)
        result = _normalize_result_payload(result)
        if result is not None:
            ctx["result"] = result
            if getattr(ctx, "response", None) is not None:
                setattr(ctx.response, "result", result)
        return result

    if getattr(ctx, "response", None) is not None:
        result = getattr(ctx.response, "result", ctx.get("result"))
        result = _unwrap_ctx_result(result)
        if isinstance(result, Mapping) and {"status_code", "headers", "body"}.issubset(
            result
        ):
            body = result.get("body")
            if body is None:
                fallback = ctx.get("result")
                if fallback is not None:
                    result = fallback
        if result is not None:
            ctx["result"] = result
            setattr(ctx.response, "result", result)
        return result

    result = _unwrap_ctx_result(ctx.get("result"))
    if isinstance(result, Mapping) and {"status_code", "headers", "body"}.issubset(
        result
    ):
        body = result.get("body")
        if body is None:
            fallback = ctx.get("result")
            if fallback is not None:
                result = fallback
    if result is not None:
        ctx["result"] = result
    return result

__all__ = ["_invoke"]
