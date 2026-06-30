from __future__ import annotations

import importlib

import pytest

import tigrbl
from tigrbl import TigrblApp, TigrblRouter
from tigrbl._spec import AppSpec
from tigrbl_concrete._concrete import TigrblApp as ConcreteTigrblApp
from tigrbl_concrete._concrete import TigrblRouter as ConcreteTigrblRouter
from tigrbl_concrete._mapping.model import bind, rebind
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import TableBase
from tigrbl.types import Column, String


class Widget(TableBase, GUIDPk):
    __tablename__ = "facade_t2_widgets"
    name = Column(String, nullable=False)


def test_public_and_concrete_facade_import_identity_is_reload_stable() -> None:
    concrete = importlib.reload(importlib.import_module("tigrbl_concrete._concrete"))
    public = importlib.reload(tigrbl)

    assert public.TigrblApp is concrete.TigrblApp
    assert public.TigrblRouter is concrete.TigrblRouter
    assert ConcreteTigrblApp is concrete.TigrblApp
    assert ConcreteTigrblRouter is concrete.TigrblRouter


def test_tigrblapp_from_spec_preserves_prefixes_and_spec_identity() -> None:
    spec = AppSpec(title="Facade T2", version="2.0", jsonrpc_prefix="/rpc2")

    app = TigrblApp.from_spec(spec)

    assert app.title == "Facade T2"
    assert app.version == "2.0"
    assert app.jsonrpc_prefix == "/rpc2"
    assert app._tigrbl_app_spec.title == "Facade T2"


def test_tigrblrouter_prefix_normalization_and_mount_rejection() -> None:
    router = TigrblRouter(prefix="api")

    assert router.prefix == "/api"
    with pytest.raises(TypeError, match="transport entrypoint"):
        router({}, None, None)


def test_bind_and_rebind_are_idempotent_for_model_surface() -> None:
    first = bind(Widget)
    second = bind(Widget)
    rebound = rebind(Widget)

    assert tuple(first) == tuple(second)
    assert tuple(rebound)
    assert hasattr(Widget, "schemas")
    assert hasattr(Widget, "ops")
