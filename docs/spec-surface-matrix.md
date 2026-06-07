# Tigrbl Spec Surface Matrix

Generated from the current public `_spec` exports and concrete/factory/shortcut
surfaces on 2026-06-07. Cells contain real class names, method/function names,
module names, file names, or class attribute names only. Rows for discovered
surfaces without a first-class spec use `missing` in the Spec column.

Legend:

- `generated`: generated JSON Schema exists under `pkgs/core/tigrbl_core/schemas`.
- `gap`: expected or plausible surface, but not currently implemented.
- `missing`: no first-class spec row currently exists for the surface in that row.
- `n/a`: no current surface in that column.


| Spec | JSON schema | Dataclass | Base | Concrete(s) | Mount | Include | Include bulk | Class collection | Shortcut(s) | Decorator(s) | define_* | derive_* | make_* |
|---|---|---:|---|---|---|---|---|---|---|---|---|---|---|
| `AliasSpec` | none | no, ABC | `AliasBase` | `Alias` | n/a | n/a | n/a | n/a | n/a | `alias`, `alias_ctx`, `op_alias` | n/a | n/a | n/a |
| `AppSpec` | generated | yes | `AppBase` | `App`, `TigrblApp` | n/a | `include_router` | `include_routers` | `ROUTERS`, `TABLES`, `OPS`, `WELL_KNOWN`, `SCHEMAS`, `HOOKS`, `DEPS`, `SECURITY_DEPS`, `MIDDLEWARES`, `ENGINES`, `ENGINE`, `ENGINE_NAME`, `RESPONSE`, `JSONRPC_PREFIX`, `SYSTEM_PREFIX`, `LIFESPAN`, `TITLE`, `DESCRIPTION`, `VERSION`, `EXECUTION_BACKEND` | `tigrbl.shortcuts.app` | n/a | `defineAppSpec` | `deriveApp` | n/a |
| `BindingRegistrySpec` | generated | yes | `BindingRegistryBase` | `BindingRegistry` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| `BindingSpec` | generated | yes | `BindingBase` | `Binding` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| `ColumnSpec` | generated | no | `ColumnBase` | `Column` | n/a | n/a | n/a | n/a | `tigrbl.shortcuts.column`, `acol`, `vcol` | n/a | n/a | n/a | `makeColumn`, `makeVirtualColumn` |
| `DataTypeSpec` | generated | yes | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| `DocsPayloadSpec` | none | yes | n/a | n/a | `mount_openapi`, `mount_openrpc`, `mount_json_schema` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| `DocsProjectionSpec` | none | yes | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| `DocsUixSpec` | none | yes | n/a | n/a | `mount_swagger`, `mount_lens`, `mount_healthz_uix` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| `EngineProviderSpec` | generated | yes | `EngineProviderBase` | `Provider` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| `EngineRegistry` | none | no | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| `EngineSpec` | generated | yes | `EngineBase` | `Engine` | n/a | n/a | n/a | n/a | `tigrbl.shortcuts.engine`, `engine_spec`, `engine`, `prov`, `provider_sqlite_memory`, `provider_sqlite_file`, `provider_postgres`, `sqlite_cfg`, `pg_cfg`, `mem`, `sqlitef`, `pg`, `pga`, `pgs` | `engine_ctx` | n/a | n/a | n/a |
| `FieldSpec` | generated | yes | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| `ForeignKeySpec` | generated | yes | `ForeignKeyBase` | `ForeignKey` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| `HookSpec` | generated | yes | `HookBase` | `Hook` | n/a | n/a | n/a | n/a | `tigrbl.shortcuts.hook`, `hook_spec`, `hook` | `hook_ctx` | n/a | n/a | n/a |
| `HTTPBindingSpec` | none | yes | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| `HttpJsonRpcBindingSpec` | generated | yes | n/a | n/a | `mount_jsonrpc` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| `HttpRestBindingSpec` | generated | yes | n/a | n/a | `mount_rest` | n/a | n/a | n/a | `tigrbl.shortcuts.rest` | `get`, `post`, `put`, `patch`, `delete` | n/a | n/a | n/a |
| `HttpStreamBindingSpec` | generated | yes | n/a | n/a | n/a | n/a | n/a | n/a | n/a | `stream_ctx` | n/a | n/a | n/a |
| `IOSpec` | generated | yes | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| `MiddlewareSpec` | none | no | `MiddlewareBase` | `Middleware` | n/a | n/a | n/a | n/a | n/a | `middleware`, `middlewares`, `MiddlewareConfig` | n/a | n/a | n/a |
| `OpSpec` | generated | yes | `OpBase` | `Op` | n/a | n/a | n/a | n/a | `tigrbl.shortcuts.op`, `op` | `op_ctx` | n/a | n/a | `make` |
| `PathSpec` | none | yes | n/a | n/a | `mount_static`, `mount_app` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| `ReflectedDatatype` | none | yes | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| `RequestSpec` | generated | yes | `RequestBase` | `Request` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| `ResponseSpec` | generated | yes | `ResponseBase` | `Response`, `TransportResponse` | n/a | n/a | n/a | n/a | `tigrbl.shortcuts.responses`, `as_json`, `as_html`, `as_text`, `as_redirect`, `as_stream`, `as_event_stream`, `as_file` | `response_ctx` | n/a | n/a | n/a |
| `RouterSpec` | generated | yes | `RouterBase` | `Router`, `TigrblRouter` | n/a | `include_table` | `include_tables` | `PATHS`, `TAGS`, `PREFIX`, `NAME` | `tigrbl.shortcuts.router` | n/a | `defineRouterSpec` | `deriveRouter` | n/a |
| `SchemaRef` | generated | yes | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| `SchemaSpec` | generated | yes | `SchemaBase` | `Schema` | n/a | n/a | n/a | n/a | `tigrbl.shortcuts.schema`, `schema_spec`, `schema` | `schema_ctx` | n/a | n/a | n/a |
| `SessionSpec` | generated | yes | `SessionABC`, `TigrblSessionBase` | `DefaultSession` | n/a | n/a | n/a | n/a | `session_spec`, `readonly`, `tx_read_committed`, `tx_repeatable_read`, `tx_serializable` | `session_ctx`, `read_only_session` | n/a | n/a | n/a |
| `SseBindingSpec` | generated | yes | n/a | n/a | n/a | n/a | n/a | n/a | n/a | `sse_ctx` | n/a | n/a | n/a |
| `StorageSpec` | generated | yes | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| `StorageTransformSpec` | generated | yes | `StorageTransformBase` | `StorageTransform` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| `StorageTypeRef` | generated | yes | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| `TableRegistrySpec` | generated | yes | `TableRegistryBase` | `TableRegistry` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| `TableSpec` | generated | yes | `TableBase` | `Table` | n/a | `include_model` | `include_models` | `COLUMNS` | `tigrbl.shortcuts.table` | `allow_anon` | `defineTableSpec` | `deriveTable` | n/a |
| `TemplateSpec` | generated | yes | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| `TransportBindingSpec` | none | no | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| `TypeRegistry` | none | no | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| `WebSocketBindingSpec` | none | yes | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| `WebTransportBindingSpec` | generated | yes | n/a | n/a | n/a | n/a | n/a | n/a | n/a | `webtransport_ctx` | n/a | n/a | n/a |
| `WellKnownResourceSpec` | none | yes | n/a | `WellKnownResource` | `mount_well_known` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| `WsBindingSpec` | generated | yes | n/a | n/a | n/a | n/a | n/a | n/a | n/a | `websocket_ctx` | n/a | n/a | n/a |
| missing | `schemas/bundle.json` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | `schemas/shared.json` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | no | `AttrDict` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | no | n/a | `Route` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | no | n/a | `BackgroundTask` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | no | n/a | `Body` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | no | n/a | `UploadedFile` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | no | n/a | `WebSocket` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | no | n/a | `Dependency` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | no | n/a | `APIKey` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | no | n/a | `HTTPBasic` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | no | n/a | `HTTPBearer` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | no | `OpenAPISecurityDependency` | `OAuth2` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | no | n/a | `OpenIdConnect` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | no | n/a | `MutualTLS` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | no | n/a | `CORSMiddleware` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | no | n/a | `FAVICON_PATH` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | no | n/a | `HTMLResponse` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | no | n/a | `JSONResponse` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | no | n/a | `PlainTextResponse` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | no | n/a | `StreamingResponse` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | no | n/a | `EventStreamResponse` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | no | n/a | `FileResponse` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | no | n/a | `RedirectResponse` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | no | n/a | `wrap_sessionmaker` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | n/a | n/a | n/a | `mount_diagnostics` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | n/a | n/a | n/a | `mount_favicon` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | n/a | n/a | n/a | `build_healthz_uix` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | n/a | n/a | n/a | `build_openapi` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | n/a | n/a | n/a | `build_swagger` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | n/a | n/a | n/a | `build_lens` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | n/a | n/a | n/a | `build_favicon` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | n/a | n/a | n/a | `build_openrpc_spec` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | n/a | n/a | n/a | `build_json_schema_bundle` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | n/a | n/a | n/a | `build_rest_router` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | n/a | n/a | n/a | `stop_uvicorn_server` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | n/a | n/a | n/a | `normalize_well_known_name` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | n/a | n/a | n/a | `well_known_path` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | n/a | n/a | n/a | n/a | `bind` | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | n/a | n/a | n/a | n/a | `rebind` | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | n/a | n/a | n/a | n/a | `build_schemas` | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | n/a | n/a | n/a | n/a | `build_hooks` | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | n/a | n/a | n/a | n/a | `build_handlers` | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | n/a | n/a | n/a | n/a | `register_rpc` | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | n/a | n/a | n/a | n/a | `build_rest` | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | n/a | n/a | n/a | n/a | `rpc_call` | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | n/a | n/a | n/a | n/a | `set_auth` | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | n/a | n/a | n/a | n/a | `add_middleware` | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | n/a | n/a | n/a | n/a | `add_route` | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | n/a | n/a | n/a | n/a | `add_router_route` | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | n/a | n/a | n/a | n/a | `attach_diagnostics` | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | n/a | n/a | n/a | n/a | `initialize` | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | n/a | n/a | n/a | n/a | `install_engines` | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | n/a | n/a | n/a | n/a | `registry` | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | n/a | n/a | n/a | n/a | n/a | n/a | `table_config` | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | n/a | n/a | n/a | n/a | n/a | n/a | `__tigrbl_allow_anon__` | n/a | n/a | n/a | n/a | n/a |
| missing | none; missing spec | n/a | n/a | n/a | n/a | n/a | n/a | n/a | `tigrbl.decorators` | n/a | n/a | n/a | n/a |
| missing | none; missing spec | n/a | n/a | n/a | n/a | n/a | n/a | n/a | `tigrbl.factories` | n/a | n/a | n/a | n/a |
| missing | none; missing spec | n/a | n/a | n/a | n/a | n/a | n/a | n/a | `Depends` | n/a | n/a | n/a | n/a |
| missing | none; missing spec | n/a | n/a | n/a | n/a | n/a | n/a | n/a | `Security` | n/a | n/a | n/a | n/a |
