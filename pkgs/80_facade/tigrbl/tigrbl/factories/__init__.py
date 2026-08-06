from __future__ import annotations

from importlib import import_module

_MODULES = (
    "app",
    "column",
    "engine",
    "hook",
    "op",
    "responses",
    "router",
    "schema",
    "table",
)

_EXPORT_MODULE = {
    "Column": "column",
    "ColumnSpec": "column",
    "F": "column",
    "IO": "column",
    "S": "column",
    "acol": "column",
    "activateTableSpec": "table",
    "activateTableSpecs": "table",
    "as_event_stream": "responses",
    "as_file": "responses",
    "as_html": "responses",
    "as_json": "responses",
    "as_redirect": "responses",
    "as_stream": "responses",
    "as_text": "responses",
    "defineAppSpec": "app",
    "defineRouterSpec": "router",
    "defineTableSpec": "table",
    "deriveApp": "app",
    "deriveRouter": "router",
    "deriveTable": "table",
    "deriveTableSpec": "table",
    "engine": "engine",
    "engine_spec": "engine",
    "hook": "hook",
    "hook_spec": "hook",
    "make": "op",
    "makeColumn": "column",
    "makeVirtualColumn": "column",
    "mariadb": "engine",
    "mariadb_cfg": "engine",
    "mem": "engine",
    "mysql": "engine",
    "mysql_cfg": "engine",
    "op": "op",
    "pg": "engine",
    "pg_cfg": "engine",
    "pga": "engine",
    "pgs": "engine",
    "prov": "engine",
    "provider_mariadb": "engine",
    "provider_mysql": "engine",
    "provider_postgres": "engine",
    "provider_sqlite_file": "engine",
    "provider_sqlite_memory": "engine",
    "provideTableSpec": "table",
    "schema": "schema",
    "schema_spec": "schema",
    "sqlite_cfg": "engine",
    "sqlitef": "engine",
    "vcol": "column",
}

__all__ = sorted((*_MODULES, *_EXPORT_MODULE))


def __getattr__(name: str):
    module_name = name if name in _MODULES else _EXPORT_MODULE.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = import_module(f"{__name__}.{module_name}")
    value = module if name in _MODULES else getattr(module, name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(__all__) | {key for key in globals() if not key.startswith("_")})
