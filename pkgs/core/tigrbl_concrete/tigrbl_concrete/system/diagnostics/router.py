from __future__ import annotations

from typing import Any, Callable, Optional

from tigrbl_concrete._concrete._router import Router
from tigrbl_concrete.http_routes import register_http_route
from .healthz import build_healthz_endpoint
from .hookz import build_hookz_endpoint
from .kernelz import build_kernelz_endpoint
from .methodz import build_methodz_endpoint
from .utils import maybe_execute, opspecs, table_iter


def _register_diagnostics_route(
    router: Any,
    *,
    path: str,
    alias: str,
    endpoint_factory: Callable[[Any], Any],
) -> None:
    """Expose diagnostics endpoints through the canonical concrete route helper."""

    async def _diagnostics_step(ctx: Any) -> None:
        payload = await endpoint_factory(ctx)
        setattr(ctx, "result", payload)
        if isinstance(getattr(ctx, "temp", None), dict):
            ctx.temp.setdefault("egress", {})["result"] = payload

    register_http_route(router, path=path, methods=("GET",), alias=alias, endpoint=_diagnostics_step)


def _register_diagnostics_paths(
    router: Any, *, path: str, alias: str, endpoint_factory: Callable[[Any], Any]
) -> None:
    _register_diagnostics_route(
        router,
        path=path,
        alias=alias,
        endpoint_factory=endpoint_factory,
    )
    system_prefix = str(getattr(router, "system_prefix", "/system") or "/system")
    if system_prefix and system_prefix != "/":
        prefixed = f"{system_prefix.rstrip('/')}{path}"
        _register_diagnostics_route(
            router,
            path=prefixed,
            alias=alias,
            endpoint_factory=endpoint_factory,
        )


def mount_diagnostics(
    router: Any,
    *,
    get_db: Optional[Callable[..., Any]] = None,
) -> Router:
    """
    Create & return a Router that exposes:
      GET /healthz
      GET /methodz
      GET /hookz
      GET /kernelz
    """
    source_router = router
    router = Router()

    dep = get_db

    healthz_endpoint = build_healthz_endpoint(dep)

    async def _runtime_healthz(ctx: Any) -> Any:
        db = getattr(ctx, "db", None)
        if db is None:
            db = getattr(ctx, "_raw_db", None)
        if db is None:
            req = getattr(ctx, "request", None)
            state = getattr(req, "state", None)
            db = getattr(state, "db", None)
        if db is None:
            return {"ok": True}
        await maybe_execute(db, "SELECT 1")
        return {"ok": True}

    _register_diagnostics_paths(
        source_router,
        path="/healthz",
        alias="healthz",
        endpoint_factory=_runtime_healthz,
    )
    router.add_route(
        "/healthz",
        healthz_endpoint,
        methods=["GET"],
        name="healthz",
        tags=["system"],
        summary="Health",
        description="Database connectivity check.",
    )

    methodz_endpoint = build_methodz_endpoint(source_router)
    _register_diagnostics_paths(
        source_router,
        path="/methodz",
        alias="methodz",
        endpoint_factory=lambda _ctx: methodz_endpoint(),
    )
    router.add_route(
        "/methodz",
        methodz_endpoint,
        methods=["GET"],
        name="methodz",
        tags=["system"],
        summary="Methods",
        description="Ordered, canonical operation list.",
    )

    hookz_endpoint = build_hookz_endpoint(source_router)
    _register_diagnostics_paths(
        source_router,
        path="/hookz",
        alias="hookz",
        endpoint_factory=lambda _ctx: hookz_endpoint(),
    )
    router.add_route(
        "/hookz",
        hookz_endpoint,
        methods=["GET"],
        name="hookz",
        tags=["system"],
        summary="Hooks",
        description=(
            "Expose hook execution order for each method.\n\n"
            "Phases appear in runner order; error phases trail.\n"
            "Within each phase, hooks are listed in execution order: "
            "global (None) hooks, then method-specific hooks."
        ),
    )

    kernelz_endpoint = build_kernelz_endpoint(source_router)

    async def _runtime_kernelz(_ctx: Any) -> Any:
        from tigrbl_runtime.runtime.kernel import _default_kernel as K

        K.ensure_primed(source_router)
        payload: dict[str, dict[str, list[str]]] = {}
        for model in table_iter(source_router):
            model_name = getattr(model, "__name__", str(model))
            payload[model_name] = {}
            for sp in opspecs(model):
                payload[model_name][sp.alias] = K.plan_labels(model, sp.alias)
        return payload

    _register_diagnostics_paths(
        source_router,
        path="/kernelz",
        alias="kernelz",
        endpoint_factory=_runtime_kernelz,
    )
    router.add_route(
        "/kernelz",
        kernelz_endpoint,
        methods=["GET"],
        name="kernelz",
        tags=["system"],
        summary="Kernel Plan",
        description="Phase-chain plan as built by the kernel per operation.",
    )

    return router


__all__ = ["mount_diagnostics"]
