from __future__ import annotations

from typing import Any

from tigrbl_concrete._concrete import engine_resolver as _resolver


def install_appspec_engine_inventory(app: Any, spec: Any) -> None:
    engines = tuple(getattr(spec, "engines", ()) or ())
    if engines:
        _resolver.register_engines(engines)
    engine_name = getattr(spec, "engine_name", None)
    if engine_name is not None:
        _resolver.set_default_engine_name(engine_name)
    if getattr(spec, "engine", None) is not None:
        _resolver.set_default(spec.engine)
    setattr(app, "_tigrbl_engine_inventory", engines)


def install_scope_engine_names(
    *,
    router: Any | None = None,
    model: Any | None = None,
    table_spec: Any | None = None,
    op_specs: tuple[Any, ...] = (),
) -> None:
    if router is not None:
        _resolver.register_router_engine_name(router, getattr(router, "engine_name", None))
    if model is not None and table_spec is not None:
        _resolver.register_table_engine_name(model, getattr(table_spec, "engine_name", None))
        for op_spec in tuple(op_specs or ()):
            alias = getattr(op_spec, "alias", None)
            if alias:
                _resolver.register_op_engine_name(
                    model,
                    str(alias),
                    getattr(op_spec, "engine_name", None),
                )
