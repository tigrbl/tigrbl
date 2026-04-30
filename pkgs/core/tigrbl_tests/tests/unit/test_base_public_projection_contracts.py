from __future__ import annotations

import tigrbl
from tigrbl import (
    AppBase,
    EngineBase,
    EngineProviderBase,
    EngineRegistry,
    ForeignKeyBase,
    RouterBase,
    TableBase,
    TableRegistryBase,
)
from tigrbl_base._base import AppBase as BaseAppBase
from tigrbl_base._base import EngineBase as BaseEngineBase
from tigrbl_base._base import EngineProviderBase as BaseEngineProviderBase
from tigrbl_base._base import ForeignKeyBase as BaseForeignKeyBase
from tigrbl_base._base import RouterBase as BaseRouterBase
from tigrbl_base._base import TableBase as BaseTableBase
from tigrbl_base._base import TableRegistryBase as BaseTableRegistryBase
from tigrbl_core._spec import EngineRegistry as CoreEngineRegistry


def test_requested_base_public_projection_symbols_are_exposed() -> None:
    expected = {
        "AppBase": (AppBase, BaseAppBase),
        "ForeignKeyBase": (ForeignKeyBase, BaseForeignKeyBase),
        "RouterBase": (RouterBase, BaseRouterBase),
        "TableBase": (TableBase, BaseTableBase),
        "TableRegistryBase": (TableRegistryBase, BaseTableRegistryBase),
        "EngineBase": (EngineBase, BaseEngineBase),
        "EngineProviderBase": (EngineProviderBase, BaseEngineProviderBase),
        "EngineRegistry": (EngineRegistry, CoreEngineRegistry),
    }

    for symbol, (projected, owner) in expected.items():
        assert symbol in tigrbl.__all__
        assert getattr(tigrbl, symbol) is projected
        assert projected is owner


def test_non_projected_base_symbols_remain_out_of_public_facade() -> None:
    for symbol in (
        "AliasBase",
        "BindingBase",
        "BindingRegistryBase",
        "ColumnBase",
        "RequestBase",
        "SchemaBase",
        "SessionABC",
        "StorageTransformBase",
        "TigrblSessionBase",
    ):
        assert symbol not in tigrbl.__all__
        assert not hasattr(tigrbl, symbol)
