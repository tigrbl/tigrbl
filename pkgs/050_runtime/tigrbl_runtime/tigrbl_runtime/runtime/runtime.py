from __future__ import annotations

from typing import Any

from tigrbl_atoms.atoms.ingress.identity import prepare_transport_identity
from tigrbl_atoms.atoms.transport.completion_fence import observe_http_completion
from tigrbl_atoms.atoms.transport.asgi_channel import bind_asgi_ingress
from tigrbl_atoms import protocol_scope
from tigrbl_kernel import Kernel, _kernel, asgi_dispatch
from tigrbl_kernel.asgi_dispatch import AsgiLifecycle
from tigrbl_kernel.webtransport_session_plan import WebTransportSessionPlan
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

    async def dispatch_asgi(
        self, app: Any, scope: dict[str, Any], receive: Any, send: Any
    ) -> None:
        projection = protocol_scope.project_asgi_scope(scope)
        state = scope.get("state")
        batch_item = state.get("_tigrbl_rpc_batch_item") if isinstance(state, dict) else None
        plan = scope.get("_tigrbl_asgi_ingress_plan") if isinstance(batch_item, dict) else None
        if not isinstance(plan, asgi_dispatch.AsgiIngressPlan):
            plan = asgi_dispatch.select_asgi_ingress(projection)
            scope["_tigrbl_asgi_ingress_plan"] = plan
        scope["app"] = app
        if plan.default_scheme and not scope.get("scheme"):
            scope = {**scope, "scheme": plan.default_scheme}
        send = bind_asgi_ingress(scope, projection, send, app.trace_sink)
        if plan.lifecycle is AsgiLifecycle.REQUEST:
            await app._handle_http(scope, receive, send)
        elif plan.lifecycle is AsgiLifecycle.APPLICATION:
            await app._handle_lifespan(scope, receive, send)
        else:
            env = GwRawEnvelope(kind="asgi3", scope=scope, receive=receive, send=send)
            if plan.lifecycle is AsgiLifecycle.WEBSOCKET_SESSION:
                await self.invoke_app(app, env)
            elif plan.lifecycle is AsgiLifecycle.WEBTRANSPORT_SESSION:
                await WebTransportSessionPlan().run(
                    scope,
                    lambda: self.invoke_app(app, env),
                    lambda state: self._snapshot_webtransport_trace(app, state),
                )

    @staticmethod
    def _snapshot_webtransport_trace(app: Any, state: dict[str, Any]) -> None:
        trace = state.get("trace")
        if isinstance(trace, list):
            app._webtransport_trace_latest = list(trace)
            snapshots = getattr(app, "_webtransport_trace_snapshots", None)
            if not isinstance(snapshots, list):
                snapshots = app._webtransport_trace_snapshots = []
            snapshots.append(list(trace))

    async def invoke_app(self, app: Any, env: GwRawEnvelope) -> None:
        plan, packed_plan = self.compile(app)
        ctx = {
            "app": app,
            "router": app,
            "raw": env,
            "env": env,
            "kernel_plan": plan,
            "plan": plan,
            "packed_plan": packed_plan,
            "temp": {},
        }
        await self.invoke(env=env, ctx=ctx, plan=plan, packed_plan=packed_plan)

    async def invoke(
        self,
        *,
        executor: str | None = None,
        env: Any,
        ctx: Any,
        plan: Any,
        packed_plan: Any | None = None,
    ) -> Any:
        scope = getattr(env, "scope", None)
        if isinstance(scope, dict):
            identity = prepare_transport_identity(scope)
            state = scope.get("state", {})
            batch_item = state.get("_tigrbl_rpc_batch_item") if isinstance(state, dict) else None
            if isinstance(batch_item, dict):
                identity.update(batch_item)
            temp = ctx.get("temp")
            if isinstance(temp, dict) and identity:
                temp["identity"] = identity
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
        with observe_http_completion(env) as http_completion:
            try:
                if not skip_channel_prelude:
                    await prepare_channel_context(env, ctx)
                result = await impl.invoke(
                    runtime=self,
                    env=env,
                    ctx=ctx,
                    plan=plan,
                    packed_plan=packed_plan,
                )
            finally:
                if http_completion is not None:
                    await complete_channel(env, ctx, http_completion=http_completion)
        if http_completion is None and not skip_channel_prelude:
            await complete_channel(env, ctx)
        return result


__all__ = ["Runtime"]
