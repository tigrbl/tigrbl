# tigrbl/v3/transport/rest/aggregator.py
"""
Aggregates per-model REST routers into a single Router.

This does not build endpoints by itself; it simply collects the routers that
the concrete model binder attached to each model at `model.rest.router`.

Recommended workflow:
  1) Include models with `mount_router=False` so you don't double-mount:
        router.include_table(User, mount_router=False)
        router.include_table(Team, mount_router=False)
        # or:
        router.include_tables([User, Team], mount_router=False)
  2) Aggregate and mount once:
        app.include_router(build_rest_router(router, base_prefix="/router"))
     or:
        mount_rest(router, app, base_prefix="/router")

Notes:
  - Router paths already include `/{resource}`; we only add `base_prefix`.
  - Model-level auth/db deps and extra REST deps are already attached to each
    model router by the concrete binder; this wrapper can add additional top-level
    dependencies if you pass them in.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence

from tigrbl_concrete._concrete._router import Router
from tigrbl_concrete._concrete.dependencies import Depends


def _norm_prefix(p: Optional[str]) -> str:
    if not p:
        return ""
    if not p.startswith("/"):
        p = "/" + p
    return p.rstrip("/")


def _normalize_deps(deps: Optional[Sequence[Any]]) -> list:
    """Accept either Depends(...) objects or plain callables."""
    out = []
    for dep in deps or ():
        try:
            is_dep_obj = hasattr(dep, "dependency")
        except Exception:
            is_dep_obj = False
        out.append(dep if is_dep_obj else Depends(dep))
    return out


def _iter_tables(router: Any, only: Optional[Sequence[type]] = None) -> Sequence[type]:
    if only:
        return list(only)
    tables: Mapping[str, type] = getattr(router, "tables", None) or {}
    return [tables[key] for key in sorted(tables.keys())]


def build_rest_router(
    router: Any,
    *,
    models: Optional[Sequence[type]] = None,
    base_prefix: str = "",
    dependencies: Optional[Sequence[Any]] = None,
) -> Router:
    """
    Build a top-level Router that includes each model's router under `base_prefix`.

    Args:
        router: your Tigrbl facade (or any object with `.tables` mapping).
        models: optional subset of models to include; defaults to all bound models.
        base_prefix: prefix applied once for all included routers (e.g., "/router").
        dependencies: additional router-level dependencies (Depends(...) or callables).

    Returns:
        Router ready to be mounted on your ASGI app.
    """
    root = Router(dependencies=_normalize_deps(dependencies))
    prefix = _norm_prefix(base_prefix)

    for model in _iter_tables(router, models):
        rest_ns = getattr(model, "rest", None)
        child_router = getattr(rest_ns, "router", None) if rest_ns is not None else None
        if child_router is None:
            continue
        root.include_router(child_router, prefix=prefix or "")
    return root


def mount_rest(
    router: Any,
    app: Any,
    *,
    models: Optional[Sequence[type]] = None,
    base_prefix: str = "",
    dependencies: Optional[Sequence[Any]] = None,
) -> Router:
    """
    Convenience helper: build the aggregated router and include it on `app`.

    Returns the created router so you can keep a reference if desired.
    """
    rest_router = build_rest_router(
        router, models=models, base_prefix=base_prefix, dependencies=dependencies
    )
    include = getattr(app, "include_router", None)
    if callable(include):
        include(rest_router)
    return rest_router


__all__ = ["build_rest_router", "mount_rest"]
