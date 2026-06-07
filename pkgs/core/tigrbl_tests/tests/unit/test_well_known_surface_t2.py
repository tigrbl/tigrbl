from __future__ import annotations

import importlib

import pytest

import tigrbl


PUBLIC_CONSTANTS = ("DEFAULT_HTTP_METHODS", "HOOK_DECLS_ATTR")
PUBLIC_DECORATORS = (
    "alias_ctx",
    "engine_ctx",
    "hook_ctx",
    "op_ctx",
    "response_ctx",
    "schema_ctx",
)
PUBLIC_IMPERATIVE_HELPERS = (
    "bind",
    "rebind",
    "build_schemas",
    "build_hooks",
    "build_handlers",
    "include_table",
    "include_tables",
    "get_schema",
)


def test_well_known_constants_are_public_and_stable() -> None:
    reloaded = importlib.reload(tigrbl)

    for symbol in PUBLIC_CONSTANTS:
        assert symbol in reloaded.__all__
        assert getattr(reloaded, symbol) is getattr(tigrbl, symbol)


@pytest.mark.parametrize("symbol", PUBLIC_DECORATORS)
def test_well_known_decorators_attach_metadata_or_reject_bad_use(symbol: str) -> None:
    decorator = getattr(tigrbl, symbol)
    assert symbol in tigrbl.__all__
    assert callable(decorator)


@pytest.mark.parametrize("symbol", PUBLIC_IMPERATIVE_HELPERS)
def test_well_known_imperative_helpers_are_public_callables(symbol: str) -> None:
    helper = getattr(tigrbl, symbol)

    assert symbol in tigrbl.__all__
    assert callable(helper)


def test_well_known_surface_does_not_expose_unowned_internals() -> None:
    for symbol in ("ColumnBase", "AliasBase", "BindingBase", "StorageTransformBase"):
        assert symbol not in tigrbl.__all__
