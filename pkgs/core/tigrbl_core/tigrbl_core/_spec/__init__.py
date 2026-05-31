"""Canonical spec package.

Keep this module import-light to avoid circular imports during package startup.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

_EXPORTS = {
    "AliasSpec": "alias_spec",
    "AppSpec": "app_spec",
    "resolve_engine_name": "app_spec",
    "validate_engine_inventory": "app_spec",
    "validate_engine_name_binding": "app_spec",
    "BindingSpec": "binding_spec",
    "BindingRegistrySpec": "binding_spec",
    "APP_LEVEL_FRAMING_SUPPORT": "binding_spec",
    "BINDING_PROFILE_EXCHANGE_SUPPORT": "binding_spec",
    "BindingProfile": "binding_spec",
    "Exchange": "binding_spec",
    "Framing": "binding_spec",
    "TransportBindingSpec": "binding_spec",
    "HTTPBindingSpec": "binding_spec",
    "WebSocketBindingSpec": "binding_spec",
    "HttpRestBindingSpec": "binding_spec",
    "HttpJsonRpcBindingSpec": "binding_spec",
    "HttpStreamBindingSpec": "binding_spec",
    "SseBindingSpec": "binding_spec",
    "WebTransportBindingSpec": "binding_spec",
    "WsBindingSpec": "binding_spec",
    "resolve_rest_nested_prefix": "binding_spec",
    "ColumnSpec": "column_spec",
    "CANONICAL_DATATYPES": "datatypes",
    "DataTypeSpec": "datatypes",
    "EngineSpec": "engine_spec",
    "EngineProviderSpec": "engine_spec",
    "EngineDatatypeBridge": "datatypes",
    "EngineRegistry": "datatypes",
    "EngineTypeLowerer": "datatypes",
    "DocsPayloadKind": "docs_spec",
    "DocsPayloadSpec": "docs_spec",
    "DocsProjectionSelection": "docs_spec",
    "DocsProjectionSpec": "docs_spec",
    "DocsUixKind": "docs_spec",
    "DocsUixSpec": "docs_spec",
    "validate_docs_payload_path": "docs_spec",
    "validate_docs_tree": "docs_spec",
    "validate_docs_uix_path": "docs_spec",
    "FieldSpec": "field_spec",
    "F": "field_spec",
    "BaseTypeAdapter": "datatypes",
    "HookSpec": "hook_spec",
    "IOSpec": "io_spec",
    "IO": "io_spec",
    "ReflectedDatatype": "datatypes",
    "ReflectedTypeMapper": "datatypes",
    "StaticEngineLowerer": "datatypes",
    "as_tuple": "monotone",
    "MiddlewareSpec": "middleware_spec",
    "highest_precedence": "monotone",
    "keyed_overlay": "monotone",
    "mapping_overlay": "monotone",
    "merge_mro_mapping_attr": "monotone",
    "merge_mro_sequence_attr": "monotone",
    "OpSpec": "op_spec",
    "sequence_union": "monotone",
    "stable_keyed_overlay": "monotone",
    "stable_unique": "monotone",
    "Arity": "op_spec",
    "TargetOp": "op_spec",
    "PersistPolicy": "op_spec",
    "TxScope": "op_spec",
    "PathKind": "path_spec",
    "PathSpec": "path_spec",
    "path_for_binding": "path_spec",
    "canonical_binding_kind": "binding_spec",
    "normalize_binding_spec": "binding_spec",
    "validate_app_framing_for_binding": "binding_spec",
    "validate_binding_profile_exchange": "binding_spec",
    "validate_path_binding": "path_spec",
    "PHASE": "op_spec",
    "PHASES": "op_spec",
    "HookPhase": "hook_spec",
    "TemplateSpec": "response_spec",
    "ResponseSpec": "response_spec",
    "resolve_response_spec": "response_resolver",
    "RequestSpec": "request_spec",
    "RouterSpec": "router_spec",
    "SchemaSpec": "schema_spec",
    "SchemaRef": "schema_spec",
    "SchemaArg": "schema_spec",
    "SessionSpec": "session_spec",
    "session_spec": "session_spec",
    "tx_read_committed": "session_spec",
    "tx_repeatable_read": "session_spec",
    "tx_serializable": "session_spec",
    "readonly": "session_spec",
    "StorageTypeRef": "datatypes",
    "StorageSpec": "storage_spec",
    "S": "storage_spec",
    "StorageTransformSpec": "storage_spec",
    "StorageTransform": "storage_spec",
    "ForeignKeySpec": "storage_spec",
    "TypeAdapter": "datatypes",
    "TypeRegistry": "datatypes",
    "TableSpec": "table_spec",
    "TableRegistrySpec": "table_registry_spec",
}

__all__ = list(_EXPORTS)


def __getattr__(name: str) -> Any:
    if name in {"PHASE", "PHASES"}:
        from .hook_types import HookPhase, HookPhases

        value = HookPhase if name == "PHASE" else HookPhases
        globals()[name] = value
        return value
    if name in {"F", "IO", "S"}:
        aliases = {
            "F": ("field_spec", "FieldSpec"),
            "IO": ("io_spec", "IOSpec"),
            "S": ("storage_spec", "StorageSpec"),
        }
        module_name, attr = aliases[name]
        module = import_module(f"{__name__}.{module_name}")
        value = getattr(module, attr)
        globals()[name] = value
        return value

    module_name = _EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(name)
    module = import_module(f"{__name__}.{module_name}")
    value = getattr(module, name)
    globals()[name] = value
    return value
