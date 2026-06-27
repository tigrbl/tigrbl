from __future__ import annotations

from ._shared import *


class _PackedErrorEdgesMixin:
    async def _run_hot_jsonrpc_security_dependencies(
        self,
        ctx: _Ctx,
        hot: HotCtx,
        program_hot_runner_id: int,
    ) -> None:
        if hot.transport_kind_id != _TRANSPORT_KIND_JSONRPC:
            return
        if program_hot_runner_id == _HOT_RUNNER_GENERIC:
            return

        model = getattr(ctx, "model", None)
        alias = getattr(ctx, "op", None)
        if model is None or not isinstance(alias, str):
            return

        specs = getattr(getattr(model, "ops", None), "by_alias", {})
        spec_group = specs.get(alias) if isinstance(specs, Mapping) else None
        spec = tuple(spec_group or ())[:1]
        if not spec:
            return

        secdeps = tuple(getattr(spec[0], "secdeps", ()) or ())
        if not secdeps:
            secdeps = tuple(getattr(spec[0], "security_deps", ()) or ())
        if not secdeps:
            return

        from tigrbl_atoms.atoms.dep.security import _run as _run_security_dep

        for dep in secdeps:
            await _run_security_dep(dep, ctx)

    def _resolve_db_acquire(
        self,
        plan: KernelPlan,
        program_id: int,
        hot_op_plan: Any | None,
    ) -> Any:
        cache_key = (id(plan), program_id)
        cached = self._db_acquire_cache.get(cache_key)
        if cached is not None:
            return cached
        model = getattr(hot_op_plan, "model", None)
        alias = getattr(hot_op_plan, "alias", None)
        hint = str(getattr(hot_op_plan, "db_acquire_hint", "resolver") or "resolver")

        if hint == "model_get_db" and callable(
            getattr(model, "__tigrbl_get_db__", None)
        ):
            _resolver = import_module("tigrbl_concrete._concrete").engine_resolver

            def _acquire(_ctx: _Ctx) -> tuple[Any, Any]:
                return _resolver.acquire(model=model)

            self._db_acquire_cache[cache_key] = _acquire
            return _acquire

        provider_cache: dict[str, Any] = {}
        app_resolver_cache: dict[str, Any] = {}

        def _runtime_owner(ctx: _Ctx) -> Any:
            return getattr(ctx, "router", None) or getattr(ctx, "app", None)

        def _resolve_from_owner(ctx: _Ctx) -> Any:
            owner = _runtime_owner(ctx)
            if owner is None:
                return None
            if "resolver" in app_resolver_cache:
                return app_resolver_cache["resolver"]
            resolver = getattr(owner, "_tigrbl_runtime_resolve_provider", None)
            if callable(resolver):
                app_resolver_cache["resolver"] = resolver
                return resolver
            return None

        def _acquire_via_owner(ctx: _Ctx) -> tuple[Any, Any] | None:
            owner = _runtime_owner(ctx)
            acquire = getattr(owner, "_tigrbl_runtime_acquire_db", None)
            if callable(acquire):
                return acquire(
                    router=getattr(ctx, "router", None) or getattr(ctx, "app", None),
                    model=model,
                    op_alias=alias if isinstance(alias, str) else None,
                )
            return None

        def _release(db: Any) -> None:
            close = getattr(db, "close", None)
            if not callable(close):
                return
            try:
                rv = close()
                if inspect.isawaitable(rv):
                    try:
                        loop = asyncio.get_running_loop()
                    except RuntimeError:
                        asyncio.run(rv)
                    else:
                        loop.create_task(rv)
            except Exception:
                return

        def _acquire_from_provider(provider: Any) -> tuple[Any, Any]:
            db = provider.session()
            return db, lambda: _release(db)

        def _acquire(ctx: _Ctx) -> tuple[Any, Any]:
            owner_session = _acquire_via_owner(ctx)
            if owner_session is not None:
                return owner_session
            provider = provider_cache.get("provider")
            if provider is not None:
                return _acquire_from_provider(provider)
            resolver = _resolve_from_owner(ctx)
            provider = None
            if callable(resolver):
                provider = resolver(
                    router=getattr(ctx, "router", None) or getattr(ctx, "app", None),
                    model=model,
                    op_alias=alias if isinstance(alias, str) else None,
                )
            if provider is not None:
                provider_cache["provider"] = provider
                return _acquire_from_provider(provider)
            owner_session = _acquire_via_owner(ctx)
            if owner_session is not None:
                return owner_session
            raise RuntimeError("No runtime database acquisition callback is configured")

        self._db_acquire_cache[cache_key] = _acquire
        return _acquire

    async def _run_segment(self, ctx: _Ctx, packed: PackedKernel, seg_id: int) -> None:
        ctx.phase = normalize_phase(self._segment_phase_names(packed)[seg_id])
        await self._resolve_segment_runners(packed)[seg_id](ctx)

    async def _run_error_segments(
        self,
        ctx: _Ctx,
        packed: PackedKernel,
        error_phase_segments: Mapping[str, tuple[int, ...]],
        *phase_names: str,
    ) -> None:
        seen: set[str] = set()
        for phase_name in phase_names:
            if phase_name in seen:
                continue
            seen.add(phase_name)
            for seg_id in error_phase_segments.get(phase_name, ()):
                try:
                    await self._run_segment(ctx, packed, seg_id)
                except Exception:
                    pass

    async def _run_rollback_edge(
        self,
        ctx: _Ctx,
        packed: PackedKernel,
        error_phase_segments: Mapping[str, tuple[int, ...]],
    ) -> None:
        rollback_segments = error_phase_segments.get("TX_ROLLBACK", ())
        if rollback_segments:
            await self._run_error_segments(
                ctx,
                packed,
                error_phase_segments,
                "TX_ROLLBACK",
            )
            return

        db = getattr(ctx, "db", None) or getattr(ctx, "_raw_db", None)
        rollback = getattr(db, "rollback", None)
        if not callable(rollback):
            return
        rv = rollback()
        if inspect.isawaitable(rv):
            await rv

    async def _prepare_error_edge(
        self,
        ctx: _Ctx,
        packed: PackedKernel,
        error_phase_segments: Mapping[str, tuple[int, ...]],
        exc: BaseException,
    ) -> str:
        failed_phase = str(normalize_phase(getattr(ctx, "phase", "") or ""))
        rollback_required = failed_phase in {
            "START_TX",
            "PRE_HANDLER",
            "HANDLER",
            "POST_HANDLER",
            "PRE_COMMIT",
            "TX_COMMIT",
        } and bool(getattr(ctx, "owns_tx", False))
        edge = select_error_edge(
            failed_phase,
            rollback_required=rollback_required,
        )
        build_error_ctx(
            ctx,
            exc,
            failed_phase=failed_phase,
            err_target=edge.target,
            rollback_required=edge.target.kind == "rollback",
        )
        if edge.target.kind == "rollback":
            await self._run_rollback_edge(ctx, packed, error_phase_segments)
        return error_phase_for(failed_phase)

    def _resolve_error_segments(
        self,
        packed: PackedKernel,
        program_id: int,
    ) -> Mapping[str, tuple[int, ...]]:
        cache_key = (id(packed), program_id)
        cached = self._program_error_segments_cache.get(cache_key)
        if cached is not None:
            return cached[1]

        profile_ids = self._hot_array(
            packed,
            "program_error_profile_ids",
            tuple(getattr(packed, "program_error_profile_ids", ()) or ()),
        )
        profile_offsets = self._hot_array(
            packed,
            "error_profile_offsets",
            tuple(getattr(packed, "error_profile_offsets", ()) or ()),
        )
        if profile_offsets and program_id < len(profile_ids):
            phase_names = tuple(getattr(packed, "phase_names", ()) or ())
            profile_lengths = self._hot_array(packed, "error_profile_lengths", tuple(getattr(packed, "error_profile_lengths", ()) or ()))
            phase_ids = self._hot_array(packed, "error_profile_phase_ids", tuple(getattr(packed, "error_profile_phase_ids", ()) or ()))
            seg_ref_offsets = self._hot_array(packed, "error_profile_segment_offsets", tuple(getattr(packed, "error_profile_segment_ref_offsets", ()) or ()))
            seg_ref_lengths = self._hot_array(packed, "error_profile_segment_lengths", tuple(getattr(packed, "error_profile_segment_ref_lengths", ()) or ()))
            seg_refs = self._hot_array(packed, "error_profile_segment_refs", tuple(getattr(packed, "error_profile_segment_refs", ()) or ()))
            profile_id = profile_ids[program_id]
            if 0 <= profile_id < len(profile_offsets):
                start = profile_offsets[profile_id]
                length = profile_lengths[profile_id] if profile_id < len(profile_lengths) else 0
                frozen = {}
                for idx in range(start, start + length):
                    phase_id = phase_ids[idx]
                    phase_name = (
                        phase_names[phase_id]
                        if 0 <= phase_id < len(phase_names)
                        else str(phase_id)
                    )
                    seg_start = seg_ref_offsets[idx]
                    seg_length = seg_ref_lengths[idx]
                    frozen[str(normalize_phase(phase_name))] = tuple(
                        int(seg_refs[j]) for j in range(seg_start, seg_start + seg_length)
                    )
                ordered_segments, remaining_segments = self._resolve_segments_for_program(
                    packed, program_id
                )
                self._program_error_segments_cache[cache_key] = (
                    (*ordered_segments, *remaining_segments),
                    frozen,
                )
                return frozen

        grouped: dict[str, list[int]] = {}
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
        seg_offset = segment_offsets[program_id]
        seg_length = segment_lengths[program_id]
        for i in range(seg_offset, seg_offset + seg_length):
            seg_id = segment_refs[i]
            phase_name = str(normalize_phase(segment_phases[seg_id]))
            if phase_name.startswith("ON_") or phase_name == "TX_ROLLBACK":
                grouped.setdefault(phase_name, []).append(seg_id)

        ordered_segments, remaining_segments = self._resolve_segments_for_program(
            packed, program_id
        )
        frozen = {phase: tuple(seg_ids) for phase, seg_ids in grouped.items()}
        self._program_error_segments_cache[cache_key] = (
            (*ordered_segments, *remaining_segments),
            frozen,
        )
        return frozen
