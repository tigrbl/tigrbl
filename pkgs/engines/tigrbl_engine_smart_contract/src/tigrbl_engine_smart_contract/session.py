from __future__ import annotations

from typing import Any

from .engine import SmartContractEngine


class SmartContractSession:
    def __init__(self, engine: SmartContractEngine) -> None:
        self._engine = engine
        self._closed = False

    def close(self) -> None:
        self._closed = True

    def call(
        self,
        function_name: str,
        *args: Any,
        block_identifier: str | int = "latest",
    ) -> Any:
        self._require_open()
        fn = getattr(self._engine.contract.functions, function_name)
        return fn(*args).call(block_identifier=block_identifier)

    def transact(
        self,
        function_name: str,
        *args: Any,
        tx_params: dict[str, Any] | None = None,
    ) -> str:
        self._require_open()
        fn = getattr(self._engine.contract.functions, function_name)
        tx_hash = fn(*args).transact(tx_params or {})
        return tx_hash.hex()

    def estimate_gas(
        self,
        function_name: str,
        *args: Any,
        tx_params: dict[str, Any] | None = None,
    ) -> int:
        self._require_open()
        fn = getattr(self._engine.contract.functions, function_name)
        return int(fn(*args).estimate_gas(tx_params or {}))

    def events(
        self,
        event_name: str,
        *,
        from_block: int | str = "latest",
        to_block: int | str = "latest",
        argument_filters: dict[str, Any] | None = None,
    ) -> list[Any]:
        self._require_open()
        event_cls = getattr(self._engine.contract.events, event_name)
        log_filter = event_cls.create_filter(
            from_block=from_block,
            to_block=to_block,
            argument_filters=argument_filters or {},
        )
        return list(log_filter.get_all_entries())

    def _require_open(self) -> None:
        if self._closed:
            raise RuntimeError("session is closed")


class AsyncSmartContractSession(SmartContractSession):
    async def close(self) -> None:  # type: ignore[override]
        super().close()
