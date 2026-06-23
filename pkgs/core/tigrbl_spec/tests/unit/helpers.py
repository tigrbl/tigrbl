from __future__ import annotations

from tigrbl_spec import with_identity


def app_payload() -> dict[str, object]:
    return with_identity(
        "AppSpec",
        {
            "title": "Tigrbl",
            "description": None,
            "version": "0.1.0",
            "execution_backend": "auto",
            "engine": None,
            "routers": {"__tuple__": []},
            "ops": {"__tuple__": []},
            "tables": {"__tuple__": []},
            "schemas": {"__tuple__": []},
            "hooks": {"__tuple__": []},
            "security_deps": {"__tuple__": []},
            "deps": {"__tuple__": []},
            "response": None,
            "jsonrpc_prefix": "/rpc",
            "system_prefix": "/system",
            "middlewares": {"__tuple__": []},
            "lifespan": None,
        },
    )


def http_rest_binding_payload() -> dict[str, object]:
    return with_identity(
        "HttpRestBindingSpec",
        {
            "proto": "http.rest",
            "methods": {"__tuple__": ["GET"]},
            "path": "/widgets",
            "exchange": "request_response",
            "framing": "json",
        },
    )


def binding_payload() -> dict[str, object]:
    return with_identity(
        "BindingSpec",
        {
            "name": "list_widgets",
            "spec": http_rest_binding_payload(),
        },
    )


def column_payload() -> dict[str, object]:
    return with_identity(
        "ColumnSpec",
        {
            "storage": None,
            "field": None,
            "io": None,
            "datatype": None,
            "default_factory": None,
            "read_producer": None,
        },
    )


def engine_payload() -> dict[str, object]:
    return with_identity(
        "EngineSpec",
        {
            "kind": "sqlite",
            "async_": False,
            "dsn": None,
            "mapping": None,
            "path": ":memory:",
            "memory": True,
            "pool": None,
            "user": None,
            "pwd": None,
            "host": None,
            "port": None,
            "name": "default",
            "pool_size": 5,
            "max": 10,
        },
    )


def headers_payload() -> dict[str, object]:
    return with_identity(
        "HeadersSpec",
        {
            "values": {
                "content-type": "application/json",
                "x-trace": "abc",
            },
            "required": {"__tuple__": ["content-type"]},
            "expose": {"__tuple__": ["x-trace"]},
        },
    )


def op_payload() -> dict[str, object]:
    return with_identity(
        "OpSpec",
        {
            "alias": "list",
            "target": "widgets",
            "table": None,
            "expose_routes": True,
            "expose_rpc": True,
            "expose_method": True,
            "bindings": {"__tuple__": [http_rest_binding_payload()]},
            "exchange": "request_response",
            "tx_scope": "read",
            "subevents": {"__tuple__": []},
            "engine": None,
            "arity": "collection",
            "http_methods": {"__tuple__": ["GET"]},
            "path_suffix": None,
            "tags": {"__tuple__": []},
            "status_code": 200,
            "response": None,
            "persist": "none",
            "request_model": None,
            "response_model": None,
            "returns": "raw",
            "handler": None,
            "hooks": {"__tuple__": []},
            "core": None,
            "core_raw": None,
            "extra": {},
            "deps": {"__tuple__": []},
            "security_deps": {"__tuple__": []},
            "secdeps": {"__tuple__": []},
        },
    )


def session_payload() -> dict[str, object]:
    return with_identity(
        "SessionSpec",
        {
            "isolation": None,
            "read_only": None,
            "autobegin": None,
            "expire_on_commit": None,
            "retry_on_conflict": None,
            "max_retries": 0,
            "backoff_ms": 0,
            "backoff_jitter": False,
            "statement_timeout_ms": None,
            "lock_timeout_ms": None,
            "fetch_rows": None,
            "stream_chunk_rows": None,
            "min_lsn": None,
            "as_of_ts": None,
            "consistency": None,
            "staleness_ms": None,
            "tenant_id": None,
            "role": None,
            "rls_context": None,
            "trace_id": None,
            "query_tag": None,
            "tag": None,
            "tracing_sample": None,
            "cache_read": None,
            "cache_write": None,
            "namespace": None,
            "kms_key_alias": None,
            "classification": None,
            "audit": None,
            "idempotency_key": None,
            "page_snapshot": None,
        },
    )


def representative_payloads() -> dict[str, dict[str, object]]:
    return {
        "AppSpec": app_payload(),
        "OpSpec": op_payload(),
        "BindingSpec": binding_payload(),
        "ColumnSpec": column_payload(),
        "EngineSpec": engine_payload(),
        "HeadersSpec": headers_payload(),
        "SessionSpec": session_payload(),
    }
