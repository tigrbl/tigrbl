from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar


class ExecutorBase(ABC):
    """Contract for runtime executors."""

    name: ClassVar[str]

    def __init__(self) -> None:
        self.runtime: Any | None = None

    def attach_runtime(self, runtime: Any) -> None:
        self.runtime = runtime

    def should_skip_channel_prelude(
        self,
        *,
        runtime: Any,
        env: Any,
        ctx: Any,
        plan: Any,
        packed_plan: Any | None = None,
    ) -> bool:
        del runtime, env, ctx, plan, packed_plan
        return False

    @abstractmethod
    async def invoke(
        self,
        *,
        runtime: Any,
        env: Any,
        ctx: Any,
        plan: Any,
        packed_plan: Any | None = None,
    ) -> Any:
        """Execute a kernel plan or packed kernel plan."""


__all__ = ["ExecutorBase"]
