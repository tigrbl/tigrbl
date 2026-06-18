# AppSpec and Internal Spec/Class Matrix

Classification rule: **AppSpec-related** means it can be authored directly in, or nested under, an `AppSpec` composition tree. **Internal-related** means it is support/runtime/registry/lowering machinery, even if public/exported.

## AppSpec Matrix

| Spec/dataclass/class | Level | Package | Module | Source |
|---|---:|---|---|---|
| `AppSpec` | App | `tigrbl_core` | `tigrbl_core._spec.app_spec` | [app_spec.py:90](pkgs/core/tigrbl_core/tigrbl_core/_spec/app_spec.py:90) |
| `RouterSpec` | App/Router | `tigrbl_core` | `tigrbl_core._spec.router_spec` | [router_spec.py:18](pkgs/core/tigrbl_core/tigrbl_core/_spec/router_spec.py:18) |
| `PathSpec` | Router/Path | `tigrbl_core` | `tigrbl_core._spec.path_spec` | [path_spec.py:40](pkgs/core/tigrbl_core/tigrbl_core/_spec/path_spec.py:40) |
| `TableSpec` | App/Router/Path/Table | `tigrbl_core` | `tigrbl_core._spec.table_spec` | [table_spec.py:60](pkgs/core/tigrbl_core/tigrbl_core/_spec/table_spec.py:60) |
| `OpSpec` | App/Router/Path/Table/Op | `tigrbl_core` | `tigrbl_core._spec.op_spec` | [op_spec.py:68](pkgs/core/tigrbl_core/tigrbl_core/_spec/op_spec.py:68) |
| `ColumnSpec` | Table/Column | `tigrbl_core` | `tigrbl_core._spec.column_spec` | [column_spec.py:17](pkgs/core/tigrbl_core/tigrbl_core/_spec/column_spec.py:17) |
| `FieldSpec` | Column/Field | `tigrbl_core` | `tigrbl_core._spec.field_spec` | [field_spec.py:29](pkgs/core/tigrbl_core/tigrbl_core/_spec/field_spec.py:29) |
| `IOSpec` | Column/IO | `tigrbl_core` | `tigrbl_core._spec.io_spec` | [io_spec.py:44](pkgs/core/tigrbl_core/tigrbl_core/_spec/io_spec.py:44) |
| `StorageSpec` | Column/Storage | `tigrbl_core` | `tigrbl_core._spec.storage_spec` | [storage_spec.py:36](pkgs/core/tigrbl_core/tigrbl_core/_spec/storage_spec.py:36) |
| `StorageTransformSpec` | Column/Storage | `tigrbl_core` | `tigrbl_core._spec.storage_spec` | [storage_spec.py:12](pkgs/core/tigrbl_core/tigrbl_core/_spec/storage_spec.py:12) |
| `ForeignKeySpec` | Column/Storage | `tigrbl_core` | `tigrbl_core._spec.storage_spec` | [storage_spec.py:24](pkgs/core/tigrbl_core/tigrbl_core/_spec/storage_spec.py:24) |
| `DataTypeSpec` | Column/Datatype | `tigrbl_core` | `tigrbl_core._spec.datatypes` | [datatypes.py:203](pkgs/core/tigrbl_core/tigrbl_core/_spec/datatypes.py:203) |
| `StorageTypeRef` | Column/Datatype | `tigrbl_core` | `tigrbl_core._spec.datatypes` | [datatypes.py:195](pkgs/core/tigrbl_core/tigrbl_core/_spec/datatypes.py:195) |
| `SchemaSpec` | Router/Table/Schema | `tigrbl_core` | `tigrbl_core._spec.schema_spec` | [schema_spec.py:38](pkgs/core/tigrbl_core/tigrbl_core/_spec/schema_spec.py:38) |
| `SchemaRef` | Op/Schema reference | `tigrbl_core` | `tigrbl_core._spec.schema_spec` | [schema_spec.py:22](pkgs/core/tigrbl_core/tigrbl_core/_spec/schema_spec.py:22) |
| `HookSpec` | Op/Hook | `tigrbl_core` | `tigrbl_core._spec.hook_spec` | [hook_spec.py:15](pkgs/core/tigrbl_core/tigrbl_core/_spec/hook_spec.py:15) |
| `ResponseSpec` | App/Router/Table/Op/Response | `tigrbl_core` | `tigrbl_core._spec.response_spec` | [response_spec.py:22](pkgs/core/tigrbl_core/tigrbl_core/_spec/response_spec.py:22) |
| `TemplateSpec` | Response/Template | `tigrbl_core` | `tigrbl_core._spec.response_spec` | [response_spec.py:12](pkgs/core/tigrbl_core/tigrbl_core/_spec/response_spec.py:12) |
| `EngineSpec` | App/Router/Table/Op/Engine | `tigrbl_core` | `tigrbl_core._spec.engine_spec` | [engine_spec.py:45](pkgs/core/tigrbl_core/tigrbl_core/_spec/engine_spec.py:45) |
| `EngineProviderSpec` | App/Router/Table/Op/Engine wrapper | `tigrbl_core` | `tigrbl_core._spec.engine_spec` | [engine_spec.py:14](pkgs/core/tigrbl_core/tigrbl_core/_spec/engine_spec.py:14) |
| `WellKnownResourceSpec` | App/Router/Path/Well-known | `tigrbl_core` | `tigrbl_core._spec.well_known_spec` | [well_known_spec.py:14](pkgs/core/tigrbl_core/tigrbl_core/_spec/well_known_spec.py:14) |
| `DocsProjectionSpec` | Path/Docs | `tigrbl_core` | `tigrbl_core._spec.docs_spec` | [docs_spec.py:27](pkgs/core/tigrbl_core/tigrbl_core/_spec/docs_spec.py:27) |
| `DocsPayloadSpec` | Path/Docs payload | `tigrbl_core` | `tigrbl_core._spec.docs_spec` | [docs_spec.py:136](pkgs/core/tigrbl_core/tigrbl_core/_spec/docs_spec.py:136) |
| `DocsUixSpec` | Path/Docs UIX | `tigrbl_core` | `tigrbl_core._spec.docs_spec` | [docs_spec.py:148](pkgs/core/tigrbl_core/tigrbl_core/_spec/docs_spec.py:148) |
| `MiddlewareSpec` | App/Router/Path/Middleware | `tigrbl_core` | `tigrbl_core._spec.middleware_spec` | [middleware_spec.py:19](pkgs/core/tigrbl_core/tigrbl_core/_spec/middleware_spec.py:19) |
| `TableProfileSpec` | Table/Profile | `tigrbl_core` | `tigrbl_core._spec.table_profile_spec` | [table_profile_spec.py:320](pkgs/core/tigrbl_core/tigrbl_core/_spec/table_profile_spec.py:320) |
| `BindingSpec` | Binding/Profile wrapper | `tigrbl_core` | `tigrbl_core._spec.binding_spec` | [binding_spec.py:506](pkgs/core/tigrbl_core/tigrbl_core/_spec/binding_spec.py:506) |
| `HTTPBindingSpec` | Op/Transport binding | `tigrbl_core` | `tigrbl_core._spec.binding_spec` | [binding_spec.py:242](pkgs/core/tigrbl_core/tigrbl_core/_spec/binding_spec.py:242) |
| `WebSocketBindingSpec` | Op/Transport binding | `tigrbl_core` | `tigrbl_core._spec.binding_spec` | [binding_spec.py:268](pkgs/core/tigrbl_core/tigrbl_core/_spec/binding_spec.py:268) |
| `HttpRestBindingSpec` | Op/Transport binding | `tigrbl_core` | `tigrbl_core._spec.binding_spec` | [binding_spec.py:293](pkgs/core/tigrbl_core/tigrbl_core/_spec/binding_spec.py:293) |
| `HttpJsonRpcBindingSpec` | Op/Transport binding | `tigrbl_core` | `tigrbl_core._spec.binding_spec` | [binding_spec.py:307](pkgs/core/tigrbl_core/tigrbl_core/_spec/binding_spec.py:307) |
| `HttpStreamBindingSpec` | Op/Transport binding | `tigrbl_core` | `tigrbl_core._spec.binding_spec` | [binding_spec.py:321](pkgs/core/tigrbl_core/tigrbl_core/_spec/binding_spec.py:321) |
| `SseBindingSpec` | Op/Transport binding | `tigrbl_core` | `tigrbl_core._spec.binding_spec` | [binding_spec.py:335](pkgs/core/tigrbl_core/tigrbl_core/_spec/binding_spec.py:335) |
| `WsBindingSpec` | Op/Transport binding | `tigrbl_core` | `tigrbl_core._spec.binding_spec` | [binding_spec.py:349](pkgs/core/tigrbl_core/tigrbl_core/_spec/binding_spec.py:349) |
| `WebTransportBindingSpec` | Op/Transport binding | `tigrbl_core` | `tigrbl_core._spec.binding_spec` | [binding_spec.py:375](pkgs/core/tigrbl_core/tigrbl_core/_spec/binding_spec.py:375) |
| `MessageBindingSpec` | Op/Transport binding | `tigrbl_core` | `tigrbl_core._spec.binding_spec` | [binding_spec.py:413](pkgs/core/tigrbl_core/tigrbl_core/_spec/binding_spec.py:413) |
| `DatagramBindingSpec` | Op/Transport binding | `tigrbl_core` | `tigrbl_core._spec.binding_spec` | [binding_spec.py:421](pkgs/core/tigrbl_core/tigrbl_core/_spec/binding_spec.py:421) |

## Internal Matrix

| Spec/dataclass/class | Level | Package | Module | Source |
|---|---:|---|---|---|
| `AliasSpec` | Internal alias contract | `tigrbl_core` | `tigrbl_core._spec.alias_spec` | [alias_spec.py:12](pkgs/core/tigrbl_core/tigrbl_core/_spec/alias_spec.py:12) |
| `BindingRegistrySpec` | Internal binding registry | `tigrbl_core` | `tigrbl_core._spec.binding_spec` | [binding_spec.py:514](pkgs/core/tigrbl_core/tigrbl_core/_spec/binding_spec.py:514) |
| `BindingEventKey` | Internal binding runtime key | `tigrbl_core` | `tigrbl_core._spec.binding_spec` | [binding_spec.py:552](pkgs/core/tigrbl_core/tigrbl_core/_spec/binding_spec.py:552) |
| `TypeAdapter` | Internal datatype protocol | `tigrbl_core` | `tigrbl_core._spec.datatypes` | [datatypes.py:277](pkgs/core/tigrbl_core/tigrbl_core/_spec/datatypes.py:277) |
| `BaseTypeAdapter` | Internal datatype adapter base | `tigrbl_core` | `tigrbl_core._spec.datatypes` | [datatypes.py:291](pkgs/core/tigrbl_core/tigrbl_core/_spec/datatypes.py:291) |
| `TypeRegistry` | Internal datatype registry | `tigrbl_core` | `tigrbl_core._spec.datatypes` | [datatypes.py:327](pkgs/core/tigrbl_core/tigrbl_core/_spec/datatypes.py:327) |
| `EngineTypeLowerer` | Internal engine lowering protocol | `tigrbl_core` | `tigrbl_core._spec.datatypes` | [datatypes.py:395](pkgs/core/tigrbl_core/tigrbl_core/_spec/datatypes.py:395) |
| `StaticEngineLowerer` | Internal engine lowering helper | `tigrbl_core` | `tigrbl_core._spec.datatypes` | [datatypes.py:401](pkgs/core/tigrbl_core/tigrbl_core/_spec/datatypes.py:401) |
| `EngineRegistry` | Internal engine datatype registry | `tigrbl_core` | `tigrbl_core._spec.datatypes` | [datatypes.py:415](pkgs/core/tigrbl_core/tigrbl_core/_spec/datatypes.py:415) |
| `EngineDatatypeBridge` | Internal engine datatype bridge | `tigrbl_core` | `tigrbl_core._spec.datatypes` | [datatypes.py:432](pkgs/core/tigrbl_core/tigrbl_core/_spec/datatypes.py:432) |
| `ReflectedDatatype` | Internal reflection payload | `tigrbl_core` | `tigrbl_core._spec.datatypes` | [datatypes.py:464](pkgs/core/tigrbl_core/tigrbl_core/_spec/datatypes.py:464) |
| `ReflectedTypeMapper` | Internal reflection mapper | `tigrbl_core` | `tigrbl_core._spec.datatypes` | [datatypes.py:470](pkgs/core/tigrbl_core/tigrbl_core/_spec/datatypes.py:470) |
| `DocsProjectionSelection` | Internal docs projection result | `tigrbl_core` | `tigrbl_core._spec.docs_spec` | [docs_spec.py:15](pkgs/core/tigrbl_core/tigrbl_core/_spec/docs_spec.py:15) |
| `ExposureDecision` | Internal exposure policy result | `tigrbl_core` | `tigrbl_core._spec.exposure_policy` | [exposure_policy.py:25](pkgs/core/tigrbl_core/tigrbl_core/_spec/exposure_policy.py:25) |
| `ExposurePolicyError` | Internal exposure policy error | `tigrbl_core` | `tigrbl_core._spec.exposure_policy` | [exposure_policy.py:32](pkgs/core/tigrbl_core/tigrbl_core/_spec/exposure_policy.py:32) |
| `ValidationInfo` | Internal field validation payload | `tigrbl_core` | `tigrbl_core._spec.field_spec` | [field_spec.py:10](pkgs/core/tigrbl_core/tigrbl_core/_spec/field_spec.py:10) |
| `HookPhase` | Internal/governed hook enum | `tigrbl_core` | `tigrbl_core._spec.hook_types` | [hook_types.py:9](pkgs/core/tigrbl_core/tigrbl_core/_spec/hook_types.py:9) |
| `_PairedCfg` | Internal IO derived-field config | `tigrbl_core` | `tigrbl_core._spec.io_spec` | [io_spec.py:9](pkgs/core/tigrbl_core/tigrbl_core/_spec/io_spec.py:9) |
| `_AssembleCfg` | Internal IO assembly config | `tigrbl_core` | `tigrbl_core._spec.io_spec` | [io_spec.py:20](pkgs/core/tigrbl_core/tigrbl_core/_spec/io_spec.py:20) |
| `_ReadtimeAlias` | Internal IO read-time alias config | `tigrbl_core` | `tigrbl_core._spec.io_spec` | [io_spec.py:26](pkgs/core/tigrbl_core/tigrbl_core/_spec/io_spec.py:26) |
| `Pair` | Internal IO helper payload | `tigrbl_core` | `tigrbl_core._spec.io_spec` | [io_spec.py:38](pkgs/core/tigrbl_core/tigrbl_core/_spec/io_spec.py:38) |
| `EngineRegistration` | Internal engine registration protocol | `tigrbl_core` | `tigrbl_core._spec.registry` | [registry.py:8](pkgs/core/tigrbl_core/tigrbl_core/_spec/registry.py:8) |
| `RequestSpec` | Internal request snapshot | `tigrbl_core` | `tigrbl_core._spec.request_spec` | [request_spec.py:10](pkgs/core/tigrbl_core/tigrbl_core/_spec/request_spec.py:10) |
| `SerdeMixin` | Internal serialization mixin | `tigrbl_core` | `tigrbl_core._spec.serde` | [serde.py:119](pkgs/core/tigrbl_core/tigrbl_core/_spec/serde.py:119) |
| `SessionSpec` | Internal session policy | `tigrbl_core` | `tigrbl_core._spec.session_spec` | [session_spec.py:12](pkgs/core/tigrbl_core/tigrbl_core/_spec/session_spec.py:12) |
| `BindingToken` | Internal table-profile binding token | `tigrbl_core` | `tigrbl_core._spec.table_profile_bindings` | [table_profile_bindings.py:116](pkgs/core/tigrbl_core/tigrbl_core/_spec/table_profile_bindings.py:116) |
| `LoweredBinding` | Internal table-profile lowering result | `tigrbl_core` | `tigrbl_core._spec.table_profile_bindings` | [table_profile_bindings.py:135](pkgs/core/tigrbl_core/tigrbl_core/_spec/table_profile_bindings.py:135) |
| `BuiltinTableProfile` | Internal builtin profile definition | `tigrbl_core` | `tigrbl_core._spec.table_profile_spec` | [table_profile_spec.py:24](pkgs/core/tigrbl_core/tigrbl_core/_spec/table_profile_spec.py:24) |
| `TableProfileError` | Internal table-profile error | `tigrbl_core` | `tigrbl_core._spec.table_profile_spec` | [table_profile_spec.py:315](pkgs/core/tigrbl_core/tigrbl_core/_spec/table_profile_spec.py:315) |
| `TableRegistrySpec` | Internal table registry payload | `tigrbl_core` | `tigrbl_core._spec.table_registry_spec` | [table_registry_spec.py:10](pkgs/core/tigrbl_core/tigrbl_core/_spec/table_registry_spec.py:10) |
| `BindingStackError` | Internal transport-stack error | `tigrbl_core` | `tigrbl_core._spec.transport_stack` | [transport_stack.py:23](pkgs/core/tigrbl_core/tigrbl_core/_spec/transport_stack.py:23) |
| `BindingStackProjection` | Internal transport-stack projection | `tigrbl_core` | `tigrbl_core._spec.transport_stack` | [transport_stack.py:28](pkgs/core/tigrbl_core/tigrbl_core/_spec/transport_stack.py:28) |
