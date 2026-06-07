from __future__ import annotations

from dataclasses import replace
import re
from typing import Any

from tigrbl_core._spec.app_spec import AppSpec
from tigrbl_core._spec.engine_spec import EngineSpec

from tigrbl_concrete._concrete import engine_resolver as _resolver


_NAME_RE = re.compile(r"[^A-Za-z0-9_]+")


def lower_concrete_engine_inputs(spec: AppSpec) -> AppSpec:
    """Normalize concrete engine inputs into canonical named inventory.

    Concrete authoring may attach raw engine specs at app, router, table, and op
    scopes. Canonical runtime consumption must use AppSpec.engines plus
    scope-level engine_name bindings only.
    """

    builder = _EngineInventoryBuilder(tuple(getattr(spec, "engines", ()) or ()))
    app_engine_name = getattr(spec, "engine_name", None)
    app_engine = getattr(spec, "engine", None)
    if app_engine is not None:
        app_engine_name = builder.add(
            app_engine,
            requested_name=app_engine_name,
            fallback_name="app",
            scope="AppSpec.engine",
        )

    routers = tuple(
        _lower_router_spec(router, builder) for router in tuple(spec.routers or ())
    )
    tables = tuple(
        _lower_table_spec(table, builder, "app_table")
        for table in tuple(spec.tables or ())
    )
    ops = tuple(_lower_op_spec(op, builder, "app_op") for op in tuple(spec.ops or ()))

    lowered = replace(
        spec,
        engine=None,
        engine_name=app_engine_name,
        engines=builder.engines,
        routers=routers,
        tables=tables,
        ops=ops,
    )
    setattr(lowered, "_tigrbl_engines_lowered", True)
    return lowered


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
        _resolver.register_router_engine_name(
            router, getattr(router, "engine_name", None)
        )
    if model is not None and table_spec is not None:
        _resolver.register_table_engine_name(
            model, getattr(table_spec, "engine_name", None)
        )
        for op_spec in tuple(op_specs or ()):
            alias = getattr(op_spec, "alias", None)
            if alias:
                _resolver.register_op_engine_name(
                    model,
                    str(alias),
                    getattr(op_spec, "engine_name", None),
                )


class _EngineInventoryBuilder:
    def __init__(self, engines: tuple[EngineSpec, ...]) -> None:
        self._engines: list[EngineSpec] = []
        self._by_name: dict[str, EngineSpec] = {}
        for engine in engines:
            if not isinstance(engine, EngineSpec):
                raise TypeError(
                    f"AppSpec.engines entries must be EngineSpec; got {type(engine).__name__}."
                )
            if not engine.name:
                raise ValueError(
                    "AppSpec.engines entries must declare EngineSpec.name."
                )
            self._insert(engine.name, engine, scope="AppSpec.engines")

    @property
    def engines(self) -> tuple[EngineSpec, ...]:
        return tuple(self._engines)

    def add(
        self,
        raw: Any,
        *,
        requested_name: str | None,
        fallback_name: str,
        scope: str,
    ) -> str:
        spec = EngineSpec.from_any(raw)
        if spec is None:
            raise ValueError(f"{scope} did not resolve to an engine spec.")

        name = (
            _clean_name(requested_name)
            or _raw_engine_name(raw)
            or _clean_name(getattr(spec, "name", None))
            or _clean_name(fallback_name)
        )
        if name is None:
            raise ValueError(f"{scope} requires a non-empty engine inventory name.")
        if spec.name != name:
            spec = replace(spec, name=name)
        self._insert(name, spec, scope=scope)
        return name

    def _insert(self, name: str, spec: EngineSpec, *, scope: str) -> None:
        existing = self._by_name.get(name)
        if existing is not None:
            if existing != spec:
                raise ValueError(
                    f"{scope} conflicts with existing engine name {name!r}."
                )
            return
        self._by_name[name] = spec
        self._engines.append(spec)


def _lower_router_spec(router: Any, builder: _EngineInventoryBuilder) -> Any:
    router_name = _scope_token(getattr(router, "name", None), "router")
    engine_name = getattr(router, "engine_name", None)
    engine = getattr(router, "engine", None)
    if engine is not None:
        engine_name = builder.add(
            engine,
            requested_name=engine_name,
            fallback_name=f"router_{router_name}",
            scope="RouterSpec.engine",
        )

    paths = tuple(
        replace(
            path,
            tables=tuple(
                _lower_table_spec(table, builder, f"{router_name}_table")
                for table in tuple(getattr(path, "tables", ()) or ())
            ),
            ops=tuple(
                _lower_op_spec(op, builder, f"{router_name}_path_op")
                for op in tuple(getattr(path, "ops", ()) or ())
            ),
        )
        for path in tuple(getattr(router, "paths", ()) or ())
    )
    tables = tuple(
        _lower_table_spec(table, builder, f"{router_name}_table")
        for table in tuple(getattr(router, "tables", ()) or ())
    )
    ops = tuple(
        _lower_op_spec(op, builder, f"{router_name}_op")
        for op in tuple(getattr(router, "ops", ()) or ())
    )
    return replace(
        router,
        engine=None,
        engine_name=engine_name,
        paths=paths,
        tables=tables,
        ops=ops,
    )


def _lower_table_spec(table: Any, builder: _EngineInventoryBuilder, prefix: str) -> Any:
    table_name = _table_token(table, prefix)
    engine_name = getattr(table, "engine_name", None)
    engine = getattr(table, "engine", None)
    if engine is not None:
        engine_name = builder.add(
            engine,
            requested_name=engine_name,
            fallback_name=f"{prefix}_{table_name}",
            scope="TableSpec.engine",
        )

    ops = tuple(
        _lower_op_spec(op, builder, f"{prefix}_{table_name}")
        for op in tuple(getattr(table, "ops", ()) or ())
    )
    return replace(table, engine=None, engine_name=engine_name, ops=ops)


def _lower_op_spec(op: Any, builder: _EngineInventoryBuilder, prefix: str) -> Any:
    alias = _scope_token(getattr(op, "alias", None), "op")
    engine_name = getattr(op, "engine_name", None)
    engine = getattr(op, "engine", None)
    if engine is not None:
        engine_name = builder.add(
            engine,
            requested_name=engine_name,
            fallback_name=f"{prefix}_{alias}",
            scope="OpSpec.engine",
        )
    return replace(op, engine=None, engine_name=engine_name)


def _raw_engine_name(raw: Any) -> str | None:
    if isinstance(raw, dict):
        return _clean_name(raw.get("engine_name") or raw.get("name"))
    return _clean_name(getattr(raw, "engine_name", None))


def _table_token(table: Any, fallback: str) -> str:
    for value in (
        getattr(table, "name", None),
        getattr(table, "resource", None),
        getattr(table, "model_ref", None),
        getattr(getattr(table, "model", None), "__name__", None),
    ):
        token = _scope_token(value, "")
        if token:
            return token
    return _scope_token(fallback, "table")


def _scope_token(value: Any, fallback: str) -> str:
    return _clean_name(value) or fallback


def _clean_name(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    text = _NAME_RE.sub("_", text).strip("_").lower()
    return text or None
