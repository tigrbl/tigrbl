from __future__ import annotations

from sqlalchemy import Column, Integer, String

import tigrbl
from tigrbl import TableBase, TigrblApp, TigrblRouter, include_tables
from tigrbl.factories.engine import mem


class IncludeTablesAlpha(TableBase):
    __tablename__ = "include_tables_alpha_contract"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class IncludeTablesBeta(TableBase):
    __tablename__ = "include_tables_beta_contract"

    id = Column(Integer, primary_key=True)
    label = Column(String, nullable=False)


def test_public_include_tables_helper_bulk_binds_namespaces_without_host_mount() -> None:
    router = TigrblRouter(engine=mem(async_=False))
    app = TigrblApp(engine=mem(async_=False), mount_system=False)

    included = include_tables(
        router,
        [IncludeTablesAlpha, IncludeTablesBeta],
        app=app,
        base_prefix="/v1",
        mount_router=False,
    )

    assert tigrbl.include_tables is include_tables
    assert set(included) == {"IncludeTablesAlpha", "IncludeTablesBeta"}
    assert set(router.tables) == {"IncludeTablesAlpha", "IncludeTablesBeta"}

    for table_name in ("IncludeTablesAlpha", "IncludeTablesBeta"):
        assert hasattr(router.schemas, table_name)
        assert hasattr(router.handlers, table_name)
        assert hasattr(router.hooks, table_name)
        assert hasattr(router.rpc, table_name)
        assert hasattr(router.rest, table_name)
        assert hasattr(router.core, table_name)
        assert table_name in router.routers
        assert table_name in router.columns
        assert table_name in router.table_config

    assert all(model_router is not None for model_router in included.values())
    assert any(str(route.path).startswith("/v1/") for route in router.routes)
    assert not any(str(route.path).startswith("/v1/") for route in app.routes)


def test_public_include_tables_helper_mounts_each_table_under_base_prefix() -> None:
    router = TigrblRouter(engine=mem(async_=False))
    app = TigrblApp(engine=mem(async_=False), mount_system=False)

    include_tables(
        router,
        [IncludeTablesAlpha, IncludeTablesBeta],
        app=app,
        base_prefix="/v1",
    )

    mounted_paths = sorted(str(route.path) for route in router.routes)
    host_paths = sorted(
        str(route.path)
        for route in app.routes
        if str(route.path).startswith("/v1/")
    )

    assert any(path.startswith("/v1/") for path in mounted_paths)
    assert host_paths == mounted_paths
