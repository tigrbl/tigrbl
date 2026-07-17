from __future__ import annotations

from io import BytesIO
from typing import Any

import pytest

from tigrbl_core._spec.engine_session_spec import EngineSessionSpec
from tigrbl import EngineSpec
from tigrbl_base._base import EngineBase
from tigrbl_engine_s3fs import register, s3fs_capabilities, s3fs_engine


class _Writer(BytesIO):
    def __init__(self, fs: "FakeS3FS", path: str) -> None:
        super().__init__()
        self.fs = fs
        self.path = path

    def __enter__(self) -> "_Writer":
        return self

    def __exit__(self, *_: Any) -> None:
        self.fs.objects[self.path] = self.getvalue()
        self.close()


class FakeS3FS:
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}
        self.write_count = 0

    def makedirs(self, path: str, exist_ok: bool = False) -> None:
        del path, exist_ok

    def open(self, path: str, mode: str):
        if mode == "wb":
            self.write_count += 1
            return _Writer(self, path)
        if path not in self.objects:
            raise FileNotFoundError(path)
        return BytesIO(self.objects[path])

    def exists(self, path: str) -> bool:
        return path in self.objects

    def rm(self, path: str) -> None:
        self.objects.pop(path, None)

    def info(self, path: str) -> dict[str, Any]:
        if path not in self.objects:
            raise FileNotFoundError(path)
        return {"name": path, "size": len(self.objects[path])}

    def find(self, path: str, detail: bool = False) -> list[str]:
        del detail
        return sorted(key for key in self.objects if key.startswith(path))


def make_engine(*, cas: bool = True):
    fs = FakeS3FS()
    engine, make_session = s3fs_engine(
        mapping={"bucket": "assets", "prefix": "tenant-a", "cas": cas, "fs": fs}
    )
    return fs, engine, make_session


def test_object_crud_listing_and_capabilities() -> None:
    fs, engine, make_session = make_engine()
    session = make_session()

    assert session.put_object("docs/readme.txt", b"hello") == "docs/readme.txt"
    assert session.get_object("docs/readme.txt") == b"hello"
    assert session.object_exists("docs/readme.txt")
    assert session.head_object("docs/readme.txt")["size"] == 5
    assert session.list_objects("docs") == ["docs/readme.txt"]
    assert engine.object_path("docs/readme.txt") == "assets/tenant-a/docs/readme.txt"
    assert session.delete_object("docs/readme.txt")
    assert not session.object_exists("docs/readme.txt")
    assert s3fs_capabilities()["transactional"] is False
    assert fs.write_count == 1


def test_registered_engine_builds_from_engine_spec() -> None:
    fs = FakeS3FS()
    register()
    engine, make_session = EngineSpec.from_any(
        {"kind": "s3fs", "bucket": "assets", "fs": fs, "cas": True}
    ).build()
    assert isinstance(engine, EngineBase)
    assert engine.to_provider() is engine
    assert engine.spec is not None
    assert engine.bucket == "assets"
    assert make_session().put_cas(b"payload").startswith("sha256:")


@pytest.mark.asyncio
async def test_engine_base_batch_surface_fails_closed() -> None:
    _, engine, _ = make_engine()
    with pytest.raises(TypeError, match="do not execute SQL"):
        await engine.executeloop([])
    with pytest.raises(TypeError, match="do not execute SQL"):
        await engine.executemany("INSERT", [])


def test_cas_is_deterministic_deduplicated_and_verified() -> None:
    fs, engine, make_session = make_engine()
    session = make_session()

    address = session.put_cas(b"same payload")
    assert address == session.put_cas(b"same payload")
    assert fs.write_count == 1
    assert session.cas_exists(address)
    assert session.get_cas(address) == b"same payload"

    fs.objects[engine.cas_path(address)] = b"corrupt"
    with pytest.raises(ValueError, match="integrity check failed"):
        session.get_cas(address)


@pytest.mark.asyncio
async def test_transaction_stages_commit_and_rollback() -> None:
    fs, _, make_session = make_engine()
    session = make_session()
    await session.begin()
    session.put_object("pending.bin", b"pending")
    assert session.get_object("pending.bin") == b"pending"
    assert fs.objects == {}
    await session.rollback()
    assert not session.object_exists("pending.bin")

    await session.begin()
    session.put_object("committed.bin", b"committed")
    await session.commit()
    assert any(path.endswith("committed.bin") for path in fs.objects)


@pytest.mark.asyncio
async def test_read_only_invalid_keys_disabled_cas_and_closed_session() -> None:
    _, engine, make_session = make_engine(cas=False)
    readonly_session = make_session(EngineSessionSpec(read_only=True))
    with pytest.raises(RuntimeError, match="read-only"):
        readonly_session.put_object("blocked", b"data")
    with pytest.raises(RuntimeError, match="not enabled"):
        engine.cas_address(b"data")
    for key in ("/absolute", "a//b", "../escape", "a/../escape", r"a\b"):
        with pytest.raises(ValueError):
            engine.object_path(key)

    session = make_session()
    await session.close()
    with pytest.raises(RuntimeError, match="closed"):
        session.object_exists("anything")
