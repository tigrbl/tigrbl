from __future__ import annotations

from typing import Any

from .kv import KVStore


class KVSession:
    def __init__(self, engine: KVStore) -> None:
        self._engine = engine
        self._closed = False

    def close(self) -> None:
        self._closed = True

    def get(self, key: str, default: Any = None) -> Any:
        self._require_open()
        return self._engine.get(key, default)

    def get_version(self, key: str) -> int | None:
        self._require_open()
        return self._engine.get_version(key)

    def set(self, key: str, value: Any, *, ttl_s: float | None = None) -> int:
        self._require_open()
        return self._engine.set(key, value, ttl_s=ttl_s)

    def cas(self, key: str, expected_version: int, value: Any, *, ttl_s: float | None = None) -> int | None:
        self._require_open()
        return self._engine.cas(key, expected_version, value, ttl_s=ttl_s)

    def delete(self, key: str) -> bool:
        self._require_open()
        return self._engine.delete(key)

    def keys(self, prefix: str = "") -> list[str]:
        self._require_open()
        return self._engine.keys(prefix)

    def reset(self) -> None:
        self._require_open()
        self._engine.reset()

    def stats(self) -> dict:
        self._require_open()
        return self._engine.stats()

    def _require_open(self) -> None:
        if self._closed:
            raise RuntimeError("session is closed")


class AsyncKVSession(KVSession):
    async def close(self) -> None:  # type: ignore[override]
        super().close()
