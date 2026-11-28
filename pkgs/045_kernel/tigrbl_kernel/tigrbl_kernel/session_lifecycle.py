from __future__ import annotations

import asyncio
import inspect
import logging
from collections.abc import Callable
from typing import Any

_logger = logging.getLogger(__name__)


class SessionTermination:
    """Run ordered, independent terminal effects once for one session."""

    def __init__(self) -> None:
        self._cleanup: asyncio.Task[None] | None = None

    async def run(self, *effects: Callable[[], Any]) -> None:
        if self._cleanup is None:
            self._cleanup = asyncio.create_task(self._run_effects(effects))
        cancellation = None
        while True:
            try:
                await asyncio.shield(self._cleanup)
                break
            except asyncio.CancelledError as exc:
                if self._cleanup.cancelled():
                    raise
                if cancellation is None:
                    cancellation = exc
        if cancellation is not None:
            raise cancellation

    @staticmethod
    async def _run_effects(effects: tuple[Callable[[], Any], ...]) -> None:
        for effect in effects:
            try:
                result = effect()
                if inspect.isawaitable(result):
                    await result
            except (Exception, asyncio.CancelledError):
                _logger.exception("Realtime session cleanup effect failed")
