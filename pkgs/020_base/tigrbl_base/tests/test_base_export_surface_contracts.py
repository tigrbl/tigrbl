from __future__ import annotations

from importlib import import_module, reload
import sys

import pytest


_BASE_EXPORT_CASES = [
    ("AliasBase", "tigrbl_base._base._alias_base"),
    ("AppBase", "tigrbl_base._base._app_base"),
    ("BindingBase", "tigrbl_base._base._binding_base"),
    ("BindingRegistryBase", "tigrbl_base._base._binding_base"),
    ("ColumnBase", "tigrbl_base._base._column_base"),
    ("EngineBase", "tigrbl_base._base._engine_base"),
    ("EngineProviderBase", "tigrbl_base._base._engine_provider_base"),
    ("ForeignKeyBase", "tigrbl_base._base._storage"),
    ("HeaderCookiesBase", "tigrbl_base._base._headers_base"),
    ("HeadersBase", "tigrbl_base._base._headers_base"),
    ("RequestBase", "tigrbl_base._base._request_base"),
    ("RouterBase", "tigrbl_base._base._router_base"),
    ("SchemaBase", "tigrbl_base._base._schema_base"),
    ("StorageTransformBase", "tigrbl_base._base._storage"),
    ("TableBase", "tigrbl_base._base._table_base"),
    ("TableRegistryBase", "tigrbl_base._base._table_registry_base"),
    ("EngineSessionBase", "tigrbl_base._base._engine_session_base"),
]


@pytest.mark.parametrize(("symbol", "module_name"), _BASE_EXPORT_CASES)
def test_base_exports_include_requested_symbols(symbol: str, module_name: str) -> None:
    base = import_module("tigrbl_base._base")

    assert symbol in base._EXPORTS
    assert symbol in base.__all__
    assert base._EXPORTS[symbol] == module_name.removeprefix("tigrbl_base._base.")


@pytest.mark.parametrize(("symbol", "module_name"), _BASE_EXPORT_CASES)
def test_base_exports_lazy_load_requested_symbols(symbol: str, module_name: str) -> None:
    base = reload(import_module("tigrbl_base._base"))
    sys.modules.pop(module_name, None)
    base.__dict__.pop(symbol, None)

    assert module_name not in sys.modules

    exported = getattr(base, symbol)

    assert module_name in sys.modules
    assert exported is getattr(sys.modules[module_name], symbol)
    assert base.__dict__[symbol] is exported


def test_base_exports_unknown_symbol_fails_closed() -> None:
    base = import_module("tigrbl_base._base")

    with pytest.raises(AttributeError):
        getattr(base, "MissingBase")


def test_base_exports_mapping_targets_existing_symbols() -> None:
    base = import_module("tigrbl_base._base")

    for symbol, relative_module in base._EXPORTS.items():
        module = import_module(f"tigrbl_base._base.{relative_module}")
        assert getattr(module, symbol) is getattr(base, symbol)
