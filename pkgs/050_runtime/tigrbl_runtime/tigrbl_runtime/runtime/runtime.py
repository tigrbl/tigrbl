from __future__ import annotations

from typing import Any

from tigrbl_kernel import Kernel, _kernel
from tigrbl_kernel.asgi_dispatch import KernelAsgiApp, execute_plan
from tigrbl_typing.gw.raw import GwRawEnvelope
from tigrbl_typing.trace import TraceSink

from tigrbl_runtime.channel import complete_channel, prepare_channel_context
from tigrbl_runtime.executors import (
    ExecutorBase,
    NumbaPackedPlanExecutor,
    PackedPlanExecutor,
)
from .base import RuntimeBase


def _normalize_execution_backend(value: Any) -> str:
    lowered = str(value or "auto").strip().lower()
    if not lowered:
        return "auto"
    if lowered in {"auto", "python"}:
        return lowered
    raise ValueError(f"unsupported execution backend: {value!r}")


class Runtime(RuntimeBase):
    """Runtime orchestrator for kernel + executors."""

    def __init__(
        self,
        kernel: Kernel | None = None,
        *,
        default_executor: str = "packed",
        kernel_backend: str = "auto",
        atoms_backend: str = "auto",
        executor_backend: str = "python",
        trace_sink: TraceSink | None = None,
        trace_atoms: bool = False,
    ) -> None:
        resolved_kernel = kernel if kernel is not None else _kernel()
        super().__init__(kernel=resolved_kernel)
        self.default_executor = default_executor
        self.trace_sink = trace_sink
        self.trace_atoms = trace_atoms and trace_sink is not None
        self.kernel_backend = _normalize_execution_backend(kernel_backend)
        self.atoms_backend = _normalize_execution_backend(atoms_backend)
        self.executor_backend = _normalize_execution_backend(executor_backend)
        self.register_executor(PackedPlanExecutor())
        self.register_executor(NumbaPackedPlanExecutor())

    def register_executor(self, executor: ExecutorBase) -> None:
        executor.attach_runtime(self)
        self.executors[executor.name] = executor

    @staticmethod
    def _revision_of(app: Any) -> int:
        revision = getattr(app, "_runtime_plan_revision", 0)
        try:
            return int(revision)
        except Exception:
            return 0

    def compile(self, *args: Any, **kwargs: Any) -> tuple[Any, Any | None]:
        if args:
            app = args[0]
        else:
            app = kwargs.get("app")
        if app is None:
            raise ValueError("Runtime.compile requires an app instance")

        revision = getattr(app, "_runtime_plan_revision", 0)
        kernel_id = id(self.kernel)
        cache_key = (kernel_id, revision)
        cached = getattr(app, "_runtime_compile_cache", None)
        if isinstance(cached, tuple) and len(cached) == 3 and cached[0] == cache_key:
            return cached[1], cached[2]

        plan = self.kernel.kernel_plan(app)
        packed_plan = getattr(plan, "packed", None)
        app._runtime_compile_cache = (cache_key, plan, packed_plan)
        return plan, packed_plan

    @staticmethod
    async def prepare_channel_context(env: Any, ctx: Any) -> None:
        await prepare_channel_context(env, ctx)

    @staticmethod
    async def complete_channel(env: Any, ctx: Any, **kwargs: Any) -> None:
        await complete_channel(env, ctx, **kwargs)

    def bind_asgi(self, app: Any) -> None:
        self._asgi_entry_point = KernelAsgiApp(app, self)

    async def dispatch_asgi(self, scope: dict[str, Any], receive: Any, send: Any) -> Any:
        return await self._asgi_entry_point(scope, receive, send)

    async def invoke_app(self, app: Any, env: GwRawEnvelope) -> None:
        await KernelAsgiApp(app, self).invoke(env)

    async def invoke(
        self,
        *,
        executor: str | None = None,
        env: Any,
        ctx: Any,
        plan: Any,
        packed_plan: Any | None = None,
    ) -> Any:
        return await execute_plan(
            self, executor=executor, env=env, ctx=ctx, plan=plan,
            packed_plan=packed_plan,
        )


__all__ = ["Runtime"]
