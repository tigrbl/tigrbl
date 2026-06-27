from __future__ import annotations

from ._shared import *


class _PackedInputExtractMixin:
    @staticmethod
    def _compiled_lookup_name(field_name: str, field_meta: Any) -> str:
        return _atom_compiled_lookup_name(field_name, field_meta)

    @staticmethod
    def _publish_compiled_slots(
        hot: HotCtx,
        field_names: tuple[str, ...],
        field_index: Mapping[str, int],
        slot_values: list[Any],
        slot_present: bytearray,
    ) -> None:
        _atom_publish_compiled_slots(
            hot,
            field_names,
            field_index,
            slot_values,
            slot_present,
        )

    def _resolve_param_shape_decode_strategy(
        self,
        packed: PackedKernel,
        program_id: int,
        param_shape_id: int,
        field_names: tuple[str, ...],
        by_field: Mapping[str, Any],
    ) -> tuple[int, tuple[tuple[int, str, int, int], ...]]:
        cache_key = (id(packed), program_id, param_shape_id)
        cached = self._param_shape_decode_strategy_cache.get(cache_key)
        if cached is not None:
            return cached

        start, length = self._param_shape_descriptor_slice(packed, param_shape_id)
        strategy: tuple[int, tuple[tuple[int, str, int, int], ...]] = (
            _DECODE_STRATEGY_GENERIC_HASHED,
            (),
        )
        if length > 0 and field_names:
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
            rows: list[tuple[int, str, int, int]] = []
            body_only = True
            for idx in range(start, start + length):
                source_mask = self._hot_int_at(
                    packed,
                    "param_shape_source_masks",
                    idx,
                    source_masks_fallback,
                )
                if source_mask != _PARAM_SOURCE_BODY:
                    body_only = False
                    break
                slot_id = self._hot_int_at(
                    packed,
                    "param_shape_slot_ids",
                    idx,
                    slot_ids_fallback,
                )
                if not (0 <= slot_id < len(field_names)):
                    body_only = False
                    break
                field_name = field_names[slot_id]
                field_meta = by_field.get(field_name, {}) if isinstance(by_field, Mapping) else {}
                rows.append(
                    (
                        slot_id,
                        self._compiled_lookup_name(field_name, field_meta),
                        self._hot_int_at(
                            packed,
                            "param_shape_decoder_ids",
                            idx,
                            decoder_ids_fallback,
                        ),
                        self._hot_int_at(
                            packed,
                            "param_shape_max_lengths",
                            idx,
                            max_lengths_fallback,
                        ),
                    )
                )
            if body_only and rows:
                strategy_kind = (
                    _DECODE_STRATEGY_BODY_ONLY_SINGLE_FIELD
                    if len(rows) == 1
                    else _DECODE_STRATEGY_BODY_ONLY_MAPPING
                )
                strategy = (strategy_kind, tuple(rows))

        self._param_shape_decode_strategy_cache[cache_key] = strategy
        return strategy

    async def _prepare_compiled_input(
        self,
        ctx: _Ctx,
        hot: HotCtx,
        packed: PackedKernel,
        program_id: int,
        hot_op_plan: Any | None,
    ) -> None:
        param_shape_id = self._resolve_program_param_shape_id(
            packed, program_id, hot_op_plan
        )
        if hot.slot_values is not None and hot.param_shape_id == param_shape_id:
            return

        hot.param_shape_id = param_shape_id
        hot.transport_kind_id = self._resolve_program_transport_kind_id(
            packed, program_id, hot_op_plan
        )
        raw_scope = hot.raw_scope or {}
        if hot.raw_headers is None:
            hot.raw_headers = self._coerce_header_pairs(raw_scope)
        if not hot.content_type:
            hot.content_type = self._content_type_from_raw_headers(hot.raw_headers or ())
        if not hot.raw_query_string:
            query_string = raw_scope.get("query_string", b"")
            if isinstance(query_string, (bytes, bytearray)):
                hot.raw_query_string = bytes(query_string)
        if hot.path_params is None and hot.route_path_params is not None:
            hot.path_params = hot.route_path_params
        request = self._ensure_hot_request(ctx, hot)
        hot.transport_kind_id = self._active_transport_kind(hot, hot.transport_kind_id)
        if param_shape_id < 0:
            method = str(hot.method or "").upper()
            if method not in {"GET", "HEAD", "OPTIONS"}:
                body_bytes = await self._ensure_body_bytes(ctx, hot)
                if request is not None and body_bytes is not None and hasattr(request, "body"):
                    request.body = body_bytes
                if body_bytes and "json" in hot.content_type:
                    try:
                        parsed = json.loads(body_bytes)
                    except Exception:
                        parsed = None
                    hot.parsed_json = parsed
                    hot.parsed_json_loaded = True
                    if hot.transport_kind_id == _TRANSPORT_KIND_JSONRPC and isinstance(parsed, dict):
                        hot.route_rpc_envelope = parsed
                        params = parsed.get("params", {})
                        hot.route_payload = params if isinstance(params, dict) else None
                    elif isinstance(parsed, dict):
                        hot.route_payload = parsed
            return
        body_bytes = await self._ensure_body_bytes(ctx, hot)
        if request is not None and body_bytes is not None and hasattr(request, "body"):
            request.body = body_bytes
        if hot.transport_kind_id in {_TRANSPORT_KIND_REST, _TRANSPORT_KIND_JSONRPC}:
            if not hot.parsed_json_loaded:
                parsed = None
                if body_bytes and "json" in hot.content_type:
                    try:
                        parsed = json.loads(body_bytes)
                    except Exception:
                        parsed = None
                hot.parsed_json = parsed
                hot.parsed_json_loaded = True

        if hot.transport_kind_id == _TRANSPORT_KIND_JSONRPC and isinstance(hot.parsed_json, dict):
            rpc_envelope = hot.parsed_json
            hot.route_rpc_envelope = rpc_envelope
            hot.dispatch_rpc_envelope = rpc_envelope
            hot.dispatch_jsonrpc_request_id = rpc_envelope.get("id")
            method = rpc_envelope.get("method")
            hot.dispatch_rpc_method = method if isinstance(method, str) else None

        plan = self._resolve_compiled_param_plan(ctx, packed, program_id, param_shape_id)
        if not plan.descriptor_plans:
            return

        body_payload = hot.parsed_json
        if hot.transport_kind_id == _TRANSPORT_KIND_JSONRPC and isinstance(body_payload, dict):
            body_payload = body_payload.get("params", {})
        if hot.transport_kind_id == _TRANSPORT_KIND_JSONRPC:
            self._reject_jsonrpc_wrapper_keys(
                body_payload,
                field_names=plan.field_names,
            )
        body_mapping = body_payload if isinstance(body_payload, dict) else None
        if body_mapping is not None and plan.reserved_input_keys:
            reserved_body_keys = sorted(
                key for key in body_mapping if key in plan.reserved_input_keys
            )
            if reserved_body_keys:
                raise HTTPException(
                    status_code=_status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=[
                        {
                            "field": key,
                            "code": "extra_forbidden",
                            "message": "Field is not permitted in request input.",
                        }
                        for key in reserved_body_keys
                    ],
                )
        path_mapping = hot.route_path_params or hot.path_params
        field_names = plan.field_names
        slot_values: list[Any] = [None] * len(field_names)
        slot_present = bytearray(len(field_names))

        if (
            plan.strategy_kind == _DECODE_STRATEGY_BODY_ONLY_SINGLE_FIELD
            and body_mapping is not None
            and plan.strategy_rows
        ):
            hot.body_hashed_items = None
            hot.query_hashed_spans = None
            hot.header_hashed_pairs = None
            slot_id, lookup_name, decoder_id, max_length = plan.strategy_rows[0]
            value = body_mapping.get(lookup_name)
            if value is not None:
                try:
                    coerced = self._decode_scalar(value, decoder_id)
                except Exception:
                    coerced = value
                if max_length > 0 and isinstance(coerced, str) and len(coerced) > max_length:
                    coerced = coerced[:max_length]
                slot_values[slot_id] = coerced
                slot_present[slot_id] = 1
            self._publish_compiled_slots(
                hot, field_names, plan.field_index, slot_values, slot_present
            )
            return

        if (
            plan.strategy_kind == _DECODE_STRATEGY_BODY_ONLY_MAPPING
            and body_mapping is not None
            and plan.strategy_rows
        ):
            hot.body_hashed_items = None
            hot.query_hashed_spans = None
            hot.header_hashed_pairs = None
            for slot_id, lookup_name, decoder_id, max_length in plan.strategy_rows:
                value = body_mapping.get(lookup_name)
                if value is None:
                    continue
                try:
                    coerced = self._decode_scalar(value, decoder_id)
                except Exception:
                    coerced = value
                if max_length > 0 and isinstance(coerced, str) and len(coerced) > max_length:
                    coerced = coerced[:max_length]
                slot_values[slot_id] = coerced
                slot_present[slot_id] = 1
            self._publish_compiled_slots(
                hot, field_names, plan.field_index, slot_values, slot_present
            )
            return

        hot.body_hashed_items = None
        query_spans: tuple[tuple[int, int, int, int], ...] = ()
        if plan.needs_query:
            if hot.query_hashed_spans is None:
                hot.query_hashed_spans = self._parse_query_spans(hot.raw_query_string)
            query_spans = hot.query_hashed_spans
        else:
            hot.query_hashed_spans = None
        header_pairs: tuple[tuple[int, bytes], ...] = ()
        if plan.needs_header:
            raw_headers = hot.raw_headers or ()
            if hot.header_hashed_pairs is None:
                hot.header_hashed_pairs = self._header_hash_pairs(raw_headers)
            header_pairs = hot.header_hashed_pairs
        else:
            hot.header_hashed_pairs = None

        for row in plan.descriptor_plans:
            slot_id = row.slot_id
            value = None
            found = False
            if row.source_mask & _PARAM_SOURCE_BODY and body_mapping is not None:
                if row.lookup_name in body_mapping:
                    found, value = True, body_mapping[row.lookup_name]
            if not found and row.source_mask & _PARAM_SOURCE_PATH and path_mapping is not None:
                if row.lookup_name in path_mapping:
                    found, value = True, path_mapping[row.lookup_name]
            if not found and row.source_mask & _PARAM_SOURCE_QUERY:
                found, value = self._lookup_query_value(
                    hot.raw_query_string, query_spans, row.lookup_hash
                )
            if not found and row.source_mask & _PARAM_SOURCE_HEADER and row.header_hash:
                found, value = self._lookup_hashed_pairs(header_pairs, row.header_hash)
            if not found:
                continue
            try:
                coerced = self._decode_scalar(value, row.decoder_id)
            except Exception:
                coerced = value
            if row.max_length > 0 and isinstance(coerced, str) and len(coerced) > row.max_length:
                coerced = coerced[: row.max_length]
            slot_values[slot_id] = coerced
            slot_present[slot_id] = 1

        self._publish_compiled_slots(
            hot, field_names, plan.field_index, slot_values, slot_present
        )
