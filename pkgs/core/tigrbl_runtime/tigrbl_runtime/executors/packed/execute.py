from __future__ import annotations

from ._shared import *


class _PackedExecuteMixin:
    async def _execute_packed(
        self, env: Any, ctx: _Ctx, plan: KernelPlan, packed: PackedKernel
    ) -> None:
        _send_json, _send_transport_response = self._resolve_transport_senders()
        StatusDetailError, create_standardized_error = self._resolve_error_helpers()

        temp = getattr(ctx, "temp", None)
        if not isinstance(temp, dict):
            ctx.temp = {}
            temp = ctx.temp

        hot = self._ensure_hot_ctx(ctx, env)
        ctx.plan = plan
        ctx.kernel_plan = plan
        if hot.method and getattr(ctx, "method", None) in (None, ""):
            ctx.method = hot.method
        if hot.path and getattr(ctx, "path", None) in (None, ""):
            ctx.path = hot.path
        if (
            hot.scope_type == "http"
            and str(hot.method or "").upper() == "POST"
            and self._resolve_jsonrpc_endpoint_for_path(ctx, hot)
        ):
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
            if isinstance(hot.parsed_json, Mapping) and hot.parsed_json.get("jsonrpc") == "2.0":
                params = hot.parsed_json.get("params", {})
                if isinstance(params, Mapping) and set(params) == {"params"}:
                    egress = temp.setdefault("egress", {})
                    if isinstance(egress, dict):
                        egress["transport_response"] = {
                            "status_code": 204,
                            "body": b"",
                        }
                    hot.route_short_circuit = True
                    hot.route_rpc_envelope = dict(hot.parsed_json)
                    hot.dispatch_rpc_envelope = dict(hot.parsed_json)
                    await _send_transport_response(env, ctx)
                    return
            if isinstance(hot.parsed_json, list):
                await _send_json(
                    env,
                    200,
                    await self._execute_jsonrpc_batch(ctx, hot, hot.parsed_json),
                )
                return

        program_id = self._require_program_id_from_ctx(ctx)
        if program_id < 0:
            program_id = self._prime_exact_route_program(ctx, env, packed)
        if program_id < 0:
            program_id = await self._prime_exact_jsonrpc_program(
                ctx, env, plan, packed
            )
        if program_id < 0:
            program_id = self._prime_exact_channel_program(ctx, env, plan, packed)
        if program_id < 0:
            program_id = await self._probe_ingress_for_program(ctx, plan, packed)
        if program_id < 0:
            scope = getattr(env, "scope", {}) or {}
            transport = hot.egress_transport_response
            if isinstance(transport, dict):
                await _send_transport_response(env, ctx)
                return

            if hot.route_method_not_allowed:
                await _send_json(env, 405, {"detail": "Method Not Allowed"})
                return
            if str(scope.get("type") or "") == "websocket":
                send = getattr(env, "send", None)
                if callable(send):
                    await send({"type": "websocket.close", "code": 4404})
                return
            if str(scope.get("type") or "") == "webtransport":
                send = getattr(env, "send", None)
                if callable(send):
                    await send({"type": "webtransport.close", "code": 4404})
                return
            await _send_json(
                env, 404, {"detail": "No runtime operation matched request."}
            )
            return

        temp["program_id"] = program_id

        hot_op_plan = (
            packed.hot_op_plans[program_id]
            if program_id < len(getattr(packed, "hot_op_plans", ()))
            else None
        )
        self._seed_batch_policy_from_hot_plan(ctx, hot_op_plan)
        self._seed_batch_scheduler(ctx, hot_op_plan, env)
        program_hot_runner_id = self._resolve_program_hot_runner_id(
            packed, program_id, hot_op_plan
        )

        if program_id >= len(plan.opmeta):
            await _send_json(
                env, 404, {"detail": "No runtime operation matched request."}
            )
            return
        if hot_op_plan is not None:
            ctx.model = hot_op_plan.model
            ctx.op = hot_op_plan.alias
            ctx.target = hot_op_plan.target
        else:
            meta = plan.opmeta[program_id]
            ctx.model = getattr(meta, "model", None)
            ctx.op = getattr(meta, "alias", None)
            ctx.target = getattr(meta, "target", None)
        env_ref = ctx.get("env")
        if env_ref is None:
            ctx["env"] = SimpleNamespace(method=ctx.op)
        elif getattr(env_ref, "method", None) in (None, "", "unknown"):
            try:
                setattr(env_ref, "method", ctx.op)
            except Exception:
                ctx["env"] = SimpleNamespace(method=ctx.op)
        release_db = None
        acquire_db = None
        batch_policy = self._batch_policy_mapping(hot_op_plan)
        batch_enabled = bool(batch_policy.get("enabled", False))
        if (
            program_hot_runner_id != _HOT_RUNNER_WS_UNARY_TEXT
            and getattr(ctx, "_raw_db", None) is None
        ):
            try:
                acquire_db = self._resolve_db_acquire(plan, program_id, hot_op_plan)
                ctx.temp["batch_db_acquire"] = acquire_db
                ctx.batch_db_acquire = acquire_db
                if not batch_enabled:
                    db, release_db = acquire_db(ctx)
                    ctx._raw_db = db
                    if getattr(ctx, "db", None) is None:
                        ctx.db = db
                    ctx.owns_tx = True
            except Exception:
                release_db = None
        if (
            program_hot_runner_id != _HOT_RUNNER_WS_UNARY_TEXT
            and hot_op_plan is not None
            and hot_op_plan.opview is not None
        ):
            ctx.opview = hot_op_plan.opview
        elif program_hot_runner_id != _HOT_RUNNER_WS_UNARY_TEXT:
            app = getattr(ctx, "app", None)
            if app is not None and ctx.model is not None and isinstance(ctx.op, str):
                opview_key = (id(plan), program_id)
                opview = self._opview_cache.get(opview_key)
                if opview is None:
                    opview = self.runtime.kernel.get_opview(app, ctx.model, ctx.op)
                    self._opview_cache[opview_key] = opview
                ctx.opview = opview

        try:
            if hot_op_plan is not None:
                error_phase_segments = hot_op_plan.error_segment_ids
            else:
                error_phase_segments = self._resolve_error_segments(
                    packed,
                    program_id,
            )

            try:
                await self._run_hot_jsonrpc_security_dependencies(
                    ctx,
                    hot,
                    program_hot_runner_id,
                )
                if hot.transport_kind_id == _TRANSPORT_KIND_JSONRPC and isinstance(
                    hot.parsed_json, dict
                ):
                    opview = getattr(ctx, "opview", None)
                    schema_in = getattr(opview, "schema_in", None)
                    field_names = tuple(getattr(schema_in, "fields", ()) or ())
                    self._reject_jsonrpc_wrapper_keys(
                        hot.parsed_json.get("params", {}),
                        field_names=field_names,
                    )
                await self._resolve_program_runner(
                    packed,
                    program_id,
                    hot_op_plan,
                )(ctx)
            except StatusDetailError as exc:
                detail = (
                    exc.detail
                    if getattr(exc, "detail", None) not in (None, "")
                    else str(exc)
                )
                error_phase = await self._prepare_error_edge(
                    ctx,
                    packed,
                    error_phase_segments,
                    exc,
                )
                fallback_phase = "ON_ERROR"
                await self._run_error_segments(
                    ctx,
                    packed,
                    error_phase_segments,
                    error_phase,
                    fallback_phase,
                )
                status_code = int(getattr(exc, "status_code", 500) or 500)
                payload = self._jsonrpc_error_payload(ctx, status_code, detail)
                await _send_json(
                    env,
                    200 if payload is not None else status_code,
                    payload or {"detail": detail},
                    headers=getattr(exc, "headers", None),
                )
                return
            except Exception as exc:
                std = create_standardized_error(exc)
                detail = (
                    std.detail
                    if getattr(std, "detail", None) not in (None, "")
                    else str(std)
                )
                error_phase = await self._prepare_error_edge(
                    ctx,
                    packed,
                    error_phase_segments,
                    exc,
                )
                fallback_phase = "ON_ERROR"
                await self._run_error_segments(
                    ctx,
                    packed,
                    error_phase_segments,
                    error_phase,
                    fallback_phase,
                )
                status_code = int(getattr(std, "status_code", 500) or 500)
                persistence_error = self._is_persistence_exception(exc)
                if persistence_error:
                    status_code = 500
                    detail = "Internal error"
                payload = self._jsonrpc_error_payload(
                    ctx,
                    status_code,
                    detail,
                    sanitize_detail=persistence_error,
                )
                await _send_json(
                    env,
                    200 if payload is not None else status_code,
                    payload or {"detail": detail},
                    headers=getattr(std, "headers", None),
                )
                return

            if program_hot_runner_id == _HOT_RUNNER_WS_UNARY_TEXT:
                return
            if isinstance(temp, dict) and temp.get("_tigrbl_hot_direct_create") is True:
                status = int(getattr(ctx, "status_code", 201) or 201)
                payload = self._serialize_model_row(getattr(ctx, "result", None))
                await _send_json(env, status, payload)
                return
            if hot.route_short_circuit and hot.egress_transport_response:
                await _send_transport_response(env, ctx)
                return

            await _send_transport_response(env, ctx)
        finally:
            if callable(release_db):
                try:
                    release_db()
                except Exception:
                    pass

    def _build_python_packed_executor(self, packed: PackedKernel):
        async def _executor(kernel: Any, env: Any, ctx: _Ctx, plan: KernelPlan) -> None:
            del kernel
            await self._execute_packed(env, ctx, plan, packed)

        return _executor

    def _build_numba_packed_executor(self, packed: PackedKernel):
        if not packed.route_to_program:
            return None
        try:
            from numba import njit
        except Exception:
            return None

        route_to_program = packed.route_to_program

        @njit(cache=True)
        def _dispatch(proto_id: int, selector_id: int) -> int:
            if proto_id < 0 or selector_id < 0:
                return -1
            if proto_id >= len(route_to_program):
                return -1
            row = route_to_program[proto_id]
            if selector_id >= len(row):
                return -1
            return row[selector_id]

        def _executor(proto_id: int, selector_id: int) -> int:
            return int(_dispatch(int(proto_id), int(selector_id)))

        return _executor

    async def invoke(
        self,
        *,
        runtime: Any,
        env: Any,
        ctx: Any,
        plan: Any,
        packed_plan: Any | None = None,
    ) -> Any:
        if not isinstance(plan, KernelPlan):
            raise TypeError("PackedPlanExecutor requires a KernelPlan instance")
        if not isinstance(packed_plan, PackedKernel):
            raise TypeError("PackedPlanExecutor requires a PackedKernel instance")

        base_ctx = _Ctx.ensure(
            request=ctx.get("request") if isinstance(ctx, Mapping) else None,
            db=ctx.get("db") if isinstance(ctx, Mapping) else None,
            seed=ctx,
        )
        await self._execute_packed(env, base_ctx, plan, packed_plan)
        return base_ctx.get("result")
