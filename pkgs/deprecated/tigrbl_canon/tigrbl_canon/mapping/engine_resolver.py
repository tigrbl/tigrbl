# tigrbl/tigrbl/v3/engine/resolver.py
from __future__ import annotations

import asyncio
import inspect
import hashlib
import json
import logging
import threading
from typing import Any, Callable, Optional

from tigrbl_concrete._concrete._engine import (
    AsyncSession,
    Engine,
    Provider,
    Session,
    provider_from_spec,
)
from tigrbl_core._spec.engine_spec import EngineSpec, EngineCfg

logger = logging.getLogger("uvicorn")

# Registry with strict precedence: op > model > router > app
_LOCK = threading.RLock()
_DEFAULT: Optional[Provider] = None
_ROUTER: dict[int, Provider] = {}
_TAB: dict[Any, Provider] = {}
_OP: dict[tuple[Any, str], Provider] = {}
_PROV_BY_KEY: dict[tuple, Provider] = {}
_NAMED: dict[str, Provider] = {}
_DEFAULT_NAME: str | None = None
_ROUTER_NAME: dict[int, str] = {}
_TAB_NAME: dict[Any, str] = {}
_OP_NAME: dict[tuple[Any, str], str] = {}
_SCHEMA_REQUIRED: set[int] = set()
_SCHEMA_READY: set[int] = set()
_SECRET_KEYS = {
    "pwd",
    "password",
    "pass",
    "secret",
    "token",
    "routerkey",
    "router_key",
    "key",
}


def _stable_json(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, default=str, separators=(",", ":"))


def _hash_secret(value: object) -> str:
    encoded = str(value).encode("utf-8", "surrogatepass")
    return hashlib.sha256(encoded).hexdigest()


def _spec_key(spec: EngineSpec) -> tuple:
    mapping = dict(spec.mapping or {})
    norm: dict[str, object] = {}
    for key, value in mapping.items():
        if str(key).lower() in _SECRET_KEYS:
            norm[key] = {"__sha256__": _hash_secret(value)}
        else:
            norm[key] = value
    mapping_s = _stable_json(norm)
    pwd_hash = _hash_secret(spec.pwd) if spec.pwd is not None else None
    return (
        spec.kind,
        bool(spec.async_),
        spec.dsn,
        spec.path,
        bool(spec.memory),
        spec.pool,
        spec.user,
        pwd_hash,
        spec.host,
        spec.port,
        spec.name,
        int(spec.pool_size or 0),
        int(spec.max or 0),
        mapping_s,
    )


def _intern_provider(spec: EngineSpec, *, provider: Provider | None = None) -> Provider:
    key = _spec_key(spec)
    with _LOCK:
        existing = _PROV_BY_KEY.get(key)
        if existing is not None:
            return existing
        new_provider = provider or provider_from_spec(spec)
        _PROV_BY_KEY[key] = new_provider
        return new_provider


def _with_class(obj: Any) -> list[Any]:
    """Return ``obj`` and its class when ``obj`` is an instance.

    This allows resolution to honor providers registered on classes even when
    an instance is supplied at lookup time.
    """
    return [obj] if isinstance(obj, type) else [obj, type(obj)]


def _coerce(ctx: Optional[EngineCfg]) -> Optional[Provider]:
    """
    Promote an @engine_ctx value to a lazy Provider.
    """
    logger.debug("_coerce called with ctx=%r", ctx)
    if ctx is None:
        logger.debug("_coerce: ctx is None")
        return None
    if isinstance(ctx, Provider):
        logger.debug("_coerce: ctx is already a Provider")
        return _intern_provider(ctx.spec, provider=ctx)
    if isinstance(ctx, Engine):
        logger.debug("_coerce: ctx is an Engine; returning provider")
        return _intern_provider(ctx.spec, provider=ctx.provider)
    if isinstance(ctx, EngineSpec):
        logger.debug("_coerce: ctx is an EngineSpec; converting to provider")
        return _intern_provider(ctx)
    spec = EngineSpec.from_any(ctx)
    logger.debug("_coerce: EngineSpec.from_any returned %r", spec)
    return _intern_provider(spec) if spec else None


def _provider_id(provider: Provider) -> int:
    return id(provider)


def _provider_by_name(name: str) -> Provider:
    try:
        return _NAMED[name]
    except KeyError as exc:
        raise RuntimeError(f"Unknown engine name {name!r}") from exc


def _resolve_named(name: str | None) -> Provider | None:
    if name is None:
        return None
    return _provider_by_name(name)


def _is_schema_ready(provider: Provider) -> bool:
    pid = _provider_id(provider)
    return pid not in _SCHEMA_REQUIRED or pid in _SCHEMA_READY


def _require_ready(provider: Provider) -> None:
    if not _is_schema_ready(provider):
        spec = getattr(provider, "spec", None)
        name = getattr(spec, "name", None)
        suffix = f" engine={name!r}" if name else ""
        raise RuntimeError(f"Schema is not ready for resolved database provider.{suffix}")


# ---- registration -----------------------------------------------------------


def set_default(ctx: EngineCfg | None) -> None:
    """
    Register the app-level default Provider used when no API/table/op binds.
    """
    global _DEFAULT
    prov = _coerce(ctx)
    logger.debug("set_default: setting default provider to %r", prov)
    with _LOCK:
        _DEFAULT = prov


def register_engine(name: str, ctx: EngineCfg) -> Provider:
    """Register an engine inventory entry by canonical engine name."""

    if not isinstance(name, str) or not name.strip():
        raise ValueError("engine name must be a non-empty string")
    prov = _coerce(ctx)
    if prov is None:
        raise ValueError(f"Engine inventory entry {name!r} has no provider")
    with _LOCK:
        existing = _NAMED.get(name)
        if existing is not None and existing is not prov:
            raise ValueError(f"Duplicate engine inventory name {name!r}")
        _NAMED[name] = prov
    return prov


def register_engines(engines: Any) -> dict[str, Provider]:
    """Register a canonical AppSpec.engines inventory."""

    out: dict[str, Provider] = {}
    for engine in tuple(engines or ()):
        name = getattr(engine, "name", None)
        if not name:
            raise ValueError("engine inventory entries must declare name")
        out[str(name)] = register_engine(str(name), engine)
    return out


def set_default_engine_name(name: str | None) -> None:
    global _DEFAULT_NAME
    with _LOCK:
        if name is not None:
            _provider_by_name(name)
        _DEFAULT_NAME = name


def register_router(router: Any, ctx: EngineCfg | None) -> None:
    """
    Register an API-level Provider.
    """
    prov = _coerce(ctx)
    logger.debug("register_router: router=%r coerced provider=%r", router, prov)
    if prov is None:
        logger.debug("register_router: no provider; skipping registration")
        return
    with _LOCK:
        _ROUTER[id(router)] = prov
        logger.debug(
            "register_router: registered provider for router id %s", id(router)
        )


def register_router_engine_name(router: Any, name: str | None) -> None:
    if name is None:
        return
    with _LOCK:
        _provider_by_name(name)
        _ROUTER_NAME[id(router)] = name


def register_table(model: Any, ctx: EngineCfg | None) -> None:
    """
    Register a table/model-level Provider.
    """
    prov = _coerce(ctx)
    logger.debug("register_table: model=%r coerced provider=%r", model, prov)
    if prov is None:
        logger.debug("register_table: no provider; skipping registration")
        return
    with _LOCK:
        _TAB[model] = prov
        logger.debug("register_table: registered provider for model %r", model)


def register_table_engine_name(model: Any, name: str | None) -> None:
    if name is None:
        return
    with _LOCK:
        _provider_by_name(name)
        _TAB_NAME[model] = name


def register_op(model: Any, alias: str, ctx: EngineCfg | None) -> None:
    """
    Register an op-level Provider for (model, alias).
    """
    prov = _coerce(ctx)
    logger.debug(
        "register_op: model=%r alias=%r coerced provider=%r", model, alias, prov
    )
    if prov is None:
        logger.debug("register_op: no provider; skipping registration")
        return
    with _LOCK:
        _OP[(model, alias)] = prov
        logger.debug(
            "register_op: registered provider for model %r alias %s", model, alias
        )


def register_op_engine_name(model: Any, alias: str, name: str | None) -> None:
    if name is None:
        return
    with _LOCK:
        _provider_by_name(name)
        _OP_NAME[(model, alias)] = name


def require_schema_ready(provider: Provider) -> None:
    with _LOCK:
        _SCHEMA_REQUIRED.add(_provider_id(provider))


def mark_schema_ready(provider: Provider) -> None:
    with _LOCK:
        _SCHEMA_READY.add(_provider_id(provider))


def clear_schema_ready(provider: Provider) -> None:
    with _LOCK:
        _SCHEMA_READY.discard(_provider_id(provider))


# ---- resolution -------------------------------------------------------------


def resolve_provider(
    *,
    router: Any = None,
    model: Any = None,
    op_alias: str | None = None,
    engine_name: str | None = None,
) -> Optional[Provider]:
    """
    Resolve the effective Provider using precedence:
        op > model > router > app(default)
    """
    logger.debug(
        "resolve_provider called with router=%r model=%r op_alias=%r",
        router,
        model,
        op_alias,
    )
    with _LOCK:
        p = _resolve_named(engine_name)
        if p is not None:
            return p
        if model is not None and op_alias is not None:
            logger.debug("resolve_provider: checking op-level provider")
            for m in _with_class(model):
                p = _resolve_named(_OP_NAME.get((m, op_alias)))
                if p:
                    logger.debug("resolve_provider: found op-level named provider %r", p)
                    return p
                logger.debug(
                    "resolve_provider: looking for op provider for %r alias %s",
                    m,
                    op_alias,
                )
                p = _OP.get((m, op_alias))
                if p:
                    logger.debug("resolve_provider: found op-level provider %r", p)
                    return p
        if model is not None:
            logger.debug("resolve_provider: checking model-level provider")
            for m in _with_class(model):
                p = _resolve_named(_TAB_NAME.get(m))
                if p:
                    logger.debug("resolve_provider: found model-level named provider %r", p)
                    return p
                logger.debug("resolve_provider: looking for model provider %r", m)
                p = _TAB.get(m)
                if p:
                    logger.debug("resolve_provider: found model-level provider %r", p)
                    return p
        if router is not None:
            logger.debug("resolve_provider: checking router-level provider")
            for a in _with_class(router):
                p = _resolve_named(_ROUTER_NAME.get(id(a)))
                if p:
                    logger.debug("resolve_provider: found router-level named provider %r", p)
                    return p
                logger.debug("resolve_provider: looking for router provider %r", a)
                # APIs are keyed by ``id`` to avoid relying on ``__hash__``
                p = _ROUTER.get(id(a))
                if p:
                    logger.debug("resolve_provider: found router-level provider %r", p)
                    return p
        named_default = _resolve_named(_DEFAULT_NAME)
        if named_default is not None:
            logger.debug("resolve_provider: returning named default provider %r", named_default)
            return named_default
        logger.debug("resolve_provider: returning default provider %r", _DEFAULT)
        return _DEFAULT


SessionT = Session | AsyncSession


def acquire(
    *,
    router: Any = None,
    model: Any = None,
    op_alias: str | None = None,
    engine_name: str | None = None,
    require_ready: bool = False,
) -> tuple[SessionT, Callable[[], None]]:
    """
    Acquire a DB session from the resolved Provider.

    Returns:
        (session, release_fn)

    Raises:
        RuntimeError: if no Provider can be resolved and no default is set.
    """
    logger.debug(
        "acquire called with router=%r model=%r op_alias=%r", router, model, op_alias
    )
    p = resolve_provider(
        router=router,
        model=model,
        op_alias=op_alias,
        engine_name=engine_name,
    )
    if p is None and model is not None:
        get_db = getattr(model, "__tigrbl_get_db__", None)
        if callable(get_db):
            db = get_db()

            def _release() -> None:
                close = getattr(db, "close", None)
                if callable(close):
                    try:
                        rv = close()
                        if inspect.isawaitable(rv):
                            try:
                                loop = asyncio.get_running_loop()
                            except RuntimeError:
                                asyncio.run(rv)
                            else:
                                loop.create_task(rv)
                    except Exception:
                        pass

            return db, _release
    if p is None:
        logger.debug("acquire: no provider resolved; raising error")
        raise RuntimeError(
            f"No database provider configured for op={op_alias} "
            f"model={getattr(model, '__name__', model)} "
            f"router={type(router).__name__ if router else None} and no default"
        )
    if require_ready:
        _require_ready(p)
    db: SessionT = p.session()
    logger.debug("acquire: session %r acquired from provider %r", db, p)

    def _release() -> None:
        logger.debug("_release: attempting to release session %r", db)
        close = getattr(db, "close", None)
        if callable(close):
            try:
                rv = close()
                logger.debug("_release: close returned %r", rv)
                if inspect.isawaitable(rv):
                    logger.debug("_release: awaiting asynchronous close")
                    try:
                        loop = asyncio.get_running_loop()
                    except RuntimeError:
                        logger.debug("_release: no running loop; using asyncio.run")
                        asyncio.run(rv)
                    else:
                        logger.debug("_release: scheduling close on running loop")
                        loop.create_task(rv)
                # If close is sync, it has already executed
            except Exception:
                logger.debug("_release: error during close", exc_info=True)
                # best-effort close; swallow to avoid masking handler errors
                pass
        logger.debug("_release: release complete for session %r", db)

    return db, _release


def iter_providers() -> list[Provider]:
    with _LOCK:
        out: list[Provider] = []
        if _DEFAULT is not None:
            out.append(_DEFAULT)
        out.extend(_ROUTER.values())
        out.extend(_TAB.values())
        out.extend(_OP.values())
        out.extend(_NAMED.values())
    seen: set[int] = set()
    uniq: list[Provider] = []
    for provider in out:
        pid = id(provider)
        if pid not in seen:
            seen.add(pid)
            uniq.append(provider)
    return uniq


def warmup(*, ensure: bool = True) -> None:
    if not ensure:
        return
    for provider in iter_providers():
        provider.ensure()


def reset(*, dispose: bool = True) -> None:
    """Reset resolver state; optionally dispose any built engines."""
    global _DEFAULT, _DEFAULT_NAME
    with _LOCK:
        providers: list[Provider] = []
        if _DEFAULT is not None:
            providers.append(_DEFAULT)
        providers.extend(_ROUTER.values())
        providers.extend(_TAB.values())
        providers.extend(_OP.values())
        providers.extend(_PROV_BY_KEY.values())

        seen: set[int] = set()
        uniq: list[Provider] = []
        for provider in providers:
            pid = id(provider)
            if pid not in seen:
                seen.add(pid)
                uniq.append(provider)

        if dispose:
            for provider in uniq:
                try:
                    engine = getattr(provider, "_engine", None)
                    if engine is None:
                        continue
                    dispose_fn = getattr(engine, "dispose", None)
                    if dispose_fn is None:
                        continue
                    result = dispose_fn()
                    if inspect.isawaitable(result):
                        try:
                            loop = asyncio.get_running_loop()
                        except RuntimeError:
                            asyncio.run(result)
                        else:
                            loop.create_task(result)
                except Exception:
                    logger.debug("reset: error disposing engine", exc_info=True)

        _DEFAULT = None
        _DEFAULT_NAME = None
        _ROUTER.clear()
        _TAB.clear()
        _OP.clear()
        _PROV_BY_KEY.clear()
        _NAMED.clear()
        _ROUTER_NAME.clear()
        _TAB_NAME.clear()
        _OP_NAME.clear()
        _SCHEMA_REQUIRED.clear()
        _SCHEMA_READY.clear()
