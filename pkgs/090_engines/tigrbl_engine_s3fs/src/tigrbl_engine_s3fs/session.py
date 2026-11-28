from __future__ import annotations

from typing import Any, Iterable

from tigrbl_base._base import EngineSessionBase
from tigrbl_core._spec.engine_session_spec import EngineSessionSpec

from .engine import S3FSEngine


def _as_bytes(data: bytes | bytearray | memoryview) -> bytes:
    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise TypeError("object data must be bytes-like")
    return bytes(data)


class S3FSSession(EngineSessionBase):
    def __init__(
        self, engine: S3FSEngine, spec: EngineSessionSpec | None = None
    ) -> None:
        super().__init__(spec)
        self.engine = engine
        self._closed = False
        self._puts: dict[str, bytes] = {}
        self._deletes: set[str] = set()

    def put_object(self, key: str, data: bytes | bytearray | memoryview) -> str:
        self._require_write()
        path = self.engine.object_path(key)
        self._put_path(path, _as_bytes(data))
        return key

    def get_object(self, key: str) -> bytes:
        return self._get_path(self.engine.object_path(key))

    def delete_object(self, key: str) -> bool:
        self._require_write()
        path = self.engine.object_path(key)
        existed = self._path_exists(path)
        self._delete_path(path)
        return existed

    def object_exists(self, key: str) -> bool:
        return self._path_exists(self.engine.object_path(key))

    def head_object(self, key: str) -> dict[str, Any]:
        path = self.engine.object_path(key)
        if path in self._puts:
            return {"name": path, "size": len(self._puts[path]), "staged": True}
        if path in self._deletes:
            raise FileNotFoundError(key)
        return self.engine.head_path(path)

    def list_objects(self, prefix: str = "") -> list[str]:
        keys = set(self.engine.list_paths(prefix))
        base = "/".join(
            part for part in (self.engine.bucket, self.engine.prefix) if part
        )
        marker = f"{base}/"
        for path in self._puts:
            if path.startswith(marker):
                keys.add(path[len(marker) :])
        for path in self._deletes:
            if path.startswith(marker):
                keys.discard(path[len(marker) :])
        if prefix:
            keys = {key for key in keys if key.startswith(prefix.strip("/"))}
        return sorted(keys)

    def put_cas(self, data: bytes | bytearray | memoryview) -> str:
        self._require_write()
        payload = _as_bytes(data)
        address = self.engine.cas_address(payload)
        path = self.engine.cas_path(address)
        if not self._path_exists(path):
            self._put_path(path, payload)
        return address

    def get_cas(self, address: str) -> bytes:
        payload = self._get_path(self.engine.cas_path(address))
        self.engine.verify_cas_payload(address, payload)
        return payload

    def cas_exists(self, address: str) -> bool:
        return self._path_exists(self.engine.cas_path(address))

    async def _tx_begin_impl(self) -> None:
        self._require_open_session()

    async def _tx_commit_impl(self) -> None:
        for path, data in self._puts.items():
            self.engine.put_path(path, data)
        for path in self._deletes:
            self.engine.delete_path(path)
        self._puts.clear()
        self._deletes.clear()

    async def _tx_rollback_impl(self) -> None:
        self._puts.clear()
        self._deletes.clear()

    async def _close_impl(self) -> None:
        self._puts.clear()
        self._deletes.clear()
        self._closed = True

    def _put_path(self, path: str, data: bytes) -> None:
        if self.in_transaction():
            self._puts[path] = data
            self._deletes.discard(path)
        else:
            self.engine.put_path(path, data)

    def _get_path(self, path: str) -> bytes:
        self._require_open_session()
        if path in self._deletes:
            raise FileNotFoundError(path)
        if path in self._puts:
            return self._puts[path]
        return self.engine.get_path(path)

    def _delete_path(self, path: str) -> None:
        if self.in_transaction():
            self._puts.pop(path, None)
            self._deletes.add(path)
        else:
            self.engine.delete_path(path)

    def _path_exists(self, path: str) -> bool:
        self._require_open_session()
        if path in self._deletes:
            return False
        if path in self._puts:
            return True
        return self.engine.path_exists(path)

    def _require_write(self) -> None:
        self._require_open_session()
        if self.read_only:
            raise RuntimeError("write attempted in read-only engine session")
        self._dirty = True

    def _require_open_session(self) -> None:
        if self._closed:
            raise RuntimeError("session is closed")

    def _add_impl(self, obj: Any) -> Any:
        raise TypeError("s3fs object sessions do not support ORM add()")

    async def _delete_impl(self, obj: Any) -> None:
        raise TypeError("s3fs object sessions do not support ORM delete()")

    async def _get_impl(self, model: type, ident: Any) -> Any | None:
        raise TypeError("use get_object() for s3fs object sessions")

    async def _execute_impl(self, stmt: Any) -> Any:
        raise TypeError("s3fs object sessions do not execute SQL statements")

    async def _executeloop_impl(self, statements: Iterable[Any]) -> Any:
        raise TypeError("s3fs object sessions do not execute SQL statements")

    async def _executemany_impl(self, stmt: Any, parameter_sets: Any) -> Any:
        raise TypeError("s3fs object sessions do not execute SQL statements")
