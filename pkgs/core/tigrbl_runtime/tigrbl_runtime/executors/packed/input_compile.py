from __future__ import annotations

from ._shared import *


class _PackedInputCompileMixin:
    @staticmethod
    def _compiled_schema_in(
        ctx: _Ctx,
    ) -> tuple[tuple[str, ...], Mapping[str, Mapping[str, Any]], tuple[str, ...]]:
        opview = getattr(ctx, "opview", None)
        schema_in = getattr(opview, "schema_in", None) if opview is not None else None
        if isinstance(schema_in, Mapping):
            fields = tuple(schema_in.get("fields", ()) or ())
            by_field = schema_in.get("by_field", {}) or {}
            required = tuple(schema_in.get("required", ()) or ())
        else:
            fields = tuple(getattr(schema_in, "fields", ()) or ())
            by_field = getattr(schema_in, "by_field", {}) or {}
            required = tuple(getattr(schema_in, "required", ()) or ())
        if not required:
            required = tuple(
                name
                for name, meta in by_field.items()
                if isinstance(meta, Mapping) and meta.get("required")
            )
        return fields, by_field, required

    def _resolve_compiled_param_plan(
        self,
        ctx: _Ctx,
        packed: PackedKernel,
        program_id: int,
        param_shape_id: int,
    ) -> _CompiledParamPlan:
        cache_key = (id(packed), program_id, param_shape_id)
        cached = self._compiled_param_plan_cache.get(cache_key)
        if cached is not None:
            return cached

        field_names, by_field, required = self._compiled_schema_in(ctx)
        opview = getattr(ctx, "opview", None)
        field_index = {field_name: idx for idx, field_name in enumerate(field_names)}
        required_set = frozenset(required)
        field_plans = tuple(
            _CompiledFieldPlan(
                slot_id=idx,
                field_name=field_name,
                required=field_name in required_set,
                nullable=(
                    bool(meta.get("nullable"))
                    if meta.get("nullable") is not None
                    else None
                ),
                py_type=meta.get("py_type"),
                coerce=bool(meta.get("coerce", True)),
                max_length=(
                    int(meta.get("max_length"))
                    if isinstance(meta.get("max_length"), int)
                    else 0
                ),
                validator=meta.get("validator"),
                in_enabled=bool(meta.get("in_enabled", True)),
                is_virtual=bool(meta.get("virtual", False)),
                default_factory=meta.get("default_factory"),
            )
            for idx, field_name in enumerate(field_names)
            for meta in ((by_field.get(field_name, {}) or {}),)
        )

        start, length = self._param_shape_descriptor_slice(packed, param_shape_id)
        lookup_hashes_fallback = tuple(
            getattr(packed, "param_shape_lookup_hashes", ()) or ()
        )
        header_hashes_fallback = tuple(
            getattr(packed, "param_shape_header_hashes", ()) or ()
        )
        source_masks_fallback = tuple(
            getattr(packed, "param_shape_source_masks", ()) or ()
        )
        slot_ids_fallback = tuple(getattr(packed, "param_shape_slot_ids", ()) or ())
        decoder_ids_fallback = tuple(
            getattr(packed, "param_shape_decoder_ids", ()) or ()
        )
        max_lengths_fallback = tuple(
            getattr(packed, "param_shape_max_lengths", ()) or ()
        )

        descriptor_rows: list[_CompiledInputDescriptor] = []
        body_lookup_names: set[str] = set()
        reserved_input_keys: set[str] = set()
        needs_query = False
        needs_header = False
        needs_path = False
        for idx in range(start, start + length):
            slot_id = self._hot_int_at(
                packed,
                "param_shape_slot_ids",
                idx,
                slot_ids_fallback,
            )
            if not (0 <= slot_id < len(field_names)):
                continue
            field_name = field_names[slot_id]
            field_meta = by_field.get(field_name, {}) if isinstance(by_field, Mapping) else {}
            source_mask = self._hot_int_at(
                packed,
                "param_shape_source_masks",
                idx,
                source_masks_fallback,
            )
            lookup_name = self._compiled_lookup_name(field_name, field_meta)
            if bool(source_mask & _PARAM_SOURCE_BODY):
                body_lookup_names.add(lookup_name)
            needs_query = needs_query or bool(source_mask & _PARAM_SOURCE_QUERY)
            needs_header = needs_header or bool(source_mask & _PARAM_SOURCE_HEADER)
            needs_path = needs_path or bool(source_mask & _PARAM_SOURCE_PATH)
            descriptor_rows.append(
                _CompiledInputDescriptor(
                    slot_id=slot_id,
                    lookup_name=lookup_name,
                    source_mask=source_mask,
                    decoder_id=self._hot_int_at(
                        packed,
                        "param_shape_decoder_ids",
                        idx,
                        decoder_ids_fallback,
                    ),
                    max_length=self._hot_int_at(
                        packed,
                        "param_shape_max_lengths",
                        idx,
                        max_lengths_fallback,
                    ),
                    lookup_hash=self._hot_int_at(
                        packed,
                        "param_shape_lookup_hashes",
                        idx,
                        lookup_hashes_fallback,
                    ),
                    header_hash=self._hot_int_at(
                        packed,
                        "param_shape_header_hashes",
                        idx,
                        header_hashes_fallback,
                    ),
                )
            )

        strategy_kind, strategy_rows = self._resolve_param_shape_decode_strategy(
            packed,
            program_id,
            param_shape_id,
            field_names,
            by_field if isinstance(by_field, Mapping) else {},
        )
        paired_index = getattr(opview, "paired_index", {}) or {}
        for field_name, desc in paired_index.items():
            if isinstance(field_name, str) and field_name and field_name not in field_index:
                reserved_input_keys.add(field_name)
            alias = desc.get("alias") if isinstance(desc, Mapping) else None
            if isinstance(alias, str) and alias:
                reserved_input_keys.add(alias)
        plan = _CompiledParamPlan(
            field_names=field_names,
            field_index=field_index,
            field_plans=field_plans,
            descriptor_plans=tuple(descriptor_rows),
            strategy_kind=strategy_kind,
            strategy_rows=strategy_rows,
            assemble_order=tuple(field_index[name] for name in sorted(field_names)),
            body_lookup_names=frozenset(body_lookup_names),
            reserved_input_keys=frozenset(reserved_input_keys),
            needs_query=needs_query,
            needs_header=needs_header,
            needs_path=needs_path,
        )
        self._compiled_param_plan_cache[cache_key] = plan
        return plan

    def _compiled_validate_and_assemble(
        self,
        ctx: _Ctx,
        hot: HotCtx,
        plan: _CompiledParamPlan,
    ) -> None:
        field_names = plan.field_names
        slot_values = hot.slot_values or []
        slot_present = hot.slot_present or bytearray()
        errors: list[dict[str, Any]] = []
        coerced: list[str] = []

        for field_plan in plan.field_plans:
            slot_id = field_plan.slot_id
            present = 0 <= slot_id < len(slot_present) and bool(slot_present[slot_id])
            if field_plan.required and not present:
                errors.append(
                    {
                        "field": field_plan.field_name,
                        "code": "required",
                        "message": "Field is required but was not provided.",
                    }
                )
                continue
            if not present or not (0 <= slot_id < len(slot_values)):
                continue

            value = slot_values[slot_id]
            if value is None and field_plan.nullable is False:
                errors.append(
                    {
                        "field": field_plan.field_name,
                        "code": "null_not_allowed",
                        "message": "Null is not allowed for this field.",
                    }
                )
                continue

            target_type = field_plan.py_type
            if value is not None and isinstance(target_type, type):
                ok, new_val, msg = _coerce_if_needed(
                    value,
                    target_type,
                    allow=field_plan.coerce,
                )
                if not ok:
                    errors.append(
                        {
                            "field": field_plan.field_name,
                            "code": "type_mismatch",
                            "message": msg or f"Expected {target_type.__name__}.",
                        }
                    )
                    continue
                if new_val is not value:
                    slot_values[slot_id] = new_val
                    value = new_val
                    coerced.append(field_plan.field_name)

            if (
                field_plan.max_length > 0
                and isinstance(value, str)
                and len(value) > field_plan.max_length
            ):
                errors.append(
                    {
                        "field": field_plan.field_name,
                        "code": "max_length",
                        "message": f"String exceeds max_length={field_plan.max_length}.",
                    }
                )
                continue

            validator = field_plan.validator
            if callable(validator) and value is not None:
                try:
                    out = validator(value, ctx)
                    if out is not None:
                        slot_values[slot_id] = out
                except Exception as exc:
                    errors.append(
                        {
                            "field": field_plan.field_name,
                            "code": "validator_failed",
                            "message": f"{type(exc).__name__}: {exc}",
                        }
                    )

        hot.compiled_in_invalid = bool(errors)
        hot.compiled_in_errors = tuple(dict(error) for error in errors) if errors else None
        hot.compiled_in_coerced = tuple(coerced)
        hot.in_present_names = tuple(
            field_names[idx]
            for idx in range(min(len(field_names), len(slot_present)))
            if slot_present[idx]
        )

        if errors:
            raise HTTPException(
                status_code=_status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=[dict(error) for error in errors],
            )

        assembled_values = list(slot_values)
        assembled_present = bytearray(len(field_names))
        virtual_values = list(slot_values)
        virtual_present = bytearray(len(field_names))
        absent: list[str] = []
        used_default: list[str] = []
        view = None

        for slot_id in plan.assemble_order:
            if not (0 <= slot_id < len(plan.field_plans)):
                continue
            field_plan = plan.field_plans[slot_id]
            present = 0 <= slot_id < len(slot_present) and bool(slot_present[slot_id])
            if present:
                value = slot_values[slot_id]
                if field_plan.is_virtual:
                    virtual_values[slot_id] = value
                    virtual_present[slot_id] = 1
                elif field_plan.in_enabled:
                    assembled_values[slot_id] = value
                    assembled_present[slot_id] = 1
                continue

            absent.append(field_plan.field_name)
            default_fn = field_plan.default_factory
            if callable(default_fn) and field_plan.in_enabled and not field_plan.is_virtual:
                if view is None:
                    view = _ctx_view(ctx)
                try:
                    default_value = default_fn(view)
                except Exception:
                    continue
                assembled_values[slot_id] = default_value
                assembled_present[slot_id] = 1
                used_default.append(field_plan.field_name)

        hot.assembled_slot_values = assembled_values
        hot.assembled_slot_present = assembled_present
        hot.virtual_slot_values = virtual_values
        hot.virtual_slot_present = virtual_present
        hot.assembled_values_view = None
        hot.virtual_in_view = None
        hot.absent_fields = tuple(absent)
        hot.used_default_factory = tuple(used_default)
