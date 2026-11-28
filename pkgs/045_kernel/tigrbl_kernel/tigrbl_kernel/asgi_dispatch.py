from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from tigrbl_atoms import protocol_scope
from tigrbl_atoms.atoms.ingress.identity import prepare_transport_identity
from tigrbl_atoms.atoms.transport.asgi_channel import bind_asgi_ingress
from tigrbl_atoms.atoms.transport.completion_fence import observe_http_completion
from tigrbl_atoms.protocol_scope import AsgiScope, AsgiScopeKind
from tigrbl_typing.gw.raw import GwRawEnvelope

from .webtransport_session_plan import WebTransportSessionPlan


class AsgiLifecycle(str, Enum):
    REQUEST = "request"
    WEBSOCKET_SESSION = "websocket_session"
    WEBTRANSPORT_SESSION = "webtransport_session"
    APPLICATION = "application"


@dataclass(frozen=True, slots=True)
class AsgiIngressPlan:
    lifecycle: AsgiLifecycle
    default_scheme: str | None = None


_INGRESS_PLANS = {
    AsgiScopeKind.HTTP: AsgiIngressPlan(AsgiLifecycle.REQUEST),
    AsgiScopeKind.WEBSOCKET: AsgiIngressPlan(AsgiLifecycle.WEBSOCKET_SESSION, "ws"),
    AsgiScopeKind.WEBTRANSPORT: AsgiIngressPlan(
        AsgiLifecycle.WEBTRANSPORT_SESSION, "webtransport"
    ),
    AsgiScopeKind.LIFESPAN: AsgiIngressPlan(AsgiLifecycle.APPLICATION),
}


def select_asgi_ingress(projection: AsgiScope) -> AsgiIngressPlan:
    """Select the carrier lifecycle before operation dispatch."""
    return _INGRESS_PLANS[projection.kind]


@dataclass(frozen=True, slots=True)
class AsgiOperationMiss:
    status_code: int
    detail: str = ""
    close_event: str | None = None


_OPERATION_MISSES = {
    AsgiScopeKind.WEBSOCKET: AsgiOperationMiss(4404, close_event="websocket.close"),
    AsgiScopeKind.WEBTRANSPORT: AsgiOperationMiss(
        4404, close_event="webtransport.close"
    ),
}
_HTTP_MISS = AsgiOperationMiss(404, "No runtime operation matched request.")
_METHOD_NOT_ALLOWED = AsgiOperationMiss(405, "Method Not Allowed")


def select_asgi_operation_miss(
    scope_kind: str, *, method_not_allowed: bool = False
) -> AsgiOperationMiss:
    if method_not_allowed:
        return _METHOD_NOT_ALLOWED
    return _OPERATION_MISSES.get(scope_kind, _HTTP_MISS)


class KernelAsgiApp:
    """A kernel entry point configured for one application."""

    def __init__(self, app: Any, services: Any) -> None:
        self.app = app
        self.services = services

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        app = self.app
        state = scope.get("state")
        batch_item = state.get("_tigrbl_rpc_batch_item") if isinstance(state, dict) else None
        plan = scope.get("_tigrbl_asgi_ingress_plan") if isinstance(batch_item, dict) else None
        projection = protocol_scope._cached_scope(scope) if isinstance(plan, AsgiIngressPlan) else None
        if projection is None:
            projection = protocol_scope.project_asgi_scope(scope)
            plan = None
        if plan is None:
            plan = select_asgi_ingress(projection)
            scope["_tigrbl_asgi_ingress_plan"] = plan
        scope["app"] = app
        if plan.default_scheme and not scope.get("scheme"):
            scope = {**scope, "scheme": plan.default_scheme}
        send = bind_asgi_ingress(scope, projection, send, app.trace_sink)
        if plan.lifecycle is AsgiLifecycle.APPLICATION:
            await app._handle_lifespan(scope, receive, send)
            return
        if plan.lifecycle is AsgiLifecycle.REQUEST and await app._handle_http_prelude(
            scope, receive, send
        ):
            return

        env = GwRawEnvelope(kind="asgi3", scope=scope, receive=receive, send=send)
        if plan.lifecycle is AsgiLifecycle.WEBTRANSPORT_SESSION:
            await WebTransportSessionPlan().run(
                scope,
                lambda: self.invoke(env),
                lambda state: self._snapshot_webtransport_trace(app, state),
            )
        else:
            await self.invoke(env)

    @staticmethod
    def _snapshot_webtransport_trace(app: Any, state: dict[str, Any]) -> None:
        trace = state.get("trace")
        if isinstance(trace, list):
            app._webtransport_trace_latest = list(trace)
            snapshots = getattr(app, "_webtransport_trace_snapshots", None)
            if not isinstance(snapshots, list):
                snapshots = app._webtransport_trace_snapshots = []
            snapshots.append(list(trace))

    async def invoke(self, env: GwRawEnvelope) -> None:
        app = self.app
        plan = self.services.kernel.kernel_plan(app)
        packed_plan = getattr(plan, "packed", None)
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
        await execute_plan(
            self.services, env=env, ctx=ctx, plan=plan, packed_plan=packed_plan,
        )


async def execute_plan(
    services: Any,
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
    selected = executor or services.default_executor
    impl = services.executors.get(selected)
    if impl is None:
        raise KeyError(f"Unknown executor: {selected}")
    skip_channel_prelude = bool(
        impl.should_skip_channel_prelude(
            runtime=services,
            env=env,
            ctx=ctx,
            plan=plan,
            packed_plan=packed_plan,
        )
    )
    with observe_http_completion(env) as http_completion:
        try:
            if not skip_channel_prelude:
                await services.prepare_channel_context(env, ctx)
            result = await impl.invoke(
                runtime=services,
                env=env,
                ctx=ctx,
                plan=plan,
                packed_plan=packed_plan,
            )
        finally:
            if http_completion is not None:
                await services.complete_channel(env, ctx, http_completion=http_completion)
    if http_completion is None and not skip_channel_prelude:
        await services.complete_channel(env, ctx)
    return result
