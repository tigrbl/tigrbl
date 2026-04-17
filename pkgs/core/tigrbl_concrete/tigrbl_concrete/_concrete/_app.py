from __future__ import annotations

import inspect
from dataclasses import replace
from typing import Any

from ._table_registry import TableRegistry
from ._websocket import WebSocket
from ._request import Request
from ._response import Response
from tigrbl_base._base import AppBase
from tigrbl_concrete.ddl import initialize as _ddl_initialize
from ._engine import Engine
from tigrbl_concrete._concrete import engine_resolver as _resolver
from tigrbl_core._spec.app_spec import AppSpec
from tigrbl_core._spec.engine_spec import EngineCfg
from ._route import (
    ROUTE_OPS_MODEL_NAME,
    add_route as _add_route_impl,
    include_router_routes as _include_router_impl,
    merge_tags as _merge_tags_impl,
    normalize_prefix as _normalize_prefix_impl,
    prefix_model_bindings as _prefix_model_bindings,
    route as _route_impl,
    upsert_route_opspec,
)
from tigrbl_concrete.system.static import _serve_static
from tigrbl_typing.gw.raw import GwRawEnvelope


class App(AppBase):
    @classmethod
    def collect(cls) -> AppSpec:
        """Collect and normalize AppSpec configuration for this App class."""
        return AppSpec.collect(cls)

    @classmethod
    def _collect_mro_spec(cls) -> AppSpec:
        return cls.collect()

    TITLE = "Tigrbl"
    VERSION = "0.1.0"
    LIFESPAN = None
    ROUTERS = ()
    OPS = ()
    TABLES = ()
    SCHEMAS = ()
    HOOKS = ()
    DESCRIPTION = None
    OPENAPI_URL = "/openapi.json"
    DOCS_URL = "/docs"
    DEBUG = False
    SWAGGER_UI_VERSION = "5.31.0"
    SECURITY_DEPS = ()
    DEPS = ()
    RESPONSE = None
    JSONRPC_PREFIX = "/rpc"
    SYSTEM_PREFIX = "/system"

    def __init__(self, *, engine: EngineCfg | None = None, **asgi_kwargs: Any) -> None:
        collected_spec = self.__class__._collect_mro_spec()
        collected_spec = self.__class__.bind_spec(collected_spec, parent=self)

        title = asgi_kwargs.pop("title", None)
        if title is not None:
            self.TITLE = title
        else:
            title = collected_spec.title
        version = asgi_kwargs.pop("version", None)
        if version is not None:
            self.VERSION = version
        else:
            version = collected_spec.version
        lifespan = asgi_kwargs.pop("lifespan", None)
        if lifespan is not None:
            self.LIFESPAN = lifespan
        else:
            lifespan = collected_spec.lifespan
        get_db = asgi_kwargs.pop("get_db", None)
        if get_db is not None:
            self.get_db = get_db
        description = asgi_kwargs.pop("description", None)
        if description is None:
            description = getattr(self, "DESCRIPTION", None)
        openapi_url = asgi_kwargs.pop("openapi_url", None)
        if openapi_url is None:
            openapi_url = getattr(self, "OPENAPI_URL", "/openapi.json")
        docs_url = asgi_kwargs.pop("docs_url", None)
        if docs_url is None:
            docs_url = getattr(self, "DOCS_URL", "/docs")
        debug = asgi_kwargs.pop("debug", None)
        if debug is None:
            debug = bool(getattr(self, "DEBUG", False))
        swagger_ui_version = asgi_kwargs.pop("swagger_ui_version", None)
        if swagger_ui_version is None:
            swagger_ui_version = getattr(self, "SWAGGER_UI_VERSION", "5.31.0")
        include_docs = asgi_kwargs.pop("include_docs", None)
        if include_docs is None:
            include_docs = bool(getattr(self, "INCLUDE_DOCS", False))
        self.title = title
        self.version = version
        self.description = description
        self.openapi_url = openapi_url
        self.docs_url = docs_url
        self.debug = debug
        self.swagger_ui_version = swagger_ui_version
        self.engine = engine if engine is not None else collected_spec.engine
        self.routers = tuple(collected_spec.routers)
        self.ops = tuple(collected_spec.ops)
        self.tables = TableRegistry(tables=collected_spec.tables)
        self.schemas = tuple(collected_spec.schemas)
        self.hooks = tuple(collected_spec.hooks)
        self.security_deps = tuple(collected_spec.security_deps)
        self.deps = tuple(collected_spec.deps)
        self.response = collected_spec.response
        self.jsonrpc_prefix = collected_spec.jsonrpc_prefix
        self.system_prefix = collected_spec.system_prefix
        self.lifespan = lifespan

        from ._router import Router

        Router.__init__(
            self,
            engine=self.engine,
            title=self.title,
            version=self.version,
            description=self.description,
            openapi_url=self.openapi_url,
            docs_url=self.docs_url,
            debug=self.debug,
            swagger_ui_version=self.swagger_ui_version,
            include_docs=include_docs,
            **asgi_kwargs,
        )
        # Router.__init__ seeds several attributes from class-level defaults.
        # Re-apply merged AppSpec values so MRO-collected app configuration
        # remains the source of truth for the app instance.
        self.routers = tuple(collected_spec.routers)
        self.ops = tuple(collected_spec.ops)
        self.tables = TableRegistry(tables=collected_spec.tables)
        self.schemas = tuple(collected_spec.schemas)
        self.hooks = tuple(collected_spec.hooks)
        self.security_deps = tuple(collected_spec.security_deps)
        self.deps = tuple(collected_spec.deps)
        self.response = collected_spec.response
        self.jsonrpc_prefix = collected_spec.jsonrpc_prefix
        self.system_prefix = collected_spec.system_prefix

        _engine_ctx = self.engine
        if _engine_ctx is not None:
            _resolver.set_default(_engine_ctx)
            _resolver.resolve_provider()

        self._runtime_default_executor = getattr(self, "DEFAULT_EXECUTOR", "packed")
        self._runtime_instance = None
        self._tigrbl_runtime_resolve_provider = _resolver.resolve_provider
        self._tigrbl_runtime_acquire_db = _resolver.acquire

    @property
    def router(self) -> "App":
        return self

    def add_route(self, path: str, endpoint: Any, *, methods: list[str] | tuple[str, ...], **kwargs: Any) -> None:
        _add_route_impl(self, path, endpoint, methods=methods, **kwargs)

    def route(self, path: str, *, methods: Any, **kwargs: Any):
        return _route_impl(self, path, methods=methods, **kwargs)

    def get(self, path: str, **kwargs: Any):
        return self.route(path, methods=["GET"], **kwargs)

    def post(self, path: str, **kwargs: Any):
        return self.route(path, methods=["POST"], **kwargs)

    def put(self, path: str, **kwargs: Any):
        return self.route(path, methods=["PUT"], **kwargs)

    def patch(self, path: str, **kwargs: Any):
        return self.route(path, methods=["PATCH"], **kwargs)

    def delete(self, path: str, **kwargs: Any):
        return self.route(path, methods=["DELETE"], **kwargs)

    def mount_openapi(self, *, path: str = "/openapi.json", name: str = "__openapi__") -> Any:
        from tigrbl_concrete.system.docs.openapi.mount import mount_openapi as _mount_openapi
        return _mount_openapi(self, path=path, name=name)

    def mount_swagger(self, *, path: str = "/docs", openapi_url: str | None = None, title: str | None = None) -> Any:
        from tigrbl_concrete.system.docs.swagger import mount_swagger as _mount_swagger
        return _mount_swagger(self, path=path, openapi_url=openapi_url, title=title)

    def mount_openrpc(self, *, path: str = "/openrpc.json", name: str = "openrpc_json") -> Any:
        from tigrbl_concrete.system.docs.openrpc import mount_openrpc as _mount_openrpc
        return _mount_openrpc(self, path=path, name=name)

    def mount_lens(self, *, path: str = "/lens", openrpc_url: str | None = None, title: str | None = None) -> Any:
        from tigrbl_concrete.system.docs.lens import mount_lens as _mount_lens
        return _mount_lens(self, path=path, openrpc_url=openrpc_url, title=title)

    def mount_json_schema(self, *, path: str = "/schemas.json") -> Any:
        from tigrbl_concrete.system.docs.json_schema import _mount_json_schema
        return _mount_json_schema(self, path=path)

    def mount_asyncapi(self, *, path: str = "/asyncapi.json") -> Any:
        from tigrbl_concrete.system.docs.asyncapi import _mount_asyncapi
        return _mount_asyncapi(self, path=path)

    def mount_static(self, *, directory: str | Path, path: str = "/static") -> Any:
        from tigrbl_concrete.system.static import _mount_static
        return _mount_static(self, directory=directory, path=path)

    def websocket(self, path: str, **kwargs: Any):
        def _decorator(handler: Any) -> Any:
            from ._route import compile_path
            from ._websocket import WebSocketRoute
            from tigrbl_concrete.system.docs.runtime_ops import (
                register_runtime_websocket_route,
            )

            full_path = path if path.startswith("/") else f"/{path}"
            normalized_path = full_path.rstrip("/") or "/"
            pattern, param_names = compile_path(normalized_path)
            route_name = kwargs.get("name", getattr(handler, "__name__", "websocket"))
            self.websocket_routes.append(
                WebSocketRoute(
                    path_template=normalized_path,
                    pattern=pattern,
                    param_names=param_names,
                    handler=handler,
                    name=route_name,
                    protocol=str(kwargs.get("protocol", kwargs.get("proto", "ws"))),
                    exchange=str(
                        kwargs.get("exchange", "bidirectional_stream")
                    ),
                    framing=str(kwargs.get("framing", "text")),
                    summary=kwargs.get("summary"),
                    description=kwargs.get("description"),
                    tags=kwargs.get("tags"),
                )
            )
            register_runtime_websocket_route(
                self,
                path=normalized_path,
                alias=route_name,
                endpoint=handler,
                protocol=str(kwargs.get("protocol", kwargs.get("proto", "ws"))),
                exchange=str(kwargs.get("exchange", "bidirectional_stream")),
                framing=str(kwargs.get("framing", "text")),
            )
            bump = getattr(self, "_bump_runtime_plan_revision", None)
            if callable(bump):
                bump()
            return handler
        return _decorator

    @property
    def runtime(self):
        runtime = getattr(self, "_runtime_instance", None)
        if runtime is None:
            from tigrbl_runtime.runtime import Runtime
            runtime = Runtime(default_executor=self._runtime_default_executor)
            self._runtime_instance = runtime
        return runtime

    async def _read_http_body(self, receive: Any) -> bytes:
        chunks: list[bytes] = []
        while True:
            message = await receive()
            if message.get("type") != "http.request":
                break
            chunks.append(message.get("body", b"") or b"")
            if not message.get("more_body"):
                break
        return b"".join(chunks)

    async def _dispatch_http_route(self, scope: dict[str, Any], receive: Any, send: Any) -> bool:
        method = str(scope.get("method") or "GET").upper()
        path = str(scope.get("path") or "/")
        body = await self._read_http_body(receive)
        request = Request.from_scope(scope, app=self)
        request.body = body
        for route in list(getattr(self, "routes", ()) or []):
            if method not in getattr(route, "methods", ()):
                continue
            matched = route.pattern.match(path)
            if matched is None:
                continue
            path_params = matched.groupdict()
            scope["path_params"] = path_params
            try:
                for dep in list(getattr(route, "security_dependencies", ()) or []):
                    dep(request)
                kwargs: dict[str, Any] = {}
                signature = inspect.signature(route.handler)
                params = list(signature.parameters.items())
                for idx, (name, param) in enumerate(params):
                    if name in path_params:
                        kwargs[name] = path_params[name]
                        continue
                    annotation = param.annotation
                    if annotation is Request or name in {"request", "_request"} or (len(params) == 1 and not path_params):
                        kwargs[name] = request
                result = route.handler(**kwargs)
                if inspect.isawaitable(result):
                    result = await result
            except Exception as exc:  # pragma: no cover - exercised by operator tests
                from tigrbl_runtime.runtime.status.exceptions import HTTPException
                if isinstance(exc, HTTPException):
                    response = Response.json(
                        {"detail": exc.detail},
                        status=int(exc.status_code),
                        headers=getattr(exc, "headers", None),
                    )
                    await response(scope, receive, send)
                    return True
                raise
            if isinstance(result, Response):
                response = result
            elif result is None:
                response = Response(status_code=204)
            elif isinstance(result, (dict, list)):
                response = Response.json(result)
            elif isinstance(result, (bytes, bytearray, memoryview)):
                response = Response.bytes(bytes(result))
            else:
                response = Response.text(str(result))
            await response(scope, receive, send)
            return True
        return False

    def install_engines(
        self, *, router: Any = None, tables: tuple[Any, ...] | None = None
    ) -> None:
        routers = (router,) if router is not None else self.ROUTERS
        tables = tables if tables is not None else self.TABLES
        install_app = self if (routers or tuple(tables)) else None
        if routers:
            for a in routers:
                Engine.install_from_objects(
                    app=install_app, router=a, tables=tuple(tables)
                )
        else:
            Engine.install_from_objects(
                app=install_app, router=None, tables=tuple(tables)
            )

    async def invoke(self, env: GwRawEnvelope) -> None:
        plan, packed_plan = self.runtime.compile(self)
        ctx: dict[str, Any] = {
            "app": self,
            "router": self,
            "raw": env,
            "env": env,
            "kernel_plan": plan,
            "plan": plan,
            "packed_plan": packed_plan,
            "temp": {},
        }
        await self.runtime.invoke(
            env=env,
            ctx=ctx,
            plan=plan,
            packed_plan=packed_plan,
        )

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        scope_type = scope.get("type")
        if scope_type == "lifespan":
            await self._handle_lifespan(scope, receive, send)
            return
        if scope_type == "websocket":
            if not scope.get("scheme"):
                scope = dict(scope)
                scope["scheme"] = "ws"
            env = GwRawEnvelope(kind="asgi3", scope=scope, receive=receive, send=send)
            await self.invoke(env)
            return
        path = scope.get("path")
        if isinstance(path, str):
            seen_paths = getattr(self, "_seen_paths", None)
            if not isinstance(seen_paths, set):
                seen_paths = set()
                setattr(self, "_seen_paths", seen_paths)
            seen_paths.add(path)
            static_response = _serve_static(self, Request.from_scope(scope, app=self))
            if static_response is not None:
                await static_response(scope, receive, send)
                return
        if await self._dispatch_http_route(scope, receive, send):
            return
        env = GwRawEnvelope(kind="asgi3", scope=scope, receive=receive, send=send)
        await self.invoke(env)

    async def _handle_websocket(
        self, scope: dict[str, Any], receive: Any, send: Any
    ) -> None:
        env = GwRawEnvelope(kind="asgi3", scope=scope, receive=receive, send=send)
        await self.invoke(env)

    async def _handle_lifespan(
        self, _scope: dict[str, Any], receive: Any, send: Any
    ) -> None:
        """Handle the ASGI lifespan protocol (startup/shutdown handshake).

        Honours a caller-supplied ``lifespan`` context manager (set via
        ``TigrblApp(..., lifespan=...)``) **and** the event-handler registry
        (``@app.on_event("startup")`` / ``"shutdown"``).  The lifespan CM
        wraps the entire up/down cycle so that shared resources it opens
        remain available until shutdown completes.
        """
        message = await receive()
        if message.get("type") != "lifespan.startup":
            return

        lifespan_cm = getattr(self, "lifespan", None) or getattr(
            self, "lifespan_context", None
        )

        try:
            # Enter the lifespan context manager (if provided) so that any
            # resources it creates stay alive until shutdown.
            if lifespan_cm is not None:
                ctx_manager = lifespan_cm(self)
                await ctx_manager.__aenter__()
            else:
                ctx_manager = None

            run_handlers = getattr(self, "run_event_handlers", None)
            if callable(run_handlers):
                await run_handlers("startup")

            await send({"type": "lifespan.startup.complete"})
        except Exception as exc:
            if ctx_manager is not None:
                try:
                    await ctx_manager.__aexit__(type(exc), exc, exc.__traceback__)
                except Exception:
                    pass
            await send({"type": "lifespan.startup.failed", "message": str(exc)})
            return

        # Wait for shutdown
        message = await receive()
        if message.get("type") == "lifespan.shutdown":
            try:
                if callable(run_handlers):
                    await run_handlers("shutdown")
            except Exception:
                pass
            finally:
                if ctx_manager is not None:
                    try:
                        await ctx_manager.__aexit__(None, None, None)
                    except Exception:
                        pass
                await send({"type": "lifespan.shutdown.complete"})

    def _normalize_prefix(self, prefix: str) -> str:
        return _normalize_prefix_impl(prefix)

    def _merge_tags(self, tags: list[str] | None) -> list[str] | None:
        return _merge_tags_impl(getattr(self, "tags", None), tags)

    def include_router(self, router: Any, *, prefix: str | None = None) -> Any:
        from ._route import compile_path

        routed = getattr(router, "router", router)
        route_prefix = prefix or ""
        _include_router_impl(self, routed, prefix=route_prefix)
        normalized_prefix = _normalize_prefix_impl(route_prefix)
        for name, model in dict(getattr(routed, "tables", {}) or {}).items():
            _prefix_model_bindings(model, normalized_prefix)
            if name == ROUTE_OPS_MODEL_NAME and name in self.tables:
                hooks = getattr(model, "hooks", None)
                for spec in tuple(getattr(getattr(model, "ops", None), "all", ()) or ()):
                    handler_step = None
                    alias_hooks = getattr(hooks, str(getattr(spec, "alias", "")), None)
                    if alias_hooks is not None:
                        handlers = list(getattr(alias_hooks, "HANDLER", ()) or ())
                        if handlers:
                            handler_step = handlers[0]
                    upsert_route_opspec(self, spec, handler_step=handler_step)
                continue
            self.tables.setdefault(name, model)
        for ws_route in list(getattr(routed, "websocket_routes", ()) or []):
            path_template = ws_route.path_template
            if normalized_prefix:
                path_template = f"{normalized_prefix}{path_template}" if path_template != "/" else normalized_prefix
            pattern, param_names = compile_path(path_template)
            self.websocket_routes.append(
                replace(ws_route, path_template=path_template, pattern=pattern, param_names=param_names)
            )
        for mount in list(getattr(routed, "_static_mounts", ()) or []):
            static_path = mount.get("path", "/static")
            if normalized_prefix:
                static_path = f"{normalized_prefix}{static_path}" if static_path != "/" else normalized_prefix
            self._static_mounts.append({"path": static_path, "directory": mount["directory"]})
        bump = getattr(self, "_bump_runtime_plan_revision", None)
        if callable(bump):
            bump()
        return router

    initialize = _ddl_initialize
