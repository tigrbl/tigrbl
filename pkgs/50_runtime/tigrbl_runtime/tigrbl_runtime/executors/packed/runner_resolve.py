from __future__ import annotations

from ._shared import *


class _PackedRunnerResolveMixin:
    def _resolve_program_compiled_param_runner(
        self,
        packed: PackedKernel,
        program_id: int,
        hot_op_plan: Any | None,
    ) -> Any:
        cache_key = (id(packed), program_id, _HOT_RUNNER_COMPILED_PARAM)
        cached = self._program_runner_cache.get(cache_key)
        if cached is not None:
            return cached

        if hot_op_plan is not None:
            ordered = tuple(getattr(hot_op_plan, "ordered_segment_ids", ()) or ())
            remaining = tuple(getattr(hot_op_plan, "remaining_segment_ids", ()) or ())
            compiled_param_phase_steps = tuple(
                getattr(hot_op_plan, "compiled_param_phase_steps", ()) or ()
            )
        else:
            ordered, remaining = self._resolve_segments_for_program(packed, program_id)
            compiled_param_phase_steps = ()

        phase_names = self._segment_phase_names(packed)
        step_ids_by_segment = self._resolve_segment_step_ids(packed)
        async_flags = tuple(
            1 if bool(flag) else 0
            for flag in self._hot_array(
                packed,
                "atom_flags",
                tuple(
                    getattr(packed, "atom_catalog_async_flags", ())
                    or getattr(packed, "step_async_flags", ())
                    or ()
                ),
            )
        )
        opcode_ids = tuple(
            int(value)
            for value in self._hot_array(
                packed,
                "atom_opcode_ids",
                tuple(getattr(packed, "atom_catalog_opcode_ids", ()) or ()),
            )
        )
        opcode_keys = tuple(getattr(packed, "atom_opcode_keys", ()) or ())
        skip_step_ids: set[int] = set()
        skip_names = {
            "ingress.transport_extract",
            "ingress.input_prepare",
            "dispatch.binding_match",
            "dispatch.binding_parse",
            "dispatch.input_normalize",
            "wire.build_in",
            "wire.validate_in",
            "resolve.assemble",
            "sys.phase_db",
        }
        for step_id, opcode_id in enumerate(opcode_ids):
            if 0 <= opcode_id < len(opcode_keys):
                if str(opcode_keys[opcode_id]) in skip_names:
                    skip_step_ids.add(step_id)

        compiled_steps: list[tuple[str, int, Any, Any, bool]] = []
        phase_requires_db: dict[str, bool] = {}
        step_table = packed.step_table
        def _append_compiled_step(
            phase_name: str,
            step: Any,
            *,
            is_async: bool,
        ) -> None:
            if bool(getattr(step, "__tigrbl_skip_in_compiled_param", False)):
                return
            if bool(getattr(step, "__tigrbl_requires_phase_db", False)):
                phase_requires_db[phase_name] = True
            direct_run = getattr(step, "__tigrbl_direct_run", None)
            if callable(direct_run):
                direct_dep = getattr(step, "__tigrbl_direct_dep", None)
                has_direct_dep = bool(
                    getattr(step, "__tigrbl_has_direct_dep", False)
                )
                direct_is_async = bool(
                    getattr(step, "__tigrbl_direct_is_async", False)
                )
                use_two_args = bool(getattr(step, "__tigrbl_use_two_args", False))
                invoke_kind = (
                    _DIRECT_INVOKE_RUN_WITH_DEP
                    if has_direct_dep
                    else (
                        _DIRECT_INVOKE_RUN_WITH_NONE
                        if use_two_args
                        else _DIRECT_INVOKE_RUN
                    )
                )
                compiled_steps.append(
                    (
                        phase_name,
                        invoke_kind,
                        direct_run,
                        direct_dep,
                        direct_is_async,
                    )
                )
                return
            compiled_steps.append(
                (
                    phase_name,
                    _DIRECT_INVOKE_STEP,
                    step,
                    None,
                    is_async,
                )
            )

        if compiled_param_phase_steps:
            for phase_name, phase_steps in compiled_param_phase_steps:
                normalized_phase = str(normalize_phase(phase_name))
                for step in phase_steps:
                    atom_name = getattr(step, "__tigrbl_atom_name__", None)
                    if atom_name in skip_names:
                        continue
                    step_is_async = bool(getattr(step, "_tigrbl_is_async", False))
                    if not step_is_async:
                        marker = getattr(step, "__code__", None)
                        step_is_async = bool(getattr(marker, "co_flags", 0) & 0x80)
                    _append_compiled_step(
                        normalized_phase,
                        step,
                        is_async=step_is_async,
                    )
        else:
            for seg_id in (*ordered, *remaining):
                phase_name = str(normalize_phase(phase_names[seg_id]))
                for step_id in step_ids_by_segment[seg_id]:
                    step = step_table[step_id]
                    if step_id in skip_step_ids:
                        continue
                    _append_compiled_step(
                        phase_name,
                        step,
                        is_async=bool(async_flags[step_id]) if step_id < len(async_flags) else False,
                    )

        async def _runner(ctx: _Ctx) -> None:
            hot = self._prepare_compiled_dispatch_prelude(
                ctx, packed, program_id, hot_op_plan
            )
            if hot is None:
                return
            await self._prepare_compiled_input(ctx, hot, packed, program_id, hot_op_plan)
            self._publish_route_payload(ctx, hot)
            if hot.compiled_input_ready:
                plan = self._resolve_compiled_param_plan(
                    ctx,
                    packed,
                    program_id,
                    hot.param_shape_id,
                )
                self._compiled_validate_and_assemble(ctx, hot, plan)
                self._publish_compiled_payload(ctx, hot)
            current_phase = ""
            for phase_name, invoke_kind, call, dep, is_async in compiled_steps:
                if phase_name != current_phase:
                    ctx.phase = phase_name
                    current_phase = phase_name
                    if ctx.get("_raw_db") is not None:
                        from tigrbl_atoms.atoms.sys.phase_db import bind_phase_db

                        bind_phase_db(ctx)
                if invoke_kind == _DIRECT_INVOKE_RUN_WITH_DEP:
                    rv = call(dep, ctx)
                elif invoke_kind == _DIRECT_INVOKE_RUN_WITH_NONE:
                    rv = call(None, ctx)
                else:
                    rv = call(ctx)
                if is_async:
                    await rv
                elif rv is not None and callable(getattr(type(rv), "__await__", None)):
                    close = getattr(rv, "close", None)
                    if callable(close):
                        close()
                    raise RuntimeError(
                        f"sync compiled step returned awaitable in phase {phase_name!r}"
                    )

        self._program_runner_cache[cache_key] = _runner
        return _runner

    def _resolve_program_websocket_unary_text_runner(
        self,
        packed: PackedKernel,
        program_id: int,
        hot_op_plan: Any | None,
    ) -> Any:
        cache_key = (id(packed), program_id, _HOT_RUNNER_WS_UNARY_TEXT)
        cached = self._program_runner_cache.get(cache_key)
        if cached is not None:
            return cached

        endpoint = getattr(hot_op_plan, "websocket_direct_endpoint", None)
        if not callable(endpoint):
            runner = self._resolve_program_linear_direct_runner(
                packed, program_id, hot_op_plan
            )
            self._program_runner_cache[cache_key] = runner
            return runner
        endpoint_is_async = inspect.iscoroutinefunction(endpoint)

        async def _runner(ctx: _Ctx) -> None:
            temp = getattr(ctx, "temp", None)
            hot = dict.get(temp, "hot_ctx") if isinstance(temp, dict) else None
            if not isinstance(hot, HotCtx):
                raise RuntimeError("websocket fast runner requires hot websocket context")
            receive = hot.raw_receive
            send = hot.raw_send
            if not callable(send):
                raise RuntimeError("websocket fast runner requires send callable")
            first_message: Mapping[str, Any] | None = None
            if callable(receive):
                initial = await receive()
                if isinstance(initial, Mapping):
                    if initial.get("type") == "websocket.connect":
                        first_message = None
                    else:
                        first_message = initial
            websocket = _DirectWebSocketUnary(
                receive=receive,
                send=send,
                path=hot.path,
                path_params=hot.route_path_params or hot.path_params,
                buffered_message=first_message,
            )
            ctx.phase = "HANDLER"
            await websocket.accept()
            if endpoint_is_async:
                result = await endpoint(websocket)
            else:
                result = endpoint(websocket)
            if result is not None:
                ctx.result = result
            if result is not None and not websocket.sent_payload and not websocket.closed:
                if isinstance(result, memoryview):
                    await websocket.send_bytes(result.tobytes())
                elif isinstance(result, (bytes, bytearray)):
                    await websocket.send_bytes(bytes(result))
                elif isinstance(result, str):
                    await websocket.send_text(result)
                else:
                    try:
                        payload_text = json.dumps(result, separators=(",", ":"))
                    except TypeError:
                        payload_text = json.dumps(
                            result, separators=(",", ":"), default=str
                        )
                    await websocket.send_text(payload_text)
            hot.egress_sent = websocket.sent_payload
            if not websocket.closed:
                await websocket.close(1000)

        self._program_runner_cache[cache_key] = _runner
        return _runner

    def _resolve_program_runner(
        self, packed: PackedKernel, program_id: int, hot_op_plan: Any | None
    ) -> Any:
        cache_key = (id(packed), program_id)
        cached = self._program_runner_cache.get(cache_key)
        if cached is not None:
            return cached
        program_hot_runner_id = self._resolve_program_hot_runner_id(
            packed, program_id, hot_op_plan
        )
        if program_hot_runner_id == _HOT_RUNNER_COMPILED_PARAM:
            runner = self._resolve_program_compiled_param_runner(
                packed, program_id, hot_op_plan
            )
            self._program_runner_cache[cache_key] = runner
            return runner
        if program_hot_runner_id == _HOT_RUNNER_WS_UNARY_TEXT:
            runner = self._resolve_program_websocket_unary_text_runner(
                packed, program_id, hot_op_plan
            )
            self._program_runner_cache[cache_key] = runner
            return runner
        if program_hot_runner_id == _HOT_RUNNER_LINEAR_DIRECT:
            runner = self._resolve_program_linear_direct_runner(
                packed, program_id, hot_op_plan
            )
            self._program_runner_cache[cache_key] = runner
            return runner
        runners = self._resolve_segment_runners(packed)
        if hot_op_plan is not None:
            ordered = tuple(getattr(hot_op_plan, "ordered_segment_ids", ()) or ())
            remaining = tuple(getattr(hot_op_plan, "remaining_segment_ids", ()) or ())
        else:
            ordered, remaining = self._resolve_segments_for_program(packed, program_id)
        phase_names = self._segment_phase_names(packed)
        all_segment_ids = (*ordered, *remaining)

        async def _runner(ctx: _Ctx) -> None:
            temp = getattr(ctx, "temp", None)
            skip_dispatch = bool(
                isinstance(temp, dict) and temp.get("_tigrbl_hot_exact_route")
            )
            fast_direct_create = bool(
                isinstance(temp, dict) and temp.get("_tigrbl_hot_direct_create")
            )
            for seg_id in all_segment_ids:
                phase_name = str(normalize_phase(phase_names[seg_id]))
                if skip_dispatch and phase_name in {
                    "INGRESS_BEGIN",
                    "INGRESS_DISPATCH",
                }:
                    continue
                if fast_direct_create and phase_name in {
                    "POST_COMMIT",
                    "EGRESS_SHAPE",
                    "EGRESS_FINALIZE",
                    "POST_RESPONSE",
                }:
                    continue
                ctx.phase = phase_name
                await runners[seg_id](ctx)

        self._program_runner_cache[cache_key] = _runner
        return _runner

    def _resolve_program_runner_for_mode(
        self,
        packed: PackedKernel,
        program_id: int,
        hot_op_plan: Any | None,
        *,
        skip_dispatch: bool = False,
        fast_direct_create: bool = False,
    ) -> Any:
        mode = (1 if skip_dispatch else 0) | (2 if fast_direct_create else 0)
        cache_key = (id(packed), program_id, mode)
        cached = self._program_runner_mode_cache.get(cache_key)
        if cached is not None:
            return cached

        base_runner = self._resolve_program_runner(packed, program_id, hot_op_plan)
        if not skip_dispatch and not fast_direct_create:
            self._program_runner_mode_cache[cache_key] = base_runner
            return base_runner

        runners = self._resolve_segment_runners(packed)
        if hot_op_plan is not None:
            ordered = tuple(getattr(hot_op_plan, "ordered_segment_ids", ()) or ())
            remaining = tuple(getattr(hot_op_plan, "remaining_segment_ids", ()) or ())
        else:
            ordered, remaining = self._resolve_segments_for_program(packed, program_id)
        phase_names = self._segment_phase_names(packed)
        all_segment_ids = (*ordered, *remaining)

        skip_phases = set()
        if skip_dispatch:
            skip_phases.update({"INGRESS_BEGIN", "INGRESS_DISPATCH"})
        if fast_direct_create:
            skip_phases.update(
                {"POST_COMMIT", "EGRESS_SHAPE", "EGRESS_FINALIZE", "POST_RESPONSE"}
            )

        async def _runner(ctx: _Ctx) -> None:
            for seg_id in all_segment_ids:
                phase_name = str(normalize_phase(phase_names[seg_id]))
                if phase_name in skip_phases:
                    continue
                ctx.phase = phase_name
                await runners[seg_id](ctx)

        self._program_runner_mode_cache[cache_key] = _runner
        return _runner
