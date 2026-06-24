from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Mapping, MutableMapping, Optional

from tigrbl_kernel import _default_kernel, build_phase_chains, get_cached_specs
from tigrbl_runtime.executors.phase_runner import _invoke


def resolve_phase_chains(model: type, alias: str) -> Mapping[str, list[Any]]:
    """Resolve executable phase chains for a concrete model operation."""
    return build_phase_chains(model, alias) or {}


async def invoke_op(
    *,
    request: Any = None,
    db: Any = None,
    model: type,
    alias: str,
    ctx: Optional[MutableMapping[str, Any]] = None,
) -> Any:
    """Resolve concrete operation metadata and execute its phase lifecycle."""
    seed_ctx: MutableMapping[str, Any] = dict(ctx or {})
    seed_ctx.setdefault("model", model)
    seed_ctx.setdefault("op", alias)
    seed_ctx.setdefault("method", alias)
    if request is not None:
        seed_ctx.setdefault("request", request)
    if db is not None:
        seed_ctx.setdefault("db", db)
    if seed_ctx.get("env") is None:
        seed_ctx["env"] = SimpleNamespace(method=alias)
    seed_ctx.setdefault("skip_egress", True)

    app_ref = (
        getattr(request, "app", None)
        or seed_ctx.get("app")
        or seed_ctx.get("router")
        or model
    )
    seed_ctx.setdefault("app", app_ref)
    seed_ctx.setdefault("router", seed_ctx.get("router") or app_ref)

    if seed_ctx.get("specs") is None:
        specs = get_cached_specs(model)
        if specs is not None:
            seed_ctx["specs"] = specs

    if seed_ctx.get("opview") is None:
        try:
            seed_ctx["opview"] = _default_kernel.get_opview(app_ref, model, alias)
        except Exception:
            # Some call paths rely only on specs/schemas and can proceed without
            # a compiled opview.
            pass

    return await _invoke(
        request=request,
        db=db,
        phases=resolve_phase_chains(model, alias),
        ctx=seed_ctx,
    )


__all__ = ["invoke_op", "resolve_phase_chains"]
