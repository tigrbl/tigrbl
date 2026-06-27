from __future__ import annotations

from ._shared import *


class _PackedRouteSelectMixin:
    def _resolve_hot_exact_websocket_routes(
        self,
        plan: KernelPlan,
        packed: PackedKernel,
    ) -> Mapping[tuple[str, str], int]:
        return _kernel_resolve_hot_exact_websocket_routes(
            plan,
            packed,
            self._hot_exact_websocket_route_cache,
        )

    def _resolve_program_id_from_exact_websocket(
        self,
        plan: KernelPlan,
        packed: PackedKernel,
        protocol: str,
        path: str,
    ) -> int:
        return _kernel_resolve_program_id_from_exact_websocket(
            plan,
            packed,
            protocol,
            path,
            self._hot_exact_websocket_route_cache,
        )

    def _prime_exact_channel_program(
        self,
        ctx: _Ctx,
        env: Any,
        plan: KernelPlan,
        packed: PackedKernel,
    ) -> int:
        hot = self._ensure_hot_ctx(ctx, env)
        if hot.scope_type not in {"websocket", "webtransport"} or not hot.path:
            return -1
        if hot.scope_type == "websocket" and hot.protocol:
            program_id = self._resolve_program_id_from_exact_websocket(
                plan, packed, hot.protocol, hot.path
            )
        else:
            program_id = -1
        if program_id < 0:
            program_id = self._resolve_program_id_from_channel(ctx, plan)
        if program_id < 0:
            return -1
        temp = getattr(ctx, "temp", None)
        if not isinstance(temp, dict):
            return -1
        proto_to_id = getattr(packed, "proto_to_id", None)
        selector_to_id = getattr(packed, "selector_to_id", None)
        route_protocol = hot.protocol
        route_selector = hot.selector
        if hot.scope_type == "webtransport":
            route_protocol = "webtransport"
            route_selector = hot.path
        if isinstance(proto_to_id, Mapping):
            proto_id = self._coerce_int(proto_to_id.get(route_protocol))
            if proto_id is not None:
                hot.proto_id = proto_id
        if isinstance(selector_to_id, Mapping):
            selector_id = self._coerce_int(selector_to_id.get(route_selector))
            if selector_id is not None:
                hot.selector_id = selector_id
        hot.program_id = program_id
        hot.route_program_id = program_id
        hot.route_opmeta_index = program_id
        if not hot.route_protocol:
            hot.route_protocol = route_protocol
        if not hot.route_selector:
            hot.route_selector = route_selector
        if not hot.dispatch_channel_protocol:
            hot.dispatch_channel_protocol = hot.route_protocol or route_protocol
        if not hot.dispatch_channel_selector:
            hot.dispatch_channel_selector = hot.route_selector or route_selector
        hot.transport_kind_id = _TRANSPORT_KIND_CHANNEL
        ctx.path = hot.path
        temp["program_id"] = program_id
        return program_id

    def _prime_exact_websocket_program(
        self,
        ctx: _Ctx,
        env: Any,
        plan: KernelPlan,
        packed: PackedKernel,
    ) -> int:
        return self._prime_exact_channel_program(ctx, env, plan, packed)

    def _resolve_hot_exact_route_slices(
        self, packed: PackedKernel
    ) -> Mapping[int, tuple[int, int]]:
        return _kernel_resolve_hot_exact_route_slices(
            packed,
            self._hot_exact_route_cache,
        )

    def _resolve_program_id_from_exact_route(
        self, packed: PackedKernel, method: str, path: str
    ) -> int:
        return _kernel_resolve_program_id_from_exact_route(
            packed,
            method,
            path,
            self._hot_exact_route_cache,
            self._hot_exact_route_verify_cache,
        )

    def _resolve_hot_exact_route_verify(
        self, packed: PackedKernel
    ) -> Mapping[int, Mapping[int, tuple[tuple[str, int], ...]]]:
        return _kernel_resolve_hot_exact_route_verify(
            packed,
            self._hot_exact_route_verify_cache,
        )

    def _resolve_hot_exact_jsonrpc_routes(
        self, plan: KernelPlan
    ) -> Mapping[str, Mapping[str, tuple[int, str, str]]]:
        return _kernel_resolve_hot_exact_jsonrpc_routes(
            plan,
            self._hot_exact_jsonrpc_cache,
        )

    @staticmethod
    def _normalize_jsonrpc_mount_path(path: str) -> str:
        return _kernel_normalize_jsonrpc_mount_path(path)

    def _resolve_jsonrpc_endpoint_for_path(self, ctx: _Ctx, hot: HotCtx) -> str | None:
        path = self._normalize_jsonrpc_mount_path(hot.path)
        for owner_key in ("router", "app"):
            owner = getattr(ctx, owner_key, None)
            if owner is None and hasattr(ctx, "get"):
                owner = ctx.get(owner_key)
            mounts = getattr(owner, "_jsonrpc_endpoint_mounts", None)
            if isinstance(mounts, Mapping):
                endpoint = mounts.get(path) or mounts.get(hot.path) or mounts.get(f"{path}/")
                if isinstance(endpoint, str) and endpoint:
                    return endpoint
        for endpoint, mapped_path in __JSONRPC_DEFAULT_ENDPOINT_MAPPINGS__.items():
            if path == self._normalize_jsonrpc_mount_path(str(mapped_path)):
                return str(endpoint)
        return None

    async def _prime_exact_jsonrpc_program(
        self,
        ctx: _Ctx,
        env: Any,
        plan: KernelPlan,
        packed: PackedKernel,
    ) -> int:
        hot = self._ensure_hot_ctx(ctx, env)
        if hot.scope_type != "http" or str(hot.method or "").upper() != "POST":
            return -1

        endpoint = self._resolve_jsonrpc_endpoint_for_path(ctx, hot)
        if not endpoint:
            return -1

        request = self._ensure_hot_request(ctx, hot)
        body_bytes = await self._ensure_body_bytes(ctx, hot)
        if request is not None and body_bytes is not None and hasattr(request, "body"):
            request.body = body_bytes

        if not hot.parsed_json_loaded:
            parsed = None
            if body_bytes:
                try:
                    parsed = json.loads(body_bytes)
                except Exception:
                    parsed = None
            hot.parsed_json = parsed
            hot.parsed_json_loaded = True

        rpc_envelope = hot.parsed_json
        if not isinstance(rpc_envelope, dict) or rpc_envelope.get("jsonrpc") != "2.0":
            return -1
        rpc_method = rpc_envelope.get("method")
        if not isinstance(rpc_method, str) or not rpc_method:
            return -1

        routes = self._resolve_hot_exact_jsonrpc_routes(plan)
        endpoint_bucket = routes.get(endpoint)
        if not isinstance(endpoint_bucket, Mapping):
            return -1
        entry = endpoint_bucket.get(rpc_method)
        if not (
            isinstance(entry, tuple)
            and len(entry) == 3
            and isinstance(entry[0], int)
            and isinstance(entry[1], str)
            and isinstance(entry[2], str)
        ):
            return -1

        program_id, binding_protocol, binding_selector = entry
        hot.program_id = int(program_id)
        hot.route_program_id = int(program_id)
        hot.route_opmeta_index = int(program_id)
        hot.route_protocol = binding_protocol
        hot.route_selector = binding_selector
        hot.dispatch_binding_protocol = binding_protocol
        hot.dispatch_binding_selector = binding_selector
        hot.dispatch_jsonrpc_request_id = rpc_envelope.get("id")
        hot.dispatch_rpc_method = rpc_method
        hot.route_rpc_envelope = rpc_envelope
        hot.dispatch_rpc_envelope = rpc_envelope
        params = rpc_envelope.get("params")
        hot.route_payload = params if isinstance(params, dict) else None
        hot.transport_kind_id = _TRANSPORT_KIND_JSONRPC

        temp = getattr(ctx, "temp", None)
        if isinstance(temp, dict):
            temp["program_id"] = int(program_id)

        ctx.method = hot.method
        ctx.path = hot.path
        ctx.selector = binding_selector
        ctx.endpoint = endpoint
        return int(program_id)

    def _prime_exact_route_program(
        self, ctx: _Ctx, env: Any, packed: PackedKernel
    ) -> int:
        hot = self._ensure_hot_ctx(ctx, env)
        if hot.scope_type != "http" or not hot.method or not hot.path:
            return -1
        program_id = self._resolve_program_id_from_exact_route(
            packed, hot.method, hot.path
        )
        if program_id < 0:
            return -1

        temp = getattr(ctx, "temp", None)
        if not isinstance(temp, dict):
            return -1

        proto_to_id = getattr(packed, "proto_to_id", None)
        selector_to_id = getattr(packed, "selector_to_id", None)
        if isinstance(proto_to_id, Mapping):
            proto_id = self._coerce_int(proto_to_id.get(hot.protocol))
            if proto_id is not None:
                hot.proto_id = proto_id
        if isinstance(selector_to_id, Mapping):
            selector_id = self._coerce_int(selector_to_id.get(hot.selector))
            if selector_id is not None:
                hot.selector_id = selector_id
        hot.program_id = program_id
        hot.route_program_id = program_id
        hot.route_opmeta_index = program_id
        if not hot.route_protocol:
            hot.route_protocol = hot.protocol
        if not hot.route_selector:
            hot.route_selector = hot.selector
        if not hot.dispatch_binding_protocol:
            hot.dispatch_binding_protocol = hot.route_protocol or hot.protocol
        if not hot.dispatch_binding_selector:
            hot.dispatch_binding_selector = hot.route_selector or hot.selector
        hot.transport_kind_id = _TRANSPORT_KIND_REST

        ctx.method = hot.method
        ctx.path = hot.path
        temp["program_id"] = program_id
        return program_id

    @classmethod
    def _prepare_compiled_dispatch_prelude(
        cls,
        ctx: _Ctx,
        packed: PackedKernel,
        program_id: int,
        hot_op_plan: Any | None,
    ) -> HotCtx | None:
        temp = getattr(ctx, "temp", None)
        if not isinstance(temp, dict):
            return None
        hot = dict.get(temp, "hot_ctx")
        if not isinstance(hot, HotCtx):
            return None
        hot.program_id = program_id
        hot.route_program_id = program_id
        hot.route_opmeta_index = program_id
        if not hot.route_protocol:
            hot.route_protocol = hot.protocol
        if not hot.route_selector:
            hot.route_selector = hot.selector
        if not hot.dispatch_binding_protocol:
            hot.dispatch_binding_protocol = hot.route_protocol or hot.protocol
        if not hot.dispatch_binding_selector:
            hot.dispatch_binding_selector = hot.route_selector or hot.selector
        if hot.scope_type in {"websocket", "webtransport"}:
            if not hot.dispatch_channel_protocol:
                hot.dispatch_channel_protocol = hot.route_protocol or hot.protocol
            if not hot.dispatch_channel_selector:
                hot.dispatch_channel_selector = hot.route_selector or hot.selector
        hot.transport_kind_id = cls._resolve_program_transport_kind_id(
            packed, program_id, hot_op_plan
        )
        if hot.method and getattr(ctx, "method", None) in (None, ""):
            ctx.method = hot.method
        if hot.path and getattr(ctx, "path", None) in (None, ""):
            ctx.path = hot.path
        proto_to_id = getattr(packed, "proto_to_id", None)
        if hot.proto_id < 0 and isinstance(proto_to_id, Mapping):
            proto_id = cls._coerce_int(proto_to_id.get(hot.protocol))
            if proto_id is not None:
                hot.proto_id = proto_id
        selector_to_id = getattr(packed, "selector_to_id", None)
        if hot.selector_id < 0 and isinstance(selector_to_id, Mapping):
            selector_id = cls._coerce_int(selector_to_id.get(hot.selector))
            if selector_id is not None:
                hot.selector_id = selector_id
        return hot
