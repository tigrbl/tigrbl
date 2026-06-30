from __future__ import annotations

import shutil
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from tigrbl import TigrblApp, build_schemas, get_schema
from tigrbl._spec import OpSpec
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import TableBase
from tigrbl.types import Column, String
from tigrbl_concrete.system.static import _mount_static


def _workspace_tmp_dir():
    root = Path.cwd() / ".tmp" / "t2-static-tests" / uuid4().hex
    root.mkdir(parents=True, exist_ok=False)
    return root


class SchemaWidget(TableBase, GUIDPk):
    __tablename__ = "static_schema_t2_widgets"
    name = Column(String, nullable=False)


def test_get_schema_is_deterministic_and_fails_closed_for_bad_context() -> None:
    spec = OpSpec(alias="create", target="create")
    build_schemas(SchemaWidget, [spec])

    assert get_schema(SchemaWidget, "create", kind="in") is get_schema(
        SchemaWidget, "create", kind="IN"
    )
    with pytest.raises(KeyError):
        get_schema(SchemaWidget, "missing")
    with pytest.raises(ValueError):
        get_schema(SchemaWidget, "create", kind="sideways")


def test_mount_static_rejects_non_absolute_reserved_and_missing_directories() -> None:
    router = SimpleNamespace()
    tmp_path = _workspace_tmp_dir()
    assets = tmp_path / "assets"
    try:
        assets.mkdir()

        with pytest.raises(ValueError, match="absolute"):
            _mount_static(router, directory=assets, path="assets")
        with pytest.raises(ValueError, match="reserved"):
            _mount_static(router, directory=assets, path="/rpc")
        with pytest.raises(ValueError, match="directory"):
            _mount_static(router, directory=tmp_path / "missing", path="/assets")
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)


@pytest.mark.asyncio
async def test_static_mount_serves_file_without_shadowing_reserved_paths() -> None:
    tmp_path = _workspace_tmp_dir()
    assets = tmp_path / "assets"
    try:
        assets.mkdir()
        (assets / "hello.txt").write_text("hello", encoding="utf-8")
        app = TigrblApp()
        app.mount_static(directory=assets, path="/assets")

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get("/assets/hello.txt")

        assert response.status_code == 200
        assert response.text == "hello"
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)
