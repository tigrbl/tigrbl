from __future__ import annotations

from typing import Any, Iterable

from tigrbl_base._base import EngineSessionBase
from tigrbl_core._spec.engine_session_spec import EngineSessionSpec

from .engine import S3Engine


def _as_bytes(data: bytes | bytearray | memoryview) -> bytes:
    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise TypeError("object data must be bytes-like")
    return bytes(data)


class S3Session(EngineSessionBase):
    def __init__(self, engine: S3Engine, spec: EngineSessionSpec | None = None) -> None:
        super().__init__(spec)
        self.engine = engine
        self._closed = False
        self._puts: dict[str, bytes] = {}
        self._deletes: set[str] = set()

    def put_object(self, key: str, data: bytes | bytearray | memoryview) -> str:
        self._require_write()
        physical_key = self.engine.object_key(key)
        self._put_key(physical_key, _as_bytes(data))
        return key

    def get_object(self, key: str) -> bytes:
        return self._get_key(self.engine.object_key(key))

    def delete_object(self, key: str) -> bool:
        self._require_write()
        physical_key = self.engine.object_key(key)
        existed = self._key_exists(physical_key)
        self._delete_key(physical_key)
        return existed

    def object_exists(self, key: str) -> bool:
        return self._key_exists(self.engine.object_key(key))

    def head_object(self, key: str) -> dict[str, Any]:
        physical_key = self.engine.object_key(key)
        if physical_key in self._puts:
            return {
                "ContentLength": len(self._puts[physical_key]),
                "staged": True,
            }
        if physical_key in self._deletes:
            raise FileNotFoundError(key)
        return self.engine.head_key(physical_key)

    def list_objects(self, prefix: str = "") -> list[str]:
        keys = set(self.engine.list_keys(prefix))
        marker = f"{self.engine.prefix}/" if self.engine.prefix else ""
        for key in self._puts:
            keys.add(key[len(marker) :] if marker and key.startswith(marker) else key)
        for key in self._deletes:
            logical = key[len(marker) :] if marker and key.startswith(marker) else key
            keys.discard(logical)
        if prefix:
            keys = {key for key in keys if key.startswith(prefix.strip("/"))}
        return sorted(keys)

    def put_cas(self, data: bytes | bytearray | memoryview) -> str:
        self._require_write()
        payload = _as_bytes(data)
        address = self.engine.cas_address(payload)
        key = self.engine.cas_key(address)
        if not self._key_exists(key):
            self._put_key(key, payload)
        return address

    def get_cas(self, address: str) -> bytes:
        payload = self._get_key(self.engine.cas_key(address))
        self.engine.verify_cas_payload(address, payload)
        return payload

    def cas_exists(self, address: str) -> bool:
        return self._key_exists(self.engine.cas_key(address))

    async def _tx_begin_impl(self) -> None:
        self._require_open_session()

    async def _tx_commit_impl(self) -> None:
        for key, data in self._puts.items():
            self.engine.put_key(key, data)
        for key in self._deletes:
            self.engine.delete_key(key)
        self._puts.clear()
        self._deletes.clear()

    async def _tx_rollback_impl(self) -> None:
        self._puts.clear()
        self._deletes.clear()

    async def _close_impl(self) -> None:
        self._puts.clear()
        self._deletes.clear()
        self._closed = True

    def _put_key(self, key: str, data: bytes) -> None:
        if self.in_transaction():
            self._puts[key] = data
            self._deletes.discard(key)
        else:
            self.engine.put_key(key, data)

    def _get_key(self, key: str) -> bytes:
        self._require_open_session()
        if key in self._deletes:
            raise FileNotFoundError(key)
        if key in self._puts:
            return self._puts[key]
        return self.engine.get_key(key)

    def _delete_key(self, key: str) -> None:
        if self.in_transaction():
            self._puts.pop(key, None)
            self._deletes.add(key)
        else:
            self.engine.delete_key(key)

    def _key_exists(self, key: str) -> bool:
        self._require_open_session()
        if key in self._deletes:
            return False
        if key in self._puts:
            return True
        return self.engine.key_exists(key)

    def _require_write(self) -> None:
        self._require_open_session()
        if self.read_only:
            raise RuntimeError("write attempted in read-only engine session")
        self._dirty = True

    def _require_open_session(self) -> None:
        if self._closed:
            raise RuntimeError("session is closed")

    def _add_impl(self, obj: Any) -> Any:
        raise TypeError("S3 object sessions do not support ORM add()")

    async def _delete_impl(self, obj: Any) -> None:
        raise TypeError("S3 object sessions do not support ORM delete()")

    async def _get_impl(self, model: type, ident: Any) -> Any | None:
        raise TypeError("use get_object() for S3 object sessions")

    async def _execute_impl(self, stmt: Any) -> Any:
        raise TypeError("S3 object sessions do not execute SQL statements")

    async def _executeloop_impl(self, statements: Iterable[Any]) -> Any:
        raise TypeError("S3 object sessions do not execute SQL statements")

    async def _executemany_impl(self, stmt: Any, parameter_sets: Any) -> Any:
        raise TypeError("S3 object sessions do not execute SQL statements")
