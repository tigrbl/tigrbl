# tigrbl/_concrete/tigrbl_router.py
from __future__ import annotations

import copy
import asyncio
import inspect
from types import SimpleNamespace
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Mapping,
    Optional,
    Sequence,
    Tuple,
)

from ._router import Router as _Router
from ._response import Response
from tigrbl_core._spec.engine_spec import EngineCfg
from tigrbl_core.config.constants import __JSONRPC_DEFAULT_ENDPOINT__
from tigrbl_concrete.ddl import initialize as _ddl_initialize
from tigrbl_concrete._mapping.router.include import (
    include_table as _include_table,
    include_tables as _include_tables,
)
from tigrbl_concrete._mapping.router.rpc import rpc_call as _rpc_call
from tigrbl_concrete._mapping.model import rebind as _rebind, bind as _bind
from ._op_registry import get_registry
from tigrbl_core._spec import OpSpec
from ._table_registry import TableRegistry
from ._route import compile_path
from ._websocket import WebSocketRoute
from tigrbl_concrete.system import mount_openrpc as _mount_openrpc
from tigrbl_concrete.system import mount_diagnostics as _mount_diagnostics
from tigrbl_concrete.system.docs import build_openapi as _build_openapi
from tigrbl_concrete._concrete import engine_resolver as _resolver
from ._engine import Engine
from ._rust_backend import (
    clear_ffi_boundary_events as _clear_rust_boundary_events,
    ffi_boundary_events as _rust_boundary_events,
    normalize_execution_backend as _normalize_execution_backend,
)


class TigrblRouter(_Router):
    """
    Canonical router-focused facade that owns:
      • containers (tables, schemas, handlers, hooks, rpc, rest, routers, columns, table_config, core proxies)
      • table inclusion (REST + RPC wiring)
      • (optional) auth knobs recognized by some middlewares/dispatchers

    It composes v3 primitives; you can still use the functions directly if you prefer.
    """

    PREFIX = ""
    REST_PREFIX = "/api"
    RPC_PREFIX = "/rpc"
    SYSTEM_PREFIX = "/system"
    TAGS: Sequence[Any] = ()
    ROUTERS: Sequence[Any] = ()
    TABLES: Sequence[Any] = ()

    # --- optional auth knobs recognized by some middlewares/dispatchers (kept for back-compat) ---
    _authn: Any = None
    _allow_anon: bool = True
    _authorize: Any = None
    _optional_authn_dep: Any = None
    _allow_anon_ops: set[str] = set()

    @staticmethod
    def _collect_declared_tables(owner: type) -> tuple[Any, ...]:
        collected: list[Any] = []
        seen: set[int] = set()
        for base in owner.__mro__:
            if "TABLES" not in base.__dict__:
                continue
            for table in tuple(base.__dict__.get("TABLES", ()) or ()):
                marker = id(table)
                if marker in seen:
                    continue
                seen.add(marker)
                collected.append(table)
        return tuple(collected)

    def __init__(
        self,
        *,
        engine: EngineCfg | None = None,
        tables: Sequence[type] | None = None,
        prefix: str | None = None,
        jsonrpc_prefix: str | None = None,
        system_prefix: str | None = None,
        router_hooks: Mapping[str, Iterable[Callable]]
        | Mapping[str, Mapping[str, Iterable[Callable]]]
        | None = None,
        execution_backend: str | None = None,
        **router_kwargs: Any,
    ) -> None:
        if prefix is not None:
            self.PREFIX = prefix
        _Router.__init__(self, engine=engine, **router_kwargs)
        self._authn = None
        self._allow_anon = True
        self._authorize = None
        self._optional_authn_dep = None
        self._allow_anon_ops: set[str] = set()
        self.jsonrpc_prefix = (
            jsonrpc_prefix
            if jsonrpc_prefix is not None
            else getattr(self, "RPC_PREFIX", getattr(self, "JSONRPC_PREFIX", "/rpc"))
        )
        self.system_prefix = (
            system_prefix
            if system_prefix is not None
            else getattr(self, "SYSTEM_PREFIX", "/system")
        )
        # ``prefix=...`` is the canonical REST mount prefix for router-scoped
        # table routes. Fall back to REST_PREFIX only when no explicit prefix
        # is provided.
        self.rest_prefix = (
            prefix if prefix is not None else getattr(self, "REST_PREFIX", "/api")
        )
        self.execution_backend = _normalize_execution_backend(execution_backend)

        # public containers (mirrors used by bindings.router)
        self.tables = TableRegistry(
            tables=self._collect_declared_tables(self.__class__)
        )
        self.schemas = SimpleNamespace()
        self.handlers = SimpleNamespace()
        self.hooks = SimpleNamespace()
        self.rpc = SimpleNamespace()
        self.rest = SimpleNamespace()
        self.routers: Dict[str, Any] = {}
        self.columns: Dict[str, Tuple[str, ...]] = {}
        self.table_config: Dict[str, Dict[str, Any]] = {}
        self.core = SimpleNamespace()
        self.core_raw = SimpleNamespace()
        self.websocket_routes: list[WebSocketRoute] = []
        self._static_mounts: list[dict[str, str]] = []
        self._jsonrpc_endpoint_mounts: dict[str, str] = {}
        self._tigrbl_runtime_resolve_provider = _resolver.resolve_provider
        self._tigrbl_runtime_acquire_db = _resolver.acquire

        # Router-level hooks map (merged into each model at include-time; precedence handled in bindings.hooks)
        self._router_hooks_map = copy.deepcopy(router_hooks) if router_hooks else None
        if tables:
            self.include_tables(list(tables))

    def rust_trace(self) -> list[dict[str, Any]]:
        return _rust_boundary_events()

    def clear_rust_trace(self) -> None:
        _clear_rust_boundary_events()

    # ------------------------- internal helpers -------------------------

    @staticmethod
    def _merge_router_hooks_into_model(model: type, hooks_map: Any) -> None:
        """
        Install Router-level hooks on the model so the binder can see them.
        Accepted shapes:
            {phase: [fn, ...]}                           # global, all aliases
            {alias: {phase: [fn, ...]}, "*": {...}}      # per-alias + wildcard
        If the model already has __tigrbl_router_hooks__, we shallow-merge keys.
        """
        if not hooks_map:
            return
        existing = getattr(model, "__tigrbl_router_hooks__", None)
        if existing is None:
            setattr(model, "__tigrbl_router_hooks__", copy.deepcopy(hooks_map))
            return

        # shallow merge (alias or phase keys); values are lists we extend
        merged = copy.deepcopy(existing)
        for k, v in (hooks_map or {}).items():
            if k not in merged:
                merged[k] = copy.deepcopy(v)
            else:
                # when both are dicts, merge phase lists
                if isinstance(v, Mapping) and isinstance(merged[k], Mapping):
                    for ph, fns in v.items():
                        merged[k].setdefault(ph, [])
                        merged[k][ph] = list(merged[k][ph]) + list(fns or [])
                else:
                    # fallback: prefer model-local value, then append router-level
                    if isinstance(merged[k], list):
                        merged[k] = list(merged[k]) + list(v or [])
                    else:
                        merged[k] = v
        setattr(model, "__tigrbl_router_hooks__", merged)

    # ------------------------- primary operations -------------------------

    def include_table(
        self, model: type, *, prefix: str | None = None, mount_router: bool = True
    ) -> Tuple[type, Any]:
        """
        Bind a model, mount its REST router, and attach all namespaces to this facade.
        """
        # inject Router-level hooks so the binder merges them
        self._merge_router_hooks_into_model(model, self._router_hooks_map)
        included_table, router = _include_table(
            self, model, app=None, prefix=prefix, mount_router=mount_router
        )
        if mount_router and router is not None:
            self.include_router(router, prefix=prefix)
        return included_table, router

    def include_tables(
        self,
        tables: Sequence[type],
        *,
        base_prefix: str | None = None,
        mount_router: bool = True,
    ) -> Dict[str, Any]:
        for m in tables:
            self._merge_router_hooks_into_model(m, self._router_hooks_map)
        included = _include_tables(
            self,
            tables,
            app=None,
            base_prefix=base_prefix,
            mount_router=mount_router,
        )
        if mount_router:
            for router in included.values():
                if router is not None:
                    self.include_router(router, prefix=base_prefix)
        return included

    def install_engines(
        self, *, router: Any | None = None, tables: tuple[Any, ...] | None = None
    ) -> None:
        """Install engine providers for this router and optional table set."""
        selected_router = self if router is None else router
        selected_tables = tables if tables is not None else tuple(self.tables.values())
        Engine.install_from_objects(
            router=selected_router, tables=tuple(selected_tables)
        )

    def initialize(
        self,
        *,
        schemas: Iterable[str] | None = None,
        sqlite_attachments: Mapping[str, str] | None = None,
        tables: Iterable[Any] | None = None,
    ):
        """Initialize DDL for this router."""
        try:
            result = _ddl_initialize(
                self,
                schemas=schemas,
                sqlite_attachments=sqlite_attachments,
                tables=tables,
            )
        except ValueError as exc:
            if str(exc) != "Engine provider is not configured":
                raise
            result = None

        if inspect.isawaitable(result):

            async def _inner() -> None:
                await result

            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                asyncio.run(_inner())
                return None
            return loop.create_task(_inner())

        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return None

        async def _noop() -> None:
            return None

        return _noop()

    async def rpc_call(
        self,
        model_or_name: type | str,
        method: str,
        payload: Any = None,
        *,
        db: Any | None = None,
        request: Any = None,
        ctx: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return await _rpc_call(
            self, model_or_name, method, payload, db=db, request=request, ctx=ctx
        )

    def mount_jsonrpc(
        self,
        *,
        prefix: str | None = None,
        endpoint: str = __JSONRPC_DEFAULT_ENDPOINT__,
        tags: Sequence[str] | None = ("rpc",),
    ) -> Any:
        from collections.abc import Mapping

        from tigrbl_concrete.transport.jsonrpc.helpers import (
            _err,
            _normalize_params,
            _ok,
        )
        from tigrbl_runtime.runtime.status.exceptions import HTTPException

        del tags
        if prefix is not None:
            self.jsonrpc_prefix = prefix
        endpoint = str(endpoint or __JSONRPC_DEFAULT_ENDPOINT__)

        async def _jsonrpc_endpoint(
            request: Any = None,
            body: Any = None,
            **_kwargs: Any,
        ) -> Any:
            def _exception_error(exc: BaseException, request_id: Any) -> dict[str, Any]:
                if isinstance(exc, HTTPException):
                    rpc_code = int(getattr(exc, "rpc_code", -32603))
                    rpc_message = str(
                        getattr(exc, "rpc_message", None)
                        or "Internal error"
                    )
                    rpc_data = getattr(exc, "rpc_data", None)
                    if rpc_data is None and isinstance(exc.detail, (dict, list)):
                        rpc_data = exc.detail
                    return _err(rpc_code, rpc_message, request_id, rpc_data)

                from tigrbl_runtime.runtime.status import create_standardized_error

                std = create_standardized_error(exc)
                rpc_code = int(getattr(std, "rpc_code", -32603))
                rpc_message = str(
                    getattr(std, "rpc_message", None)
                    or "Internal error"
                )
                rpc_data = getattr(std, "rpc_data", None)
                if rpc_data is None and isinstance(std.detail, (dict, list)):
                    rpc_data = std.detail
                return _err(rpc_code, rpc_message, request_id, rpc_data)

            async def _handle_one(payload: Mapping[str, Any]) -> tuple[dict[str, Any] | None, int]:
                request_id = payload.get("id")
                explicit_jsonrpc = payload.get("jsonrpc") == "2.0"
                notification = explicit_jsonrpc and "id" not in payload

                method = str(payload.get("method") or "")
                if not method:
                    return _err(-32600, "Method is required", request_id), 400

                model_name, dot, alias = method.partition(".")
                if not dot or not model_name or not alias:
                    return _err(-32601, "Method not found", request_id), 404

                try:
                    params = _normalize_params(payload.get("params"))
                    result = await self.rpc_call(
                        model_name,
                        alias,
                        params,
                        request=request,
                        ctx={"request": request},
                    )
                except AttributeError:
                    return _err(-32601, "Method not found", request_id), 404
                except Exception as exc:
                    if notification:
                        return None, 204
                    return _exception_error(exc, request_id), 200

                if notification:
                    return None, 204
                return _ok(result, request_id), 200

            try:
                payload = body
                if payload is None and request is not None:
                    payload = request.json_sync()
                if payload is None:
                    payload = {}

                if isinstance(payload, list):
                    responses: list[dict[str, Any]] = []
                    for item in payload:
                        if not isinstance(item, Mapping):
                            responses.append(_err(-32600, "Invalid Request", None))
                            continue
                        response, _status = await _handle_one(item)
                        if response is not None:
                            responses.append(response)
                    if not responses:
                        return Response(status_code=204)
                    return Response.json(responses, status_code=200)

                request_id = payload.get("id") if isinstance(payload, Mapping) else None
                if not isinstance(payload, Mapping):
                    return Response.json(
                        _err(-32600, "Invalid Request", request_id),
                        status_code=400,
                    )

                params_raw = payload.get("params")
                if (
                    payload.get("jsonrpc") == "2.0"
                    and isinstance(params_raw, Mapping)
                    and set(params_raw) == {"params"}
                ):
                    return Response(status_code=204)

                response, status_code = await _handle_one(payload)
                if response is None:
                    return Response(status_code=204)
                return Response.json(response, status_code=status_code)
            except HTTPException as exc:
                rpc_code = int(getattr(exc, "rpc_code", -32603))
                rpc_message = str(
                    getattr(exc, "rpc_message", None)
                    or "Internal error"
                )
                rpc_data = getattr(exc, "rpc_data", None)
                if rpc_data is None and isinstance(exc.detail, (dict, list)):
                    rpc_data = exc.detail
                return Response.json(
                    _err(rpc_code, rpc_message, request_id, rpc_data),
                    status_code=int(exc.status_code),
                )
            except AttributeError as exc:
                return Response.json(
                    _err(-32601, str(exc), request_id),
                    status_code=404,
                )
            except Exception as exc:
                from tigrbl_runtime.runtime.status import create_standardized_error

                std = create_standardized_error(exc)
                rpc_code = int(getattr(std, "rpc_code", -32603))
                rpc_message = str(
                    getattr(std, "rpc_message", None)
                    or "Internal error"
                )
                rpc_data = getattr(std, "rpc_data", None)
                if rpc_data is None and isinstance(std.detail, (dict, list)):
                    rpc_data = std.detail
                return Response.json(
                    _err(rpc_code, rpc_message, request_id, rpc_data),
                    status_code=int(getattr(std, "status_code", 500) or 500),
                )

        existing_paths = {getattr(route, "path", None) for route in self.routes}
        candidate_paths = (
            self.jsonrpc_prefix,
            f"{self.jsonrpc_prefix}/" if self.jsonrpc_prefix != "/" else "/",
        )
        for path in candidate_paths:
            self._jsonrpc_endpoint_mounts[path] = endpoint
            if path in existing_paths:
                continue
            self.add_route(
                path,
                _jsonrpc_endpoint,
                methods=["POST"],
            )
        return self

    def mount_openrpc(
        self,
        *,
        path: str = "/openrpc.json",
        name: str = "openrpc_json",
        tags: Sequence[str] | None = None,
    ) -> Any:
        """Mount an OpenRPC JSON endpoint onto this router instance."""
        return _mount_openrpc(self, path=path, name=name, tags=tags)

    def mount_json_schema(self, *, path: str = "/schemas.json") -> Any:
        from tigrbl_concrete.system import mount_json_schema as _mount_json_schema

        return _mount_json_schema(self, path=path)

    def mount_asyncapi(self, *, path: str = "/asyncapi.json") -> Any:
        from tigrbl_concrete.system import mount_asyncapi as _mount_asyncapi

        return _mount_asyncapi(self, path=path)

    def mount_static(self, *, directory: str, path: str = "/static") -> Any:
        from tigrbl_concrete.system import mount_static as _mount_static

        return _mount_static(self, directory=directory, path=path)

    def build_json_schema_bundle(self) -> Dict[str, Any]:
        from tigrbl_concrete.system import build_json_schema_bundle as _build_json_schema_bundle

        return _build_json_schema_bundle(self)

    def build_asyncapi_spec(self) -> Dict[str, Any]:
        from tigrbl_concrete.system import build_asyncapi_spec as _build_asyncapi_spec

        return _build_asyncapi_spec(self)

    def websocket(self, path: str, **kwargs: Any) -> Callable[[Any], Any]:
        def _decorator(handler: Any) -> Any:
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
            return handler

        return _decorator

    def attach_diagnostics(
        self, *, prefix: str | None = None, app: Any | None = None
    ) -> Any:
        """Mount diagnostics router onto this router or the provided ``app``."""
        px = prefix if prefix is not None else self.system_prefix
        prov = _resolver.resolve_provider(router=self)
        get_db = prov.get_db if prov else None
        router = _mount_diagnostics(self, get_db=get_db)
        self.include_router(router, prefix=px)
        if app is not None and app is not self:
            include_other = getattr(app, "include_router", None)
            if callable(include_other):
                include_other(router, prefix=px)
            app_tables = getattr(app, "tables", None)
            if isinstance(app_tables, dict):
                for name, model in getattr(self, "tables", {}).items():
                    app_tables.setdefault(name, model)
                default_router = getattr(app, "_default_router", None)
                if default_router is not None and isinstance(
                    getattr(default_router, "tables", None), dict
                ):
                    for name, model in getattr(self, "tables", {}).items():
                        default_router.tables.setdefault(name, model)
        return router

    def openapi(self) -> Dict[str, Any]:
        """Build and return the OpenAPI document for this router."""
        return _build_openapi(self)

    # ------------------------- registry passthroughs -------------------------

    def registry(self, model: type):
        """Return the per-model OpspecRegistry."""
        return get_registry(model)

    def bind(self, model: type) -> Tuple[OpSpec, ...]:
        """Bind/rebuild a model in place (without mounting)."""
        self._merge_router_hooks_into_model(model, self._router_hooks_map)
        return _bind(model)

    def rebind(
        self, model: type, *, changed_keys: Optional[set[tuple[str, str]]] = None
    ) -> Tuple[OpSpec, ...]:
        """Targeted rebuild of a bound model."""
        return _rebind(model, changed_keys=changed_keys)

    # Optional: let callers set auth knobs used by some middlewares/dispatchers
    def set_auth(
        self,
        *,
        authn: Any = None,
        allow_anon: Optional[bool] = None,
        authorize: Any = None,
        optional_authn_dep: Any = None,
    ) -> None:
        if authn is not None:
            self._authn = authn
            if allow_anon is None:
                allow_anon = False
        if allow_anon is not None:
            self._allow_anon = bool(allow_anon)
        if authorize is not None:
            self._authorize = authorize
        if optional_authn_dep is not None:
            self._optional_authn_dep = optional_authn_dep

        # Refresh already-included models so routers pick up new auth settings
        if self.tables:
            self._refresh_security()

    def _resolve_registered_model(self, name: str, value: Any) -> Any:
        if isinstance(value, type):
            return value
        core_proxy = getattr(self.core, name, None)
        model = getattr(core_proxy, "_model", None)
        return model if isinstance(model, type) else None

    def _refresh_security(self) -> None:
        """Re-seed auth deps on models and rebuild routers."""
        # Reset routes and allow_anon ops cache
        self.routes = []
        self._allow_anon_ops = set()
        for name, registered in list(self.tables.items()):
            model = self._resolve_registered_model(name, registered)
            if not isinstance(model, type):
                continue
            self.include_table(model, mount_router=False)

    def _collect_tables(self):
        # dedupe; handle multiple DeclarativeBases (multiple metadatas)
        seen = set()
        tables = []
        for name, registered in self.tables.items():
            table = (
                registered
                if not isinstance(registered, type)
                and hasattr(registered, "metadata")
                and hasattr(registered, "columns")
                else None
            )
            if table is None:
                model = self._resolve_registered_model(name, registered)
                table = (
                    getattr(model, "__table__", None)
                    if isinstance(model, type)
                    else None
                )
            if table is not None and not table.columns:
                continue
            if table is not None and table not in seen:
                seen.add(table)
                tables.append(table)
        return tables

    # ------------------------- repr -------------------------

    def __repr__(self) -> str:  # pragma: no cover
        tables = list(getattr(self, "tables", {}))
        rpc_ns = getattr(self, "rpc", None)
        rpc_keys = list(getattr(rpc_ns, "__dict__", {}).keys()) if rpc_ns else []
        return f"<TigrblRouter tables={tables} rpc={rpc_keys}>"
