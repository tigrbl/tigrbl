from __future__ import annotations

from typing import Any

JSON_SCHEMA_DRAFT_2020_12 = "https://json-schema.org/draft/2020-12/schema"
SHARED_SCHEMA_NAME = "shared.json"

INDIVIDUAL_SPEC_NAMES: tuple[str, ...] = (
    "AppSpec",
    "BindingRegistrySpec",
    "BindingSpec",
    "ColumnSpec",
    "DataTypeSpec",
    "EngineProviderSpec",
    "EngineSpec",
    "FieldSpec",
    "ForeignKeySpec",
    "HookSpec",
    "HttpJsonRpcBindingSpec",
    "HttpRestBindingSpec",
    "HttpStreamBindingSpec",
    "IOSpec",
    "OpSpec",
    "RequestSpec",
    "ResponseSpec",
    "RouterSpec",
    "SchemaRef",
    "SchemaSpec",
    "SessionSpec",
    "SseBindingSpec",
    "StorageSpec",
    "StorageTransformSpec",
    "StorageTypeRef",
    "TableRegistrySpec",
    "TableSpec",
    "TemplateSpec",
    "WebTransportBindingSpec",
    "WsBindingSpec",
)

_CANONICAL_DATATYPES = (
    "string",
    "integer",
    "number",
    "decimal",
    "boolean",
    "bytes",
    "date",
    "datetime",
    "time",
    "duration",
    "json",
    "object",
    "array",
    "uuid",
    "ulid",
)


def _shared_ref(name: str) -> dict[str, str]:
    return {"$ref": f"./{SHARED_SCHEMA_NAME}#/$defs/{name}"}


def _spec_ref(name: str) -> dict[str, str]:
    return {"$ref": f"./{name}.json"}


def _spec_envelope_ref(name: str) -> dict[str, str]:
    return {"$ref": f"./{name}.json#/$defs/{name}Envelope"}


def _nullable(schema: dict[str, Any]) -> dict[str, Any]:
    return {"anyOf": [schema, {"type": "null"}]}


def _spec_or_envelope(name: str) -> dict[str, Any]:
    return {"anyOf": [_spec_ref(name), _spec_envelope_ref(name)]}


def _object_schema(
    title: str,
    properties: dict[str, Any],
    *,
    required: tuple[str, ...] | None = None,
    additional_properties: bool = False,
) -> dict[str, Any]:
    return {
        "title": title,
        "type": "object",
        "properties": properties,
        "required": list(required if required is not None else tuple(properties)),
        "additionalProperties": additional_properties,
    }


def _envelope_schema(spec_name: str, class_path: str) -> dict[str, Any]:
    return {
        "title": f"{spec_name}Envelope",
        "type": "object",
        "properties": {
            "__dataclass__": {"const": class_path},
        },
        "required": ["__dataclass__"],
        "additionalProperties": _shared_ref("SerdeValue"),
    }


def _root_schema(spec_name: str, class_path: str, body: dict[str, Any]) -> dict[str, Any]:
    schema = {
        "$schema": JSON_SCHEMA_DRAFT_2020_12,
        "$id": f"{spec_name}.json",
        **body,
        "$defs": {
            f"{spec_name}Envelope": _envelope_schema(spec_name, class_path),
        },
    }
    schema.setdefault("title", spec_name)
    return schema


def build_shared_json_schema() -> dict[str, Any]:
    defs: dict[str, Any] = {
        "ImportPath": {
            "type": "string",
            "pattern": r"^.+:.+$",
            "description": "Python import path in module:qualname form.",
        },
        "SerdeArray": {"type": "array", "items": _shared_ref("SerdeValue")},
        "SerdeObject": {"type": "object", "additionalProperties": _shared_ref("SerdeValue")},
        "SerdeTupleEnvelope": {
            "type": "object",
            "properties": {"__tuple__": {"type": "array", "items": _shared_ref("SerdeValue")}},
            "required": ["__tuple__"],
            "additionalProperties": False,
        },
        "SerdeClassEnvelope": _object_schema(
            "SerdeClassEnvelope",
            {"__class__": _shared_ref("ImportPath")},
        ),
        "SerdeCallableEnvelope": _object_schema(
            "SerdeCallableEnvelope",
            {"__callable__": _shared_ref("ImportPath")},
        ),
        "SerdeDataclassEnvelope": {
            "title": "SerdeDataclassEnvelope",
            "type": "object",
            "properties": {"__dataclass__": _shared_ref("ImportPath")},
            "required": ["__dataclass__"],
            "additionalProperties": _shared_ref("SerdeValue"),
        },
    }
    defs["SerdeValue"] = {
        "title": "SerdeValue",
        "anyOf": [
            {"type": "null"},
            {"type": "boolean"},
            {"type": "integer"},
            {"type": "number"},
            {"type": "string"},
            _shared_ref("SerdeArray"),
            _shared_ref("SerdeObject"),
            _shared_ref("SerdeTupleEnvelope"),
            _shared_ref("SerdeClassEnvelope"),
            _shared_ref("SerdeCallableEnvelope"),
            _shared_ref("SerdeDataclassEnvelope"),
        ],
    }
    defs["StringTuple"] = {
        "type": "object",
        "properties": {"__tuple__": {"type": "array", "items": {"type": "string"}}},
        "required": ["__tuple__"],
        "additionalProperties": False,
    }
    defs["StepFnTuple"] = {
        "type": "object",
        "properties": {"__tuple__": {"type": "array", "items": _shared_ref("SerdeValue")}},
        "required": ["__tuple__"],
        "additionalProperties": False,
    }
    defs["HookFamilyTuple"] = {
        "type": "object",
        "properties": {"__tuple__": {"type": "array", "items": {"type": "string"}}},
        "required": ["__tuple__"],
        "additionalProperties": False,
    }
    defs["StringMap"] = {"type": "object", "additionalProperties": {"type": "string"}}
    defs["StringListMap"] = {
        "type": "object",
        "additionalProperties": {"type": "array", "items": {"type": "string"}},
    }
    defs["AnyMap"] = {"type": "object", "additionalProperties": _shared_ref("SerdeValue")}
    defs["TransportBindingSpec"] = {
        "anyOf": [
            _spec_ref("HttpRestBindingSpec"),
            _spec_ref("HttpJsonRpcBindingSpec"),
            _spec_ref("HttpStreamBindingSpec"),
            _spec_ref("SseBindingSpec"),
            _spec_ref("WsBindingSpec"),
            _spec_ref("WebTransportBindingSpec"),
            _spec_envelope_ref("HttpRestBindingSpec"),
            _spec_envelope_ref("HttpJsonRpcBindingSpec"),
            _spec_envelope_ref("HttpStreamBindingSpec"),
            _spec_envelope_ref("SseBindingSpec"),
            _spec_envelope_ref("WsBindingSpec"),
            _spec_envelope_ref("WebTransportBindingSpec"),
        ]
    }
    return {
        "$schema": JSON_SCHEMA_DRAFT_2020_12,
        "$id": SHARED_SCHEMA_NAME,
        "title": "Tigrbl Core Shared JSON Schema Definitions",
        "$defs": defs,
    }


def build_individual_spec_json_schemas() -> dict[str, dict[str, Any]]:
    schemas: dict[str, dict[str, Any]] = {}

    schemas["StorageTypeRef"] = _root_schema(
        "StorageTypeRef",
        "tigrbl_core._spec.datatypes:StorageTypeRef",
        _object_schema(
            "StorageTypeRef",
            {
                "physical_name": {"type": "string"},
                "engine_kind": _nullable({"type": "string"}),
            },
        ),
    )

    schemas["DataTypeSpec"] = _root_schema(
        "DataTypeSpec",
        "tigrbl_core._spec.datatypes:DataTypeSpec",
        _object_schema(
            "DataTypeSpec",
            {
                "logical_name": {"type": "string", "enum": list(_CANONICAL_DATATYPES)},
                "nullable": {"type": "boolean"},
                "options": _shared_ref("AnyMap"),
            },
        ),
    )

    schemas["FieldSpec"] = _root_schema(
        "FieldSpec",
        "tigrbl_core._spec.field_spec:FieldSpec",
        _object_schema(
            "FieldSpec",
            {
                "py_type": _shared_ref("SerdeValue"),
                "constraints": _shared_ref("AnyMap"),
                "description": _nullable({"type": "string"}),
                "required_in": _shared_ref("StringTuple"),
                "allow_null_in": _shared_ref("StringTuple"),
            },
        ),
    )

    schemas["IOSpec"] = _root_schema(
        "IOSpec",
        "tigrbl_core._spec.io_spec:IOSpec",
        _object_schema(
            "IOSpec",
            {
                "in_verbs": _shared_ref("StringTuple"),
                "out_verbs": _shared_ref("StringTuple"),
                "mutable_verbs": _shared_ref("StringTuple"),
                "alias_in": _nullable({"type": "string"}),
                "alias_out": _nullable({"type": "string"}),
                "header_in": _nullable({"type": "string"}),
                "header_out": _nullable({"type": "string"}),
                "header_required_in": {"type": "boolean"},
                "sensitive": {"type": "boolean"},
                "redact_last": _nullable({"type": "integer"}),
                "filter_ops": _shared_ref("StringTuple"),
                "sortable": {"type": "boolean"},
                "allow_in": _nullable(_shared_ref("SerdeValue")),
                "allow_out": _nullable(_shared_ref("SerdeValue")),
                "_paired": _nullable(_shared_ref("SerdeValue")),
                "_assemble": _nullable(_shared_ref("SerdeValue")),
                "_readtime_aliases": _shared_ref("StepFnTuple"),
            },
        ),
    )

    schemas["ForeignKeySpec"] = _root_schema(
        "ForeignKeySpec",
        "tigrbl_core._spec.storage_spec:ForeignKeySpec",
        _object_schema(
            "ForeignKeySpec",
            {
                "target": {"type": "string"},
                "on_delete": {
                    "type": "string",
                    "enum": ["CASCADE", "RESTRICT", "SET NULL", "SET DEFAULT"],
                },
                "on_update": {
                    "type": "string",
                    "enum": ["CASCADE", "RESTRICT", "SET NULL", "SET DEFAULT"],
                },
                "deferrable": {"type": "boolean"},
                "initially_deferred": {"type": "boolean"},
                "match": {"type": "string", "enum": ["FULL", "PARTIAL", "SIMPLE"]},
            },
        ),
    )

    schemas["StorageTransformSpec"] = _root_schema(
        "StorageTransformSpec",
        "tigrbl_core._spec.storage_spec:StorageTransformSpec",
        _object_schema(
            "StorageTransformSpec",
            {
                "to_stored": _nullable(_shared_ref("SerdeValue")),
                "from_stored": _nullable(_shared_ref("SerdeValue")),
            },
        ),
    )

    schemas["StorageSpec"] = _root_schema(
        "StorageSpec",
        "tigrbl_core._spec.storage_spec:StorageSpec",
        _object_schema(
            "StorageSpec",
            {
                "type_": _nullable(_shared_ref("SerdeValue")),
                "physical_type": _nullable(_spec_or_envelope("StorageTypeRef")),
                "nullable": _nullable({"type": "boolean"}),
                "unique": {"type": "boolean"},
                "index": {"type": "boolean"},
                "primary_key": {"type": "boolean"},
                "autoincrement": _nullable({"type": "boolean"}),
                "default": _nullable(_shared_ref("SerdeValue")),
                "onupdate": _nullable(_shared_ref("SerdeValue")),
                "server_default": _nullable(_shared_ref("SerdeValue")),
                "refresh_on_return": {"type": "boolean"},
                "transform": _nullable(_spec_or_envelope("StorageTransformSpec")),
                "fk": _nullable(_spec_or_envelope("ForeignKeySpec")),
                "check": _nullable({"type": "string"}),
                "comment": _nullable({"type": "string"}),
            },
        ),
    )

    schemas["ColumnSpec"] = _root_schema(
        "ColumnSpec",
        "tigrbl_core._spec.column_spec:ColumnSpec",
        _object_schema(
            "ColumnSpec",
            {
                "storage": _nullable(_spec_or_envelope("StorageSpec")),
                "field": _nullable(_spec_or_envelope("FieldSpec")),
                "io": _nullable(_spec_or_envelope("IOSpec")),
                "datatype": _nullable(_spec_or_envelope("DataTypeSpec")),
                "default_factory": _nullable(_shared_ref("SerdeValue")),
                "read_producer": _nullable(_shared_ref("SerdeValue")),
            },
        ),
    )

    schemas["SchemaRef"] = _root_schema(
        "SchemaRef",
        "tigrbl_core._spec.schema_spec:SchemaRef",
        _object_schema(
            "SchemaRef",
            {
                "alias": {"type": "string"},
                "kind": {"type": "string", "enum": ["in", "out"]},
            },
        ),
    )

    schemas["SchemaSpec"] = _root_schema(
        "SchemaSpec",
        "tigrbl_core._spec.schema_spec:SchemaSpec",
        _object_schema(
            "SchemaSpec",
            {
                "alias": {"type": "string"},
                "kind": {"type": "string", "enum": ["in", "out"]},
                "for_": _nullable(_shared_ref("SerdeValue")),
                "schema": _nullable(_shared_ref("SerdeValue")),
            },
        ),
    )

    schemas["EngineSpec"] = _root_schema(
        "EngineSpec",
        "tigrbl_core._spec.engine_spec:EngineSpec",
        _object_schema(
            "EngineSpec",
            {
                "kind": _nullable({"type": "string"}),
                "async_": {"type": "boolean"},
                "dsn": _nullable({"type": "string"}),
                "mapping": _nullable(_shared_ref("SerdeObject")),
                "path": _nullable({"type": "string"}),
                "memory": {"type": "boolean"},
                "pool": _nullable({"type": "string"}),
                "user": _nullable({"type": "string"}),
                "pwd": _nullable({"type": "string"}),
                "host": _nullable({"type": "string"}),
                "port": _nullable({"type": "integer"}),
                "name": _nullable({"type": "string"}),
                "pool_size": {"type": "integer"},
                "max": {"type": "integer"},
            },
        ),
    )

    schemas["EngineProviderSpec"] = _root_schema(
        "EngineProviderSpec",
        "tigrbl_core._spec.engine_spec:EngineProviderSpec",
        _object_schema(
            "EngineProviderSpec",
            {
                "spec": _spec_or_envelope("EngineSpec"),
            },
        ),
    )

    schemas["TemplateSpec"] = _root_schema(
        "TemplateSpec",
        "tigrbl_core._spec.response_spec:TemplateSpec",
        _object_schema(
            "TemplateSpec",
            {
                "name": {"type": "string"},
                "search_paths": {"type": "array", "items": {"type": "string"}},
                "package": _nullable({"type": "string"}),
                "auto_reload": _nullable({"type": "boolean"}),
                "filters": _shared_ref("SerdeObject"),
                "globals": _shared_ref("SerdeObject"),
            },
        ),
    )

    schemas["ResponseSpec"] = _root_schema(
        "ResponseSpec",
        "tigrbl_core._spec.response_spec:ResponseSpec",
        _object_schema(
            "ResponseSpec",
            {
                "kind": {
                    "type": "string",
                    "enum": ["auto", "json", "html", "text", "file", "stream", "redirect"],
                },
                "media_type": _nullable({"type": "string"}),
                "status_code": _nullable({"type": "integer"}),
                "headers": _shared_ref("StringMap"),
                "envelope": _nullable({"type": "boolean"}),
                "template": _nullable(_spec_or_envelope("TemplateSpec")),
                "filename": _nullable({"type": "string"}),
                "download": _nullable({"type": "boolean"}),
                "etag": _nullable({"type": "string"}),
                "cache_control": _nullable({"type": "string"}),
                "redirect_to": _nullable({"type": "string"}),
            },
        ),
    )

    schemas["RequestSpec"] = _root_schema(
        "RequestSpec",
        "tigrbl_core._spec.request_spec:RequestSpec",
        _object_schema(
            "RequestSpec",
            {
                "method": {"type": "string"},
                "path": {"type": "string"},
                "headers": _shared_ref("StringMap"),
                "query": _shared_ref("StringListMap"),
                "path_params": _shared_ref("StringMap"),
                "body": {"type": "string"},
                "script_name": {"type": "string"},
                "app": _nullable(_shared_ref("SerdeValue")),
            },
        ),
    )

    schemas["HttpRestBindingSpec"] = _root_schema(
        "HttpRestBindingSpec",
        "tigrbl_core._spec.binding_spec:HttpRestBindingSpec",
        _object_schema(
            "HttpRestBindingSpec",
            {
                "proto": {"type": "string", "enum": ["http.rest", "https.rest"]},
                "methods": _shared_ref("StringTuple"),
                "path": {"type": "string"},
                "exchange": {"type": "string"},
                "framing": {"type": "string"},
            },
        ),
    )

    schemas["HttpJsonRpcBindingSpec"] = _root_schema(
        "HttpJsonRpcBindingSpec",
        "tigrbl_core._spec.binding_spec:HttpJsonRpcBindingSpec",
        _object_schema(
            "HttpJsonRpcBindingSpec",
            {
                "proto": {"type": "string", "enum": ["http.jsonrpc", "https.jsonrpc"]},
                "rpc_method": {"type": "string"},
                "exchange": {"type": "string"},
                "framing": {"type": "string"},
            },
        ),
    )

    schemas["HttpStreamBindingSpec"] = _root_schema(
        "HttpStreamBindingSpec",
        "tigrbl_core._spec.binding_spec:HttpStreamBindingSpec",
        _object_schema(
            "HttpStreamBindingSpec",
            {
                "proto": {"type": "string", "enum": ["http.stream", "https.stream"]},
                "path": {"type": "string"},
                "methods": _shared_ref("StringTuple"),
                "exchange": {"type": "string"},
                "framing": {"type": "string"},
            },
        ),
    )

    schemas["SseBindingSpec"] = _root_schema(
        "SseBindingSpec",
        "tigrbl_core._spec.binding_spec:SseBindingSpec",
        _object_schema(
            "SseBindingSpec",
            {
                "proto": {"type": "string", "enum": ["http.sse", "https.sse"]},
                "path": {"type": "string"},
                "methods": _shared_ref("StringTuple"),
                "exchange": {"type": "string"},
                "framing": {"type": "string"},
            },
        ),
    )

    schemas["WsBindingSpec"] = _root_schema(
        "WsBindingSpec",
        "tigrbl_core._spec.binding_spec:WsBindingSpec",
        _object_schema(
            "WsBindingSpec",
            {
                "proto": {"type": "string", "enum": ["ws", "wss"]},
                "path": {"type": "string"},
                "subprotocols": _shared_ref("StringTuple"),
                "exchange": {"type": "string"},
                "framing": {"type": "string"},
            },
        ),
    )

    schemas["WebTransportBindingSpec"] = _root_schema(
        "WebTransportBindingSpec",
        "tigrbl_core._spec.binding_spec:WebTransportBindingSpec",
        _object_schema(
            "WebTransportBindingSpec",
            {
                "proto": {"type": "string", "const": "webtransport"},
                "path": {"type": "string"},
                "exchange": {"type": "string"},
                "framing": {"type": "string"},
            },
        ),
    )

    schemas["BindingSpec"] = _root_schema(
        "BindingSpec",
        "tigrbl_core._spec.binding_spec:BindingSpec",
        _object_schema(
            "BindingSpec",
            {
                "name": {"type": "string"},
                "spec": _shared_ref("TransportBindingSpec"),
            },
        ),
    )

    schemas["BindingRegistrySpec"] = _root_schema(
        "BindingRegistrySpec",
        "tigrbl_core._spec.binding_spec:BindingRegistrySpec",
        _object_schema(
            "BindingRegistrySpec",
            {
                "_bindings": {"type": "object", "additionalProperties": _spec_or_envelope("BindingSpec")},
            },
        ),
    )

    schemas["HookSpec"] = _root_schema(
        "HookSpec",
        "tigrbl_core._spec.hook_spec:HookSpec",
        _object_schema(
            "HookSpec",
            {
                "phase": {"type": "string"},
                "fn": _shared_ref("SerdeValue"),
                "ops": {"anyOf": [{"type": "string"}, _shared_ref("StringTuple")]},
                "bindings": _shared_ref("StringTuple"),
                "exchange": _nullable({"type": "string"}),
                "family": _shared_ref("HookFamilyTuple"),
                "subevents": _shared_ref("StringTuple"),
                "order": {"type": "integer"},
                "when": _nullable(_shared_ref("SerdeValue")),
                "name": _nullable({"type": "string"}),
                "description": _nullable({"type": "string"}),
            },
        ),
    )

    schemas["OpSpec"] = _root_schema(
        "OpSpec",
        "tigrbl_core._spec.op_spec:OpSpec",
        _object_schema(
            "OpSpec",
            {
                "alias": {"type": "string"},
                "target": {"type": "string"},
                "table": _nullable(_shared_ref("SerdeValue")),
                "expose_routes": {"type": "boolean"},
                "expose_rpc": {"type": "boolean"},
                "expose_method": {"type": "boolean"},
                "bindings": {
                    "type": "object",
                    "properties": {"__tuple__": {"type": "array", "items": _shared_ref("TransportBindingSpec")}},
                    "required": ["__tuple__"],
                    "additionalProperties": False,
                },
                "exchange": {"type": "string"},
                "tx_scope": {"type": "string"},
                "subevents": _shared_ref("StringTuple"),
                "engine": _nullable(_shared_ref("SerdeValue")),
                "arity": {"type": "string", "enum": ["collection", "member"]},
                "http_methods": _nullable(_shared_ref("StringTuple")),
                "path_suffix": _nullable({"type": "string"}),
                "tags": _shared_ref("StringTuple"),
                "status_code": _nullable({"type": "integer"}),
                "response": _nullable(_spec_or_envelope("ResponseSpec")),
                "persist": {"type": "string"},
                "request_model": _nullable(_shared_ref("SerdeValue")),
                "response_model": _nullable(_shared_ref("SerdeValue")),
                "returns": {"type": "string", "enum": ["raw", "model"]},
                "handler": _nullable(_shared_ref("SerdeValue")),
                "hooks": {
                    "type": "object",
                    "properties": {"__tuple__": {"type": "array", "items": _spec_or_envelope("HookSpec")}},
                    "required": ["__tuple__"],
                    "additionalProperties": False,
                },
                "core": _nullable(_shared_ref("SerdeValue")),
                "core_raw": _nullable(_shared_ref("SerdeValue")),
                "extra": _shared_ref("AnyMap"),
                "deps": _shared_ref("StepFnTuple"),
                "security_deps": _shared_ref("StepFnTuple"),
                "secdeps": _shared_ref("StepFnTuple"),
            },
        ),
    )

    schemas["TableSpec"] = _root_schema(
        "TableSpec",
        "tigrbl_core._spec.table_spec:TableSpec",
        _object_schema(
            "TableSpec",
            {
                "model": _nullable(_shared_ref("SerdeValue")),
                "model_ref": _nullable({"type": "string"}),
                "engine": _nullable(_shared_ref("SerdeValue")),
                "ops": _shared_ref("StepFnTuple"),
                "columns": {"anyOf": [_shared_ref("StepFnTuple"), _shared_ref("SerdeObject")]},
                "schemas": _shared_ref("StepFnTuple"),
                "hooks": _shared_ref("StepFnTuple"),
                "security_deps": _shared_ref("StepFnTuple"),
                "deps": _shared_ref("StepFnTuple"),
                "portability_class": _nullable({"type": "string"}),
                "interoperable_with": _shared_ref("StringTuple"),
                "roundtrip_mode": {"type": "string"},
                "response": _nullable(_spec_or_envelope("ResponseSpec")),
            },
        ),
    )

    schemas["RouterSpec"] = _root_schema(
        "RouterSpec",
        "tigrbl_core._spec.router_spec:RouterSpec",
        _object_schema(
            "RouterSpec",
            {
                "name": {"type": "string"},
                "prefix": {"type": "string"},
                "engine": _nullable(_shared_ref("SerdeValue")),
                "tags": _shared_ref("StringTuple"),
                "ops": _shared_ref("StepFnTuple"),
                "schemas": _shared_ref("StepFnTuple"),
                "hooks": _shared_ref("StepFnTuple"),
                "security_deps": _shared_ref("StepFnTuple"),
                "deps": _shared_ref("StepFnTuple"),
                "response": _nullable(_spec_or_envelope("ResponseSpec")),
                "tables": _shared_ref("StepFnTuple"),
            },
        ),
    )

    schemas["AppSpec"] = _root_schema(
        "AppSpec",
        "tigrbl_core._spec.app_spec:AppSpec",
        _object_schema(
            "AppSpec",
            {
                "title": {"type": "string"},
                "description": _nullable({"type": "string"}),
                "version": {"type": "string"},
                "execution_backend": {"type": "string"},
                "engine": _nullable(_shared_ref("SerdeValue")),
                "routers": _shared_ref("StepFnTuple"),
                "ops": _shared_ref("StepFnTuple"),
                "tables": _shared_ref("StepFnTuple"),
                "schemas": _shared_ref("StepFnTuple"),
                "hooks": _shared_ref("StepFnTuple"),
                "security_deps": _shared_ref("StepFnTuple"),
                "deps": _shared_ref("StepFnTuple"),
                "response": _nullable(_spec_or_envelope("ResponseSpec")),
                "jsonrpc_prefix": {"type": "string"},
                "system_prefix": {"type": "string"},
                "middlewares": _shared_ref("StepFnTuple"),
                "lifespan": _nullable(_shared_ref("SerdeValue")),
            },
        ),
    )

    schemas["SessionSpec"] = _root_schema(
        "SessionSpec",
        "tigrbl_core._spec.session_spec:SessionSpec",
        _object_schema(
            "SessionSpec",
            {
                "isolation": _nullable({"type": "string"}),
                "read_only": _nullable({"type": "boolean"}),
                "autobegin": _nullable({"type": "boolean"}),
                "expire_on_commit": _nullable({"type": "boolean"}),
                "retry_on_conflict": _nullable({"type": "boolean"}),
                "max_retries": {"type": "integer"},
                "backoff_ms": {"type": "integer"},
                "backoff_jitter": {"type": "boolean"},
                "statement_timeout_ms": _nullable({"type": "integer"}),
                "lock_timeout_ms": _nullable({"type": "integer"}),
                "fetch_rows": _nullable({"type": "integer"}),
                "stream_chunk_rows": _nullable({"type": "integer"}),
                "min_lsn": _nullable({"type": "string"}),
                "as_of_ts": _nullable({"type": "string"}),
                "consistency": _nullable({"type": "string"}),
                "staleness_ms": _nullable({"type": "integer"}),
                "tenant_id": _nullable({"type": "string"}),
                "role": _nullable({"type": "string"}),
                "rls_context": _nullable(_shared_ref("StringMap")),
                "trace_id": _nullable({"type": "string"}),
                "query_tag": _nullable({"type": "string"}),
                "tag": _nullable({"type": "string"}),
                "tracing_sample": _nullable({"type": "number"}),
                "cache_read": _nullable({"type": "boolean"}),
                "cache_write": _nullable({"type": "boolean"}),
                "namespace": _nullable({"type": "string"}),
                "kms_key_alias": _nullable({"type": "string"}),
                "classification": _nullable({"type": "string"}),
                "audit": _nullable({"type": "boolean"}),
                "idempotency_key": _nullable({"type": "string"}),
                "page_snapshot": _nullable({"type": "string"}),
            },
        ),
    )

    schemas["TableRegistrySpec"] = _root_schema(
        "TableRegistrySpec",
        "tigrbl_core._spec.table_registry_spec:TableRegistrySpec",
        _object_schema(
            "TableRegistrySpec",
            {
                "tables": _shared_ref("StepFnTuple"),
            },
        ),
    )

    return schemas


def build_spec_json_schema_bundle() -> dict[str, Any]:
    return {
        "$schema": JSON_SCHEMA_DRAFT_2020_12,
        "title": "Tigrbl Core Spec Schema Manifest",
        "shared": SHARED_SCHEMA_NAME,
        "schemas": {name: f"{name}.json" for name in INDIVIDUAL_SPEC_NAMES},
    }


__all__ = [
    "INDIVIDUAL_SPEC_NAMES",
    "JSON_SCHEMA_DRAFT_2020_12",
    "SHARED_SCHEMA_NAME",
    "build_individual_spec_json_schemas",
    "build_shared_json_schema",
    "build_spec_json_schema_bundle",
]
