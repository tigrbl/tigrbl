from __future__ import annotations

from io import BytesIO
from typing import Any

import pytest

from tigrbl_core._spec.engine_session_spec import EngineSessionSpec
from tigrbl import EngineSpec
from tigrbl_base._base import EngineBase
from tigrbl_engine_s3 import register, s3_capabilities, s3_engine


class FakeS3Client:
    def __init__(self) -> None:
        self.objects: dict[tuple[str, str], bytes] = {}
        self.put_calls: list[dict[str, Any]] = []

    def put_object(self, **kwargs: Any) -> dict[str, str]:
        self.put_calls.append(kwargs)
        self.objects[(kwargs["Bucket"], kwargs["Key"])] = bytes(kwargs["Body"])
        return {"ETag": "fake"}

    def get_object(self, *, Bucket: str, Key: str) -> dict[str, Any]:
        return {"Body": BytesIO(self.objects[(Bucket, Key)])}

    def delete_object(self, *, Bucket: str, Key: str) -> dict[str, Any]:
        self.objects.pop((Bucket, Key), None)
        return {}

    def head_object(self, *, Bucket: str, Key: str) -> dict[str, Any]:
        payload = self.objects[(Bucket, Key)]
        return {"ContentLength": len(payload), "ETag": "fake"}

    def list_objects_v2(self, **kwargs: Any) -> dict[str, Any]:
        bucket = kwargs["Bucket"]
        prefix = kwargs.get("Prefix", "")
        return {
            "Contents": [
                {"Key": key}
                for (known_bucket, key), _ in sorted(self.objects.items())
                if known_bucket == bucket and key.startswith(prefix)
            ],
            "IsTruncated": False,
        }


def make_engine(*, cas: bool = True):
    client = FakeS3Client()
    engine, make_session = s3_engine(
        mapping={
            "bucket": "assets",
            "prefix": "tenant-a",
            "cas": cas,
            "client": client,
            "put_options": {"ServerSideEncryption": "AES256"},
        }
    )
    return client, engine, make_session


def test_object_crud_listing_options_and_capabilities() -> None:
    client, engine, make_session = make_engine()
    session = make_session()

    assert session.put_object("docs/readme.txt", b"hello") == "docs/readme.txt"
    assert session.get_object("docs/readme.txt") == b"hello"
    assert session.object_exists("docs/readme.txt")
    assert session.head_object("docs/readme.txt")["ContentLength"] == 5
    assert session.list_objects("docs") == ["docs/readme.txt"]
    assert engine.object_key("docs/readme.txt") == "tenant-a/docs/readme.txt"
    assert client.put_calls[0]["ServerSideEncryption"] == "AES256"
    assert session.delete_object("docs/readme.txt")
    assert not session.object_exists("docs/readme.txt")
    assert s3_capabilities()["direct_s3_api"] is True


def test_registered_engine_builds_from_engine_spec() -> None:
    client = FakeS3Client()
    register()
    engine, make_session = EngineSpec.from_any(
        {"kind": "s3", "bucket": "assets", "client": client, "cas": True}
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
    client, engine, make_session = make_engine()
    session = make_session()

    address = session.put_cas(b"same payload")
    assert address == session.put_cas(b"same payload")
    assert len(client.put_calls) == 1
    assert session.cas_exists(address)
    assert session.get_cas(address) == b"same payload"

    client.objects[(engine.bucket, engine.cas_key(address))] = b"corrupt"
    with pytest.raises(ValueError, match="integrity check failed"):
        session.get_cas(address)


@pytest.mark.asyncio
async def test_transaction_stages_commit_and_rollback() -> None:
    client, _, make_session = make_engine()
    session = make_session()
    await session.begin()
    session.put_object("pending.bin", b"pending")
    assert session.get_object("pending.bin") == b"pending"
    assert client.objects == {}
    await session.rollback()
    assert not session.object_exists("pending.bin")

    await session.begin()
    session.put_object("committed.bin", b"committed")
    await session.commit()
    assert any(key.endswith("committed.bin") for _, key in client.objects)


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
            engine.object_key(key)

    session = make_session()
    await session.close()
    with pytest.raises(RuntimeError, match="closed"):
        session.object_exists("anything")
