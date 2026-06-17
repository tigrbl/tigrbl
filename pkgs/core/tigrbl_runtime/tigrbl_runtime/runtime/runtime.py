from __future__ import annotations

from typing import Any

from tigrbl_kernel import Kernel, _kernel

from tigrbl_runtime.channel import complete_channel, prepare_channel_context
from tigrbl_runtime.executors import (
    ExecutorBase,
    NumbaPackedPlanExecutor,
    PackedPlanExecutor,
)
from tigrbl_runtime.rust import (
    ExecutionBackend,
    RustBackendConfig,
    reject_rust_backend,
    RustBindingsUnavailableError,
)
from .base import RuntimeBase


class Runtime(RuntimeBase):
    """Runtime orchestrator for kernel + executors."""

    def __init__(
        self,
        kernel: Kernel | None = None,
        *,
        default_executor: str = "packed",
        kernel_backend: str | ExecutionBackend = ExecutionBackend.AUTO,
        atoms_backend: str | ExecutionBackend = ExecutionBackend.AUTO,
        executor_backend: str | ExecutionBackend = ExecutionBackend.PYTHON,
        rust_backend: RustBackendConfig | None = None,
    ) -> None:
        resolved_kernel = kernel if kernel is not None else _kernel()
        super().__init__(kernel=resolved_kernel)
        self.default_executor = default_executor
        self.kernel_backend = reject_rust_backend(
            kernel_backend,
            label="kernel_backend",
        )
        self.atoms_backend = reject_rust_backend(
            atoms_backend,
            label="atoms_backend",
        )
        self.executor_backend = reject_rust_backend(
            executor_backend,
            label="executor_backend",
        )
        self.rust_backend = rust_backend or RustBackendConfig(
            backend=self.executor_backend
        )
        reject_rust_backend(self.rust_backend, label="rust_backend")
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

    def _uses_rust_executor(self) -> bool:
        return False

    def _compile_rust(self, app: Any) -> tuple[Any, Any]:
        del app
        raise RustBindingsUnavailableError(
            "Runtime._compile_rust is unavailable. "
            "Tigrbl runtime execution is Python-only."
        )

    def rust_handle(self, app: Any) -> Any:
        del app
        raise RustBindingsUnavailableError(
            "Runtime.rust_handle is unavailable. "
            "Tigrbl runtime execution is Python-only."
        )

    def execute_rust(
        self,
        envelope: Any,
        *,
        app: Any | None = None,
        handle: Any | None = None,
    ) -> dict[str, Any]:
        del envelope, app, handle
        raise RustBindingsUnavailableError(
            "Runtime.execute_rust is unavailable. "
            "Tigrbl runtime execution is Python-only."
        )

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

    async def invoke(
        self,
        *,
        executor: str | None = None,
        env: Any,
        ctx: Any,
        plan: Any,
        packed_plan: Any | None = None,
    ) -> Any:
        selected = executor or self.default_executor
        impl = self.executors.get(selected)
        if impl is None:
            raise KeyError(f"Unknown executor: {selected}")
        skip_channel_prelude = bool(
            impl.should_skip_channel_prelude(
                runtime=self,
                env=env,
                ctx=ctx,
                plan=plan,
                packed_plan=packed_plan,
            )
        )
        if not skip_channel_prelude:
            await prepare_channel_context(env, ctx)
        result = await impl.invoke(
            runtime=self,
            env=env,
            ctx=ctx,
            plan=plan,
            packed_plan=packed_plan,
        )
        if not skip_channel_prelude:
            await complete_channel(env, ctx)
        return result


__all__ = ["Runtime"]
