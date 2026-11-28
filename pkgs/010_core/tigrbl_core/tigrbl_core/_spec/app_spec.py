# pkgs/standards/tigrbl_core/tigrbl/_spec/app_spec.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Sequence

from .._spec.engine_spec import EngineCfg, EngineSpec
from .._spec.monotone import as_tuple, merge_mro_sequence_attr
from .._spec.response_spec import ResponseSpec
from .._spec.well_known_spec import WellKnownResourceSpec
from .serde import SerdeMixin


def _seqify(value: Any) -> tuple[Any, ...]:
    """Normalize sequence-like inputs while treating scalars as a single item."""

    return as_tuple(value)


def merge_seq_attr(
    owner: type,
    attr: str,
    *,
    include_inherited: bool = False,
    reverse: bool = False,
    dedupe: bool = True,
) -> tuple[Any, ...]:
    """Merge sequence-like class attributes over the MRO."""

    return merge_mro_sequence_attr(
        owner,
        attr,
        include_inherited=include_inherited,
        reverse=reverse,
        dedupe=dedupe,
    )


def normalize_app_spec(spec: "AppSpec") -> "AppSpec":
    """Return a normalized app spec snapshot with stable sequence fields."""

    routers = _seqify(spec.routers)
    tables = _seqify(spec.tables)
    ops = _seqify(spec.ops)

    return AppSpec(
        title=str(spec.title or "Tigrbl"),
        description=spec.description,
        version=str(spec.version or "0.1.0"),
        execution_backend=normalize_execution_backend(
            getattr(spec, "execution_backend", None),
        ),
        engine=spec.engine,
        engine_name=spec.engine_name,
        engines=_seqify(spec.engines),
        routers=routers,
        ops=ops,
        well_known=_seqify(spec.well_known),
        tables=tables,
        schemas=_seqify(spec.schemas),
        hooks=_seqify(spec.hooks),
        security_deps=_seqify(spec.security_deps),
        deps=_seqify(spec.deps),
        middlewares=_seqify(spec.middlewares),
        response=spec.response,
        jsonrpc_prefix=str(spec.jsonrpc_prefix or "/rpc"),
        system_prefix=str(spec.system_prefix or "/system"),
        lifespan=spec.lifespan,
    )


def normalize_execution_backend(value: Any) -> str:
    lowered = str(value or "auto").strip().lower()
    if not lowered:
        return "auto"
    if lowered in {"auto", "python"}:
        return lowered
    raise ValueError(f"unsupported execution backend: {value!r}")


@dataclass(eq=False)
class AppSpec(SerdeMixin):
    """
    Used to *produce an App subclass* via App.from_spec().
    """

    title: str = "Tigrbl"
    description: str | None = None
    version: str = "0.1.0"
    execution_backend: str = "auto"
    engine: Optional[EngineCfg] = None
    engine_name: str | None = None
    engines: Sequence[EngineSpec] = field(default_factory=tuple)

    # NEW: multi-Router composition (store Router classes or instances)
    routers: Sequence[Any] = field(default_factory=tuple)

    # NEW: orchestration/topology knobs
    ops: Sequence[Any] = field(default_factory=tuple)  # op descriptors or specs
    well_known: Sequence[WellKnownResourceSpec] = field(default_factory=tuple)
    tables: Sequence[Any] = field(default_factory=tuple)  # table refs owned by app
    schemas: Sequence[Any] = field(default_factory=tuple)  # schema classes/defs
    hooks: Sequence[Callable[..., Any]] = field(default_factory=tuple)

    # security/dep stacks (ASGI dependencies or callables)
    security_deps: Sequence[Callable[..., Any]] = field(default_factory=tuple)
    deps: Sequence[Callable[..., Any]] = field(default_factory=tuple)

    # response defaults
    response: Optional[ResponseSpec] = None

    # system routing prefixes (REST/JSON-RPC namespaces)
    jsonrpc_prefix: str = "/rpc"
    system_prefix: str = "/system"

    # optional framework bits
    middlewares: Sequence[Any] = field(default_factory=tuple)
    lifespan: Optional[Callable[..., Any]] = None

    def __post_init__(self) -> None:
        self.execution_backend = normalize_execution_backend(self.execution_backend)
        self.engines = _seqify(self.engines)
        self.routers = _seqify(self.routers)
        self.ops = _seqify(self.ops)
        self.well_known = _seqify(self.well_known)
        self.tables = _seqify(self.tables)
        self.schemas = _seqify(self.schemas)
        self.hooks = _seqify(self.hooks)
        self.security_deps = _seqify(self.security_deps)
        self.deps = _seqify(self.deps)
        self.middlewares = _seqify(self.middlewares)

        for resource in self.well_known:
            if isinstance(resource, str):
                raise TypeError("AppSpec.well_known entries must be nested specs, not strings.")
            if not isinstance(resource, WellKnownResourceSpec):
                raise TypeError(
                    "AppSpec.well_known entries must be WellKnownResourceSpec; "
                    f"got {type(resource).__name__}."
                )
        validate_engine_inventory(self.engines)
        validate_engine_name_binding(
            self.engine_name,
            self.engines,
            scope="AppSpec.engine_name",
        )
        for router in tuple(self.routers or ()):
            validate_engine_name_binding(
                getattr(router, "engine_name", None),
                self.engines,
                scope="RouterSpec.engine_name",
            )
            for path in tuple(getattr(router, "paths", ()) or ()):
                for table in tuple(getattr(path, "tables", ()) or ()):
                    validate_engine_name_binding(
                        getattr(table, "engine_name", None),
                        self.engines,
                        scope="TableSpec.engine_name",
                    )
                    for op in tuple(getattr(table, "ops", ()) or ()):
                        validate_engine_name_binding(
                            getattr(op, "engine_name", None),
                            self.engines,
                            scope="OpSpec.engine_name",
                        )
                for op in tuple(getattr(path, "ops", ()) or ()):
                    validate_engine_name_binding(
                        getattr(op, "engine_name", None),
                        self.engines,
                        scope="OpSpec.engine_name",
                    )
            for table in tuple(getattr(router, "tables", ()) or ()):
                validate_engine_name_binding(
                    getattr(table, "engine_name", None),
                    self.engines,
                    scope="TableSpec.engine_name",
                )
            for op in tuple(getattr(router, "ops", ()) or ()):
                validate_engine_name_binding(
                    getattr(op, "engine_name", None),
                    self.engines,
                    scope="OpSpec.engine_name",
                )
            _validate_router_docs_tree(router)
        for table in tuple(self.tables or ()):
            validate_engine_name_binding(
                getattr(table, "engine_name", None),
                self.engines,
                scope="TableSpec.engine_name",
            )
        for op in tuple(self.ops or ()):
            validate_engine_name_binding(
                getattr(op, "engine_name", None),
                self.engines,
                scope="OpSpec.engine_name",
            )

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "AppSpec":
        if "routes" in payload:
            raise ValueError("AppSpec does not accept 'routes'; use path-owned specs.")
        return super().from_dict(payload)

    @classmethod
    def collect(cls, app: type) -> "AppSpec":
        sentinel = object()
        title: Any = sentinel
        version: Any = sentinel
        execution_backend: Any = sentinel
        engine: Any | None = sentinel  # type: ignore[assignment]
        engine_name: Any | None = sentinel
        engines: Any | None = sentinel
        response: Any = sentinel
        jsonrpc_prefix: Any = sentinel
        system_prefix: Any = sentinel
        lifespan: Any = sentinel

        for base in app.__mro__:
            if "TITLE" in base.__dict__ and title is sentinel:
                title = base.__dict__["TITLE"]
            if "VERSION" in base.__dict__ and version is sentinel:
                version = base.__dict__["VERSION"]
            if (
                "EXECUTION_BACKEND" in base.__dict__
                and execution_backend is sentinel
            ):
                execution_backend = base.__dict__["EXECUTION_BACKEND"]
            if "ENGINE" in base.__dict__ and engine is sentinel:
                engine = base.__dict__["ENGINE"]
            if "ENGINE_NAME" in base.__dict__ and engine_name is sentinel:
                engine_name = base.__dict__["ENGINE_NAME"]
            if "ENGINES" in base.__dict__ and engines is sentinel:
                engines = base.__dict__["ENGINES"]
            if "RESPONSE" in base.__dict__ and response is sentinel:
                response = base.__dict__["RESPONSE"]
            if "JSONRPC_PREFIX" in base.__dict__ and jsonrpc_prefix is sentinel:
                jsonrpc_prefix = base.__dict__["JSONRPC_PREFIX"]
            if "SYSTEM_PREFIX" in base.__dict__ and system_prefix is sentinel:
                system_prefix = base.__dict__["SYSTEM_PREFIX"]
            if "LIFESPAN" in base.__dict__ and lifespan is sentinel:
                lifespan = base.__dict__["LIFESPAN"]

        if title is sentinel:
            title = "Tigrbl"
        if version is sentinel:
            version = "0.1.0"
        if execution_backend is sentinel:
            execution_backend = "auto"
        if engine is sentinel:
            engine = None
        if engine_name is sentinel:
            engine_name = None
        if engines is sentinel:
            engines = ()
        if response is sentinel:
            response = None
        if jsonrpc_prefix is sentinel:
            jsonrpc_prefix = "/rpc"
        if system_prefix is sentinel:
            system_prefix = "/system"
        if lifespan is sentinel:
            lifespan = None

        description = getattr(app, "DESCRIPTION", None)
        include_inherited_routers = "ROUTERS" not in app.__dict__
        spec = cls(
            title=title,
            description=description,
            version=version,
            execution_backend=execution_backend,
            engine=engine,
            engine_name=engine_name,
            engines=tuple(engines or ()),
            routers=tuple(
                merge_seq_attr(
                    app,
                    "ROUTERS",
                    include_inherited=include_inherited_routers,
                    reverse=include_inherited_routers,
                    dedupe=False,
                )
                or ()
            ),
            ops=tuple(merge_seq_attr(app, "OPS") or ()),
            well_known=tuple(merge_seq_attr(app, "WELL_KNOWN") or ()),
            tables=tuple(merge_seq_attr(app, "TABLES") or ()),
            schemas=tuple(merge_seq_attr(app, "SCHEMAS") or ()),
            hooks=tuple(merge_seq_attr(app, "HOOKS") or ()),
            security_deps=tuple(merge_seq_attr(app, "SECURITY_DEPS") or ()),
            deps=tuple(merge_seq_attr(app, "DEPS") or ()),
            response=response,
            jsonrpc_prefix=(jsonrpc_prefix or "/rpc"),
            system_prefix=(system_prefix or "/system"),
            middlewares=tuple(merge_seq_attr(app, "MIDDLEWARES") or ()),
            lifespan=lifespan,
        )
        return normalize_app_spec(
            cls(
                title=spec.title,
                description=spec.description,
                version=spec.version,
                execution_backend=spec.execution_backend,
                engine=spec.engine,
                engine_name=spec.engine_name,
                engines=tuple(spec.engines or ()),
                routers=tuple(spec.routers or ()),
                ops=tuple(spec.ops or ()),
                well_known=tuple(spec.well_known or ()),
                tables=tuple(spec.tables or ()),
                schemas=tuple(spec.schemas or ()),
                hooks=tuple(spec.hooks or ()),
                security_deps=tuple(spec.security_deps or ()),
                deps=tuple(spec.deps or ()),
                response=spec.response,
                jsonrpc_prefix=(spec.jsonrpc_prefix or "/rpc"),
                system_prefix=(spec.system_prefix or "/system"),
                middlewares=tuple(spec.middlewares or ()),
                lifespan=spec.lifespan,
            )
        )


def validate_engine_inventory(engines: Sequence[EngineSpec]) -> None:
    names: set[str] = set()
    for engine in tuple(engines or ()):
        if not isinstance(engine, EngineSpec):
            raise TypeError(
                f"AppSpec.engines entries must be EngineSpec; got {type(engine).__name__}."
            )
        if not engine.name:
            raise ValueError("AppSpec.engines entries must declare EngineSpec.name.")
        if engine.name in names:
            raise ValueError(f"Duplicate EngineSpec.name in AppSpec.engines: {engine.name!r}.")
        names.add(engine.name)


def validate_engine_name_binding(
    engine_name: str | None,
    engines: Sequence[EngineSpec],
    *,
    scope: str,
) -> None:
    if engine_name is None:
        return
    names = {engine.name for engine in tuple(engines or ())}
    if engine_name not in names:
        raise ValueError(f"{scope} references unknown engine name {engine_name!r}.")


def resolve_engine_name(
    app: AppSpec,
    *,
    router: Any | None = None,
    table: Any | None = None,
    op: Any | None = None,
) -> str | None:
    for scope in (op, table, router, app):
        name = getattr(scope, "engine_name", None)
        if name:
            validate_engine_name_binding(
                name,
                app.engines,
                scope=f"{scope.__class__.__name__}.engine_name",
            )
            return str(name)
    return None


def _validate_router_docs_tree(router: Any) -> None:
    paths = tuple(getattr(router, "paths", ()) or ())
    if not paths:
        return
    from .docs_spec import validate_docs_tree

    validate_docs_tree(paths)
