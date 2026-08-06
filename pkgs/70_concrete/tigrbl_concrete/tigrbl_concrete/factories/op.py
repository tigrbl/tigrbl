from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Literal

from tigrbl_concrete._concrete._op import Op
from tigrbl_core._spec.binding_spec import Exchange, TransportBindingSpec
from tigrbl_core._spec.engine_spec import EngineCfg
from tigrbl_core._spec.hook_spec import HookSpec
from tigrbl_core._spec.hook_types import StepFn
from tigrbl_core._spec.op_spec import Arity, PersistPolicy, TargetOp, TxScope
from tigrbl_core._spec.response_spec import ResponseSpec
from tigrbl_core._spec.schema_spec import SchemaArg


def makeOp(
    *,
    alias: str,
    target: TargetOp = "custom",
    table: type | None = None,
    expose_routes: bool = True,
    expose_rpc: bool = True,
    expose_method: bool = True,
    bindings: Sequence[TransportBindingSpec] = (),
    exchange: Exchange = "request_response",
    tx_scope: TxScope = "inherit",
    subevents: Sequence[str] = (),
    engine: EngineCfg | None = None,
    engine_name: str | None = None,
    arity: Arity = "collection",
    http_methods: Sequence[str] | None = None,
    path_suffix: str | None = None,
    tags: Sequence[str] = (),
    status_code: int | None = None,
    response: ResponseSpec | None = None,
    persist: PersistPolicy = "default",
    batch: Mapping[str, Any] | bool | None = None,
    request_model: SchemaArg | None = None,
    response_model: SchemaArg | None = None,
    returns: Literal["raw", "model"] = "raw",
    handler: StepFn | None = None,
    hooks: Sequence[HookSpec] = (),
    core: StepFn | None = None,
    core_raw: StepFn | None = None,
    extra: Mapping[str, Any] | None = None,
    deps: Sequence[StepFn | str] = (),
    security_deps: Sequence[StepFn | str] = (),
) -> Op:
    """Make one explicit, typed concrete operation descriptor."""

    if not isinstance(alias, str) or not alias.strip():
        raise ValueError("operation alias must be a non-empty string")
    for name, value in (("handler", handler), ("core", core), ("core_raw", core_raw)):
        if value is not None and not callable(value):
            raise TypeError(f"operation {name} must be callable")

    resolved_core = core if core is not None else handler
    resolved_core_raw = core_raw if core_raw is not None else resolved_core
    return Op(
        alias=alias,
        target=target,
        table=table,
        expose_routes=expose_routes,
        expose_rpc=expose_rpc,
        expose_method=expose_method,
        bindings=tuple(bindings),
        exchange=exchange,
        tx_scope=tx_scope,
        subevents=tuple(subevents),
        engine=engine,
        engine_name=engine_name,
        arity=arity,
        http_methods=tuple(http_methods) if http_methods is not None else None,
        path_suffix=path_suffix,
        tags=tuple(tags),
        status_code=status_code,
        response=response,
        persist=persist,
        batch=batch,
        request_model=request_model,
        response_model=response_model,
        returns=returns,
        handler=handler,
        hooks=tuple(hooks),
        core=resolved_core,
        core_raw=resolved_core_raw,
        extra=dict(extra or {}),
        deps=tuple(deps),
        security_deps=tuple(security_deps),
    )


op = makeOp

__all__ = ["makeOp", "op"]
