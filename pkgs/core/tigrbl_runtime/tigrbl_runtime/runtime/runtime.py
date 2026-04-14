from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from tigrbl_kernel import Kernel, RustPlan, _kernel

from tigrbl_runtime.channel import complete_channel, prepare_channel_context
from tigrbl_runtime.executors import (
    ExecutorBase,
    NumbaPackedPlanExecutor,
    PackedPlanExecutor,
)
from tigrbl_runtime.rust import (
    ExecutionBackend,
    RustBackendConfig,
    build_rust_app_spec,
    coerce_execution_backend,
    compile_app as compile_rust_app,
    create_runtime_from_compiled,
    rust_parity_snapshot,
    normalize_spec as normalize_rust_spec,
)
from tigrbl_runtime.rust.runtime import RustRuntimeHandle
from .base import RuntimeBase


class Runtime(RuntimeBase):
    """Runtime orchestrator for kernel + executors."""

    def __init__(
        self,
        kernel: Kernel | None = None,
        *,
        default_executor: str = "numba_packed",
        kernel_backend: str | ExecutionBackend = ExecutionBackend.AUTO,
        atoms_backend: str | ExecutionBackend = ExecutionBackend.AUTO,
        executor_backend: str | ExecutionBackend = ExecutionBackend.PYTHON,
        rust_backend: RustBackendConfig | None = None,
    ) -> None:
        resolved_kernel = kernel if kernel is not None else _kernel()
        super().__init__(kernel=resolved_kernel)
        self.default_executor = default_executor
        self.kernel_backend = coerce_execution_backend(kernel_backend)
        self.atoms_backend = coerce_execution_backend(atoms_backend)
        self.executor_backend = coerce_execution_backend(executor_backend)
        self.rust_backend = rust_backend or RustBackendConfig(
            backend=self.executor_backend
        )
        self._rust_compile_cache: dict[
            tuple[int, int, int, str, str, str], tuple[RustPlan, RustRuntimeHandle]
        ] = {}
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

    def _rust_cache_key(
        self,
        app: Any,
    ) -> tuple[int, int, int, str, str, str]:
        return (
            id(self.kernel),
            id(app),
            self._revision_of(app),
            self.kernel_backend.value,
            self.atoms_backend.value,
            self.executor_backend.value,
        )

    def _uses_rust_executor(self) -> bool:
        return self.executor_backend is ExecutionBackend.RUST

    def _compile_rust(self, app: Any) -> tuple[RustPlan, RustRuntimeHandle]:
        cache_key = self._rust_cache_key(app)
        cached = self._rust_compile_cache.get(cache_key)
        if cached is not None:
            return cached

        payload = build_rust_app_spec(app)
        normalized = normalize_rust_spec(payload)
        compiled = compile_rust_app(payload)
        plan = RustPlan(
            description=(
                "compiled rust KernelPlan for "
                f"{compiled.get('app_name', payload['name'])}"
            ),
            compiled_plan=compiled,
            backend="rust",
            normalized_spec=normalized,
            parity_snapshot=rust_parity_snapshot(payload),
            claimable=False,
        )
        handle = create_runtime_from_compiled(compiled)
        self._rust_compile_cache[cache_key] = (plan, handle)
        return plan, handle

    @staticmethod
    def _coerce_rust_envelope(envelope: Any) -> dict[str, Any]:
        if isinstance(envelope, Mapping):
            return dict(envelope)
        asdict = getattr(envelope, "asdict", None)
        if callable(asdict):
            payload = asdict()
            if isinstance(payload, Mapping):
                return dict(payload)
        raise TypeError(
            "Runtime.execute_rust expects a mapping-like envelope or value with asdict()"
        )

    @staticmethod
    def _execute_with_handle(
        handle: RustRuntimeHandle,
        envelope: dict[str, Any],
    ) -> dict[str, Any]:
        transport = str(envelope.get("transport", "rest") or "rest").lower()
        dispatch = {
            "rest": handle.execute_rest,
            "jsonrpc": handle.execute_jsonrpc,
            "rpc": handle.execute_jsonrpc,
            "ws": handle.execute_ws,
            "stream": handle.execute_stream,
            "sse": handle.execute_sse,
        }
        execute = dispatch.get(transport)
        if execute is None:
            raise ValueError(f"unsupported rust transport: {transport!r}")
        return execute(envelope)

    def rust_handle(self, app: Any) -> RustRuntimeHandle:
        _, handle = self._compile_rust(app)
        return handle

    def execute_rust(
        self,
        envelope: Any,
        *,
        app: Any | None = None,
        handle: RustRuntimeHandle | None = None,
    ) -> dict[str, Any]:
        resolved_handle = handle
        if resolved_handle is None:
            if app is None:
                raise ValueError(
                    "Runtime.execute_rust requires either an app or a rust handle"
                )
            resolved_handle = self.rust_handle(app)
        payload = self._coerce_rust_envelope(envelope)
        return self._execute_with_handle(resolved_handle, payload)

    def compile(self, *args: Any, **kwargs: Any) -> tuple[Any, Any | None]:
        if args:
            app = args[0]
        else:
            app = kwargs.get("app")
        if app is None:
            raise ValueError("Runtime.compile requires an app instance")

        if self._uses_rust_executor():
            rust_plan, rust_handle = self._compile_rust(app)
            return rust_plan, rust_handle

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
        if self._uses_rust_executor():
            resolved_handle = packed_plan
            if resolved_handle is None and isinstance(ctx, Mapping):
                app = ctx.get("app") or ctx.get("router")
                if app is not None:
                    resolved_handle = self.rust_handle(app)
            return self.execute_rust(env, handle=resolved_handle)

        selected = executor or self.default_executor
        impl = self.executors.get(selected)
        if impl is None:
            raise KeyError(f"Unknown executor: {selected}")
        await prepare_channel_context(env, ctx)
        result = await impl.invoke(
            runtime=self,
            env=env,
            ctx=ctx,
            plan=plan,
            packed_plan=packed_plan,
        )
        await complete_channel(env, ctx)
        return result


__all__ = ["Runtime"]
