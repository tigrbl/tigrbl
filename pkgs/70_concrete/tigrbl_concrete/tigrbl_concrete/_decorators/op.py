"""Operation-related decorators for Tigrbl v3."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Callable, Iterable, Optional, Sequence, Union

from tigrbl_core._spec.binding_spec import (
    Exchange,
    Framing,
    FramingSpec,
    HttpStreamBindingSpec,
    SseBindingSpec,
    TransportBindingSpec,
    WebTransportBindingSpec,
    WsBindingSpec,
    framing_spec_from_kind,
)
from tigrbl_core._spec.op_spec import (
    Arity,
    OpSpec,
    PersistPolicy,
    TargetOp,
    TxScope,
)
from tigrbl_core._spec.op_utils import (
    _maybe_await as _core_maybe_await,
    _normalize_persist as _core_normalize_persist,
    _unwrap as _core_unwrap,
)
from tigrbl_core._spec.schema_spec import SchemaArg


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------


def _unwrap(obj: Any) -> Callable[..., Any]:
    """Get underlying function for (class|static)method; else return obj."""
    return _core_unwrap(obj)


def _ensure_cm(func: Any) -> Any:
    """Ensure method is a classmethod so it receives (cls, ctx)."""
    if isinstance(func, (classmethod, staticmethod)):
        return func
    return classmethod(func)


def _maybe_await(v):
    return _core_maybe_await(v)


# ---------------------------------------------------------------------------
# alias_ctx with optional rich overrides
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AliasDecl:
    alias: str
    # Optional overrides (lazy-capable schema args are fine; resolved later)
    request_schema: Optional[SchemaArg] = None
    response_schema: Optional[SchemaArg] = None
    persist: Optional[PersistPolicy] = None
    arity: Optional[Arity] = None
    rest: Optional[bool] = None


def alias(name: str, **kw) -> AliasDecl:
    """Convenience helper: alias('get', response_schema=..., rest=False)."""
    return AliasDecl(alias=name, **kw)


def alias_ctx(**verb_to_alias_or_decl: Union[str, AliasDecl]):
    """Class decorator mapping canonical verbs → aliases with optional overrides."""

    def deco(cls: type):
        amap = dict(getattr(cls, "__tigrbl_aliases__", {}) or {})
        overrides = dict(getattr(cls, "__tigrbl_alias_overrides__", {}) or {})

        for canon, value in verb_to_alias_or_decl.items():
            if isinstance(value, AliasDecl):
                amap[canon] = value.alias
                overrides[canon] = {
                    "request_schema": value.request_schema,
                    "response_schema": value.response_schema,
                    "persist": value.persist,
                    "arity": value.arity,
                    "rest": value.rest,
                }
            elif isinstance(value, str):
                amap[canon] = value
            else:
                raise TypeError(
                    f"alias_ctx[{canon}] must be str or AliasDecl, got {type(value)}"
                )

        setattr(cls, "__tigrbl_aliases__", amap)
        setattr(cls, "__tigrbl_alias_overrides__", overrides)
        # Alias maps are rebuilt from class metadata at bind-time.
        return cls

    return deco


# ---------------------------------------------------------------------------
# op_alias (class decorator): attach an OpSpec alias to the model
# ---------------------------------------------------------------------------


def op_alias(
    *,
    alias: str,
    target: TargetOp,
    arity: Arity | None = None,
    persist: PersistPolicy = "default",
    request_model: SchemaArg | None = None,
    response_model: SchemaArg | None = None,
    http_methods: Sequence[str] | None = None,
    tags: Sequence[str] | None = None,
):
    """Class decorator to declare an alias for an operation."""

    def deco(table_cls: type):
        ops = list(getattr(table_cls, "__tigrbl_ops__", ()))
        inferred_arity = arity or _infer_arity(target)
        if arity is None and target == "custom" and table_cls.__name__.endswith("App"):
            inferred_arity = "collection"

        spec = OpSpec(
            alias=alias,
            target=target,
            table=table_cls,
            arity=inferred_arity,
            persist=_normalize_persist(persist),
            request_model=request_model,
            response_model=response_model,
            http_methods=tuple(http_methods) if http_methods else None,
            tags=tuple(tags or ()),
        )
        ops.append(spec)
        table_cls.__tigrbl_ops__ = tuple(ops)
        return table_cls

    return deco


# ---------------------------------------------------------------------------
# op_ctx (single path: target + arity) with schema overrides
# ---------------------------------------------------------------------------


def op_ctx(
    *,
    bind: Any | Iterable[Any] | None = None,
    bindings: TransportBindingSpec | Iterable[TransportBindingSpec] | None = None,
    alias: Optional[str] = None,
    target: Optional[TargetOp] = None,
    arity: Optional[Arity] = None,
    exchange: Exchange = "request_response",
    tx_scope: TxScope = "inherit",
    subevents: Sequence[str] | None = None,
    http_methods: Sequence[str] | None = None,
    rest: Optional[bool] = None,
    request_schema: Optional[SchemaArg] = None,
    response_schema: Optional[SchemaArg] = None,
    persist: Optional[PersistPolicy] = None,
    status_code: Optional[int] = None,
    security_deps: Sequence[Any] | None = None,
):
    """Declare a ctx-only operation whose body is `(cls, ctx)`."""

    def deco(fn):
        cm = _ensure_cm(fn)
        f = _unwrap(cm)
        f.__tigrbl_ctx_only__ = True
        resolved_target = target or "custom"
        inferred_arity = arity or _infer_arity(resolved_target)
        if (
            arity is None
            and resolved_target == "custom"
            and bind is not None
            and any(
                isinstance(obj, type) and obj.__name__.endswith("App")
                for obj in (
                    bind
                    if isinstance(bind, Iterable) and not isinstance(bind, (str, bytes))
                    else [bind]
                )
            )
        ):
            inferred_arity = "collection"

        if alias is not None:
            resolved_alias = alias
        elif resolved_target != "custom":
            resolved_alias = resolved_target
        elif bind is not None:
            resolved_alias = f.__name__
        else:
            resolved_alias = "custom"

        spec = OpSpec(
            alias=resolved_alias,
            target=resolved_target,
            arity=inferred_arity,
            bindings=_normalize_bindings(bindings),
            exchange=exchange,
            tx_scope=tx_scope,
            subevents=tuple(subevents or ()),
            http_methods=tuple(http_methods) if http_methods else None,
            expose_routes=True if rest is None else bool(rest),
            request_model=request_schema,
            response_model=response_schema,
            persist=_normalize_persist(persist),
            status_code=status_code,
            security_deps=tuple(security_deps or ()),
        )
        f.__tigrbl_op_spec__ = spec
        # Backward-compatible attr name; value is always OpSpec.
        f.__tigrbl_op_decl__ = spec

        if bind is not None:
            targets = _bind_targets(bind)
            for obj in targets:
                setattr(obj, f.__name__, cm)
                if isinstance(obj, type):
                    _register_bound_op(
                        obj,
                        spec,
                        f,
                        arity_was_explicit=arity is not None,
                        persist_was_explicit=persist is not None,
                        rest_was_explicit=rest is not None,
                    )
                    _refresh_bound_ops(obj)

        return cm

    return deco


# ---------------------------------------------------------------------------
# Collection helpers
# ---------------------------------------------------------------------------

_COLLECTION_VERBS = {
    "create",
    "list",
    "bulk_create",
    "bulk_update",
    "bulk_replace",
    "bulk_merge",
    "bulk_delete",
    "clear",
    "merge",
}


def _infer_arity(target: str) -> str:
    if target == "custom":
        return "collection"
    return "collection" if target in _COLLECTION_VERBS else "member"


def _normalize_persist(p) -> str:
    return _core_normalize_persist(p)


def _normalize_bindings(
    value: TransportBindingSpec | Iterable[TransportBindingSpec] | None,
) -> tuple[TransportBindingSpec, ...]:
    if value is None:
        return ()
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
        return tuple(value)
    return (value,)


def _bind_targets(bind: Any | Iterable[Any]) -> tuple[Any, ...]:
    if isinstance(bind, Iterable) and not isinstance(bind, (str, bytes)):
        return tuple(bind)
    return (bind,)


def _register_bound_op(
    model: type,
    spec: OpSpec,
    func: Callable[..., Any],
    *,
    arity_was_explicit: bool,
    persist_was_explicit: bool,
    rest_was_explicit: bool,
) -> None:
    registered = _registered_bound_spec(
        model,
        spec,
        func,
    )
    ops = list(getattr(model, "__tigrbl_ops__", ()) or ())
    key = (registered.alias, registered.target)
    for index, existing in enumerate(ops):
        existing_key = (
            getattr(existing, "alias", None),
            getattr(existing, "target", None),
        )
        if existing_key == key:
            ops[index] = _merge_registered_bound_spec(
                existing,
                registered,
                arity_was_explicit=arity_was_explicit,
                persist_was_explicit=persist_was_explicit,
                rest_was_explicit=rest_was_explicit,
            )
            break
    else:
        ops.append(registered)
    model.__tigrbl_ops__ = tuple(ops)


def _registered_bound_spec(
    model: type,
    spec: OpSpec,
    func: Callable[..., Any],
) -> OpSpec:
    try:
        from tigrbl_core._spec.op_spec import _wrap_ctx_core

        handler = _wrap_ctx_core(model, func)
    except Exception:
        handler = None
    return replace(
        spec,
        table=model,
        handler=handler,
        core=handler,
        core_raw=handler,
    )


def _merge_registered_bound_spec(
    existing: OpSpec,
    registered: OpSpec,
    *,
    arity_was_explicit: bool,
    persist_was_explicit: bool,
    rest_was_explicit: bool,
) -> OpSpec:
    existing_bindings = tuple(getattr(existing, "bindings", ()) or ())
    registered_bindings = tuple(getattr(registered, "bindings", ()) or ())
    bindings = registered_bindings or existing_bindings
    if existing_bindings and registered_bindings:
        bindings = tuple(dict.fromkeys((*existing_bindings, *registered_bindings)))

    return replace(
        registered,
        http_methods=registered.http_methods or existing.http_methods,
        bindings=bindings,
        path_suffix=registered.path_suffix
        if registered.path_suffix is not None
        else existing.path_suffix,
        tags=registered.tags or existing.tags,
        status_code=registered.status_code
        if registered.status_code is not None
        else existing.status_code,
        request_model=registered.request_model or existing.request_model,
        response_model=registered.response_model or existing.response_model,
        response=registered.response or existing.response,
        engine=registered.engine if registered.engine is not None else existing.engine,
        engine_name=registered.engine_name
        if registered.engine_name is not None
        else existing.engine_name,
        arity=registered.arity if arity_was_explicit else existing.arity,
        persist=registered.persist if persist_was_explicit else existing.persist,
        expose_routes=registered.expose_routes
        if rest_was_explicit
        else existing.expose_routes,
        expose_rpc=registered.expose_rpc
        if registered.expose_rpc is not None
        else existing.expose_rpc,
        expose_method=registered.expose_method
        if registered.expose_method is not None
        else existing.expose_method,
        deps=registered.deps or existing.deps,
        security_deps=registered.security_deps or existing.security_deps,
        secdeps=registered.secdeps or existing.secdeps,
        extra={**dict(getattr(existing, "extra", {}) or {}), **dict(registered.extra)},
    )


def _normalize_framing_arg(framing: Framing | FramingSpec | None) -> FramingSpec | None:
    return framing_spec_from_kind(framing)


def websocket_ctx(
    path: str,
    *,
    proto: str = "ws",
    framing: Framing | FramingSpec = "text",
    subprotocols: Sequence[str] | None = None,
    **kwargs: Any,
):
    binding = WsBindingSpec(
        proto=proto,
        path=path,
        subprotocols=tuple(subprotocols or ()),
        framing=_normalize_framing_arg(framing),
    )
    exchange = kwargs.pop("exchange", binding.exchange)
    return op_ctx(bindings=(binding,), exchange=exchange, **kwargs)


def sse_ctx(
    path: str,
    *,
    proto: str = "http.sse",
    methods: Sequence[str] | None = None,
    **kwargs: Any,
):
    binding = SseBindingSpec(proto=proto, path=path, methods=tuple(methods or ("GET",)))
    exchange = kwargs.pop("exchange", binding.exchange)
    return op_ctx(bindings=(binding,), exchange=exchange, **kwargs)


def stream_ctx(
    path: str,
    *,
    proto: str = "http.stream",
    methods: Sequence[str] | None = None,
    framing: Framing | FramingSpec = "stream",
    **kwargs: Any,
):
    binding = HttpStreamBindingSpec(
        proto=proto,
        path=path,
        methods=tuple(methods or ("GET",)),
        framing=_normalize_framing_arg(framing),
    )
    exchange = kwargs.pop("exchange", binding.exchange)
    return op_ctx(bindings=(binding,), exchange=exchange, **kwargs)


def webtransport_ctx(
    path: str,
    *,
    proto: str = "webtransport",
    **kwargs: Any,
):
    binding = WebTransportBindingSpec(proto=proto, path=path)
    exchange = kwargs.pop("exchange", binding.exchange)
    return op_ctx(bindings=(binding,), exchange=exchange, **kwargs)


def _refresh_bound_ops(model: type) -> None:
    try:
        from tigrbl_core._spec.op_spec import _mro_collect_decorated_ops
        from tigrbl_concrete._mapping.model import (
            _bind_model_hooks,
            _materialize_handlers,
        )

        specs = tuple(_mro_collect_decorated_ops(model))
        _materialize_handlers(model, specs)
        _bind_model_hooks(model, specs)
    except Exception:
        # Best-effort refresh for dynamic binds.
        return


__all__ = [
    "alias",
    "alias_ctx",
    "op_alias",
    "op_ctx",
    "sse_ctx",
    "stream_ctx",
    "websocket_ctx",
    "webtransport_ctx",
]
