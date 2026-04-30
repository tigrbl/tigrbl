from __future__ import annotations

from typing import Any, Callable, Optional

from tigrbl_concrete._concrete._router import Router
from .healthz import build_healthz_endpoint
from .hookz import build_hookz_endpoint
from .kernelz import build_kernelz_endpoint
from .methodz import build_methodz_endpoint
from .utils import maybe_execute, opspecs, table_iter


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

    healthz_endpoint = build_healthz_endpoint(dep, router=source_router)

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

    router.add_route(
        "/healthz",
        healthz_endpoint,
        methods=["GET"],
        name="healthz",
        tags=["system"],
        summary="Health",
        description="Database connectivity check.",
        inherit_owner_dependencies=False,
    )

    methodz_endpoint = build_methodz_endpoint(source_router)
    router.add_route(
        "/methodz",
        methodz_endpoint,
        methods=["GET"],
        name="methodz",
        tags=["system"],
        summary="Methods",
        description="Ordered, canonical operation list.",
        inherit_owner_dependencies=False,
    )

    hookz_endpoint = build_hookz_endpoint(source_router)
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
        inherit_owner_dependencies=False,
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

    router.add_route(
        "/kernelz",
        kernelz_endpoint,
        methods=["GET"],
        name="kernelz",
        tags=["system"],
        summary="Kernel Plan",
        description="Phase-chain plan as built by the kernel per operation.",
        inherit_owner_dependencies=False,
    )

    return router


__all__ = ["mount_diagnostics"]
