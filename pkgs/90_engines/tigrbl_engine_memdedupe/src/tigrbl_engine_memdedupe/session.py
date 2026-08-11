from __future__ import annotations

from typing import Any

from tigrbl_base._base import EngineSessionBase
from tigrbl_core._spec.engine_session_spec import EngineSessionSpec

from .engine import DedupeEngine


class DedupeSession(EngineSessionBase):
    def __init__(
        self,
        engine: DedupeEngine,
        spec: EngineSessionSpec | None = None,
    ) -> None:
        super().__init__(spec)
        self._engine = engine
        self._closed = False

    async def _tx_begin_impl(self) -> None:
        return

    async def _tx_commit_impl(self) -> None:
        return

    async def _tx_rollback_impl(self) -> None:
        return

    async def _close_impl(self) -> None:
        self._closed = True

    def seen(self, key: str) -> bool:
        self._require_not_closed()
        return self._engine.seen(self._require_key(key))

    def mark(self, key: str, *, ttl_s: float | None = None) -> None:
        self._require_writable("mark")
        self._engine.mark(self._require_key(key), ttl_s=ttl_s)
        self._dirty = True

    def mark_if_absent(self, key: str, *, ttl_s: float | None = None) -> bool:
        self._require_writable("mark_if_absent")
        accepted = self._engine.mark_if_absent(self._require_key(key), ttl_s=ttl_s)
        if accepted:
            self._dirty = True
        return accepted

    async def forget(self, key: str) -> bool:
        self._require_writable("forget")
        removed = self._engine.discard(self._require_key(key))
        if removed:
            self._dirty = True
        return removed

    def size(self) -> int:
        self._require_not_closed()
        return self._engine.size()

    def reset(self) -> None:
        self._require_writable("reset")
        self._engine.reset()
        self._dirty = True

    def stats(self) -> dict[str, Any]:
        self._require_not_closed()
        return self._engine.stats()

    def _require_not_closed(self) -> None:
        if self._closed:
            raise RuntimeError("session is closed")

    def _require_writable(self, operation: str) -> None:
        self._require_not_closed()
        if self._spec and self._spec.read_only:
            raise RuntimeError(
                f"write attempted in read-only engine session ({operation})"
            )

    @staticmethod
    def _require_key(value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("memdedupe keys must be strings")
        return value

    def _add_impl(self, obj: Any) -> Any:
        del obj
        raise TypeError("memdedupe sessions do not support ORM add(); use mark()")

    async def _delete_impl(self, obj: Any) -> None:
        self._require_not_closed()
        self._engine.discard(self._require_key(obj))

    async def _get_impl(self, model: type, ident: Any) -> Any | None:
        del model, ident
        raise TypeError("memdedupe sessions do not support ORM get(); use seen()")

    async def _execute_impl(self, stmt: Any) -> Any:
        del stmt
        raise TypeError("memdedupe sessions do not execute statements")

    async def _executeloop_impl(self, statements: Any) -> Any:
        del statements
        raise TypeError("memdedupe sessions do not execute statement batches")

    async def _executemany_impl(self, stmt: Any, parameter_sets: Any) -> Any:
        del stmt, parameter_sets
        raise TypeError("memdedupe sessions do not execute statement batches")


class AsyncDedupeSession(DedupeSession):
    """Deprecated compatibility name; DedupeSession already has async lifecycle."""
