from __future__ import annotations

from ._shared import *


class _PackedSegmentsMixin:
    async def _probe_ingress_for_program(
        self, ctx: _Ctx, plan: KernelPlan, packed: PackedKernel
    ) -> int:
        if not getattr(plan, "opmeta", None):
            return -1

        seed_program_id = 0
        segment_offsets = self._hot_array(
            packed,
            "program_segment_offsets",
            tuple(getattr(packed, "program_segment_ref_offsets", ()) or getattr(packed, "op_segment_offsets", ()) or ()),
        )
        segment_lengths = self._hot_array(
            packed,
            "program_segment_lengths",
            tuple(getattr(packed, "program_segment_ref_lengths", ()) or getattr(packed, "op_segment_lengths", ()) or ()),
        )
        segment_refs = self._hot_array(
            packed,
            "program_segment_refs",
            tuple(getattr(packed, "program_segment_refs", ()) or getattr(packed, "op_to_segment_ids", ()) or ()),
        )
        segment_phases = self._segment_phase_names(packed)
        seg_offset = segment_offsets[seed_program_id]
        seg_length = segment_lengths[seed_program_id]
        for i in range(seg_offset, seg_offset + seg_length):
            seg_id = segment_refs[i]
            phase = str(segment_phases[seg_id])
            if not phase.startswith("INGRESS_"):
                break
            await self._run_segment(ctx, packed, seg_id)

        temp = getattr(ctx, "temp", None)
        if isinstance(temp, dict):
            temp["ingress_probed"] = True

        return self._require_program_id_from_ctx(ctx)

    def _resolve_segment_step_ids(
        self, packed: PackedKernel
    ) -> tuple[tuple[int, ...], ...]:
        packed_id = id(packed)
        cached = self._segment_steps_cache.get(packed_id)
        if cached is not None:
            return cached
        offsets_fallback = tuple(
            getattr(packed, "segment_catalog_offsets", ())
            or getattr(packed, "segment_offsets", ())
            or ()
        )
        lengths_fallback = tuple(
            getattr(packed, "segment_catalog_lengths", ())
            or getattr(packed, "segment_lengths", ())
            or ()
        )
        atom_refs_fallback = tuple(
            getattr(packed, "segment_catalog_atom_ids", ())
            or getattr(packed, "segment_step_ids", ())
            or ()
        )
        compiled = []
        for segment_index in range(
            self._hot_count(packed, "segment_step_offsets", offsets_fallback)
        ):
            start = self._hot_int_at(
                packed,
                "segment_step_offsets",
                segment_index,
                offsets_fallback,
            )
            length = self._hot_int_at(
                packed,
                "segment_step_lengths",
                segment_index,
                lengths_fallback,
            )
            if start is None or length is None:
                compiled.append(())
                continue
            end = int(start) + int(length)
            compiled.append(
                tuple(
                    int(
                        self._hot_int_at(
                            packed,
                            "segment_step_atom_refs",
                            idx,
                            atom_refs_fallback,
                        )
                        or 0
                    )
                    for idx in range(int(start), end)
                )
            )
        frozen = tuple(compiled)
        self._segment_steps_cache[packed_id] = frozen
        return frozen

    def _resolve_segment_runners(self, packed: PackedKernel) -> tuple[Any, ...]:
        packed_id = id(packed)
        cached = self._segment_runners_cache.get(packed_id)
        if cached is not None:
            return cached

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
        executor_kinds = tuple(
            self._hot_array(
                packed,
                "segment_executor_kind_ids",
                tuple(getattr(packed, "segment_catalog_executor_kinds", ()) or getattr(packed, "segment_executor_kinds", ()) or ()),
            )
        )

        step_table = packed.step_table

        def _compile_step(step_id: int) -> tuple[int, Any, Any, bool]:
            step = step_table[step_id]
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
                return (invoke_kind, direct_run, direct_dep, direct_is_async)
            return (
                _DIRECT_INVOKE_STEP,
                step,
                None,
                bool(async_flags[step_id]) if step_id < len(async_flags) else False,
            )

        def _invoke(call: Any, invoke_kind: int, dep: Any, ctx: _Ctx) -> Any:
            if invoke_kind == _DIRECT_INVOKE_RUN_WITH_DEP:
                return call(dep, ctx)
            if invoke_kind == _DIRECT_INVOKE_RUN_WITH_NONE:
                return call(None, ctx)
            return call(ctx)

        def _make_fused_sync_runner(step_ids: tuple[int, ...]):
            steps = tuple(_compile_step(step_id) for step_id in step_ids)

            async def _runner(ctx: _Ctx) -> None:
                for invoke_kind, call, dep, is_async in steps:
                    rv = _invoke(call, invoke_kind, dep, ctx)
                    if is_async or inspect.isawaitable(rv):
                        close = getattr(rv, "close", None)
                        if callable(close):
                            close()
                        raise RuntimeError("sync segment step returned awaitable")

            return _runner

        def _make_async_direct_runner(step_ids: tuple[int, ...]):
            steps = tuple(_compile_step(step_id) for step_id in step_ids)

            async def _runner(ctx: _Ctx) -> None:
                for invoke_kind, call, dep, is_async in steps:
                    rv = _invoke(call, invoke_kind, dep, ctx)
                    if is_async:
                        await rv
                    elif inspect.isawaitable(rv):
                        await rv

            return _runner

        def _make_mixed_runner(step_ids: tuple[int, ...]):
            steps = tuple(_compile_step(step_id) for step_id in step_ids)

            async def _runner(ctx: _Ctx) -> None:
                for invoke_kind, call, dep, is_async in steps:
                    rv = _invoke(call, invoke_kind, dep, ctx)
                    if is_async:
                        await rv
                        continue
                    if inspect.isawaitable(rv):
                        await rv

            return _runner

        runners: list[Any] = []
        for seg_id, step_ids in enumerate(step_ids_by_segment):
            executor_kind = executor_kinds[seg_id] if seg_id < len(executor_kinds) else ""
            if executor_kind in {"sync.extractable", 1}:
                runners.append(_make_fused_sync_runner(step_ids))
            elif executor_kind in {"async.direct", 3}:
                runners.append(_make_async_direct_runner(step_ids))
            else:
                runners.append(_make_mixed_runner(step_ids))

        frozen = tuple(runners)
        self._segment_runners_cache[packed_id] = frozen
        return frozen

    @classmethod
    def _resolve_program_hot_runner_id(
        cls,
        packed: PackedKernel,
        program_id: int,
        hot_op_plan: Any | None,
    ) -> int:
        return _kernel_resolve_program_hot_runner_id(
            packed,
            program_id,
            hot_op_plan,
        )

    def _resolve_program_linear_direct_runner(
        self,
        packed: PackedKernel,
        program_id: int,
        hot_op_plan: Any | None,
    ) -> Any:
        cache_key = (id(packed), program_id, _HOT_RUNNER_LINEAR_DIRECT)
        cached = self._program_runner_cache.get(cache_key)
        if cached is not None:
            return cached

        if hot_op_plan is not None:
            ordered = tuple(getattr(hot_op_plan, "ordered_segment_ids", ()) or ())
            remaining = tuple(getattr(hot_op_plan, "remaining_segment_ids", ()) or ())
        else:
            ordered, remaining = self._resolve_segments_for_program(packed, program_id)

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
        compiled_steps: list[tuple[str, int, Any, Any, bool]] = []
        step_table = packed.step_table
        for seg_id in (*ordered, *remaining):
            phase_name = str(normalize_phase(phase_names[seg_id]))
            for step_id in step_ids_by_segment[seg_id]:
                step = step_table[step_id]
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
                    continue
                compiled_steps.append(
                    (
                        phase_name,
                        _DIRECT_INVOKE_STEP,
                        step,
                        None,
                        bool(async_flags[step_id]) if step_id < len(async_flags) else False,
                    )
                )

        async def _runner(ctx: _Ctx) -> None:
            current_phase = ""
            for phase_name, invoke_kind, call, dep, is_async in compiled_steps:
                if phase_name != current_phase:
                    ctx.phase = phase_name
                    current_phase = phase_name
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
