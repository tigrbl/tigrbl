from __future__ import annotations

from ._shared import *


class _PackedHotContextMixin:
    @staticmethod
    def _publish_compiled_payload(ctx: _Ctx, hot: HotCtx) -> None:
        field_names = tuple(getattr(hot, "slot_field_names", ()) or ())
        values = getattr(hot, "assembled_slot_values", None)
        present = getattr(hot, "assembled_slot_present", None)
        if not field_names or values is None or present is None:
            return
        payload = {
            field_names[idx]: values[idx]
            for idx in range(min(len(field_names), len(values), len(present)))
            if present[idx]
        }
        if not payload:
            return
        ctx["payload"] = payload
        ctx["in_data"] = payload
        ctx["data"] = payload

    @staticmethod
    def _publish_route_payload(ctx: _Ctx, hot: HotCtx) -> None:
        payload = getattr(hot, "route_payload", None)
        if not isinstance(payload, Mapping):
            return
        ctx["payload"] = dict(payload)
        ctx["in_data"] = dict(payload)
        ctx["data"] = dict(payload)

    def _resolve_segments_for_program(
        self, packed: PackedKernel, program_id: int
    ) -> tuple[tuple[int, ...], tuple[int, ...]]:
        cache_key = (id(packed), program_id)
        cached = self._program_segments_cache.get(cache_key)
        if cached is not None:
            return cached

        offsets_fallback = tuple(
            getattr(packed, "program_segment_ref_offsets", ())
            or getattr(packed, "op_segment_offsets", ())
            or ()
        )
        lengths_fallback = tuple(
            getattr(packed, "program_segment_ref_lengths", ())
            or getattr(packed, "op_segment_lengths", ())
            or ()
        )
        refs_fallback = tuple(
            getattr(packed, "program_segment_refs", ())
            or getattr(packed, "op_to_segment_ids", ())
            or ()
        )
        segment_phases = self._segment_phase_names(packed)
        seg_offset = self._hot_int_at(
            packed,
            "program_segment_offsets",
            program_id,
            offsets_fallback,
        )
        seg_length = self._hot_int_at(
            packed,
            "program_segment_lengths",
            program_id,
            lengths_fallback,
        )
        if seg_offset is None or seg_length is None:
            resolved = ((), ())
            self._program_segments_cache[cache_key] = resolved
            return resolved
        ordered_segments: list[int] = []
        by_phase: dict[str, list[int]] = {}
        remaining: list[int] = []
        seen_segment_ids: set[int] = set()
        for i in range(int(seg_offset), int(seg_offset) + int(seg_length)):
            seg_id = self._hot_int_at(
                packed,
                "program_segment_refs",
                i,
                refs_fallback,
            )
            if seg_id is None:
                continue
            phase = str(normalize_phase(segment_phases[seg_id]))
            if phase.startswith("ON_") or phase == "TX_ROLLBACK":
                continue
            by_phase.setdefault(phase, []).append(seg_id)

        for phase in self._PHASE_EXECUTION_ORDER:
            for seg_id in by_phase.pop(phase, ()):  # pragma: no branch
                if seg_id in seen_segment_ids:
                    continue
                seen_segment_ids.add(seg_id)
                ordered_segments.append(seg_id)

        for i in range(int(seg_offset), int(seg_offset) + int(seg_length)):
            seg_id = self._hot_int_at(
                packed,
                "program_segment_refs",
                i,
                refs_fallback,
            )
            if seg_id is None:
                continue
            if seg_id in seen_segment_ids:
                continue
            phase = str(segment_phases[seg_id])
            phase = str(normalize_phase(phase))
            if phase.startswith("ON_") or phase == "TX_ROLLBACK":
                continue
            seen_segment_ids.add(seg_id)
            remaining.append(seg_id)

        resolved = (tuple(ordered_segments), tuple(remaining))
        self._program_segments_cache[cache_key] = resolved
        return resolved

    @staticmethod
    def _coerce_int(value: Any) -> int | None:
        return value if isinstance(value, int) else None

    @staticmethod
    def _coerce_dict(value: Any) -> dict[str, Any] | None:
        if isinstance(value, dict):
            return value
        if isinstance(value, Mapping):
            return dict(value)
        return None

    @classmethod
    def _sync_hot_from_temp(cls, temp: dict[str, Any], hot: HotCtx) -> None:
        route = dict.get(temp, "route")
        if isinstance(route, dict):
            if "selector" in route and isinstance(route.get("selector"), str):
                hot.route_selector = str(route.get("selector"))
            if "protocol" in route and isinstance(route.get("protocol"), str):
                hot.route_protocol = str(route.get("protocol"))
            if "program_id" in route:
                program_id = cls._coerce_int(route.get("program_id"))
                if program_id is not None:
                    hot.route_program_id = program_id
                    hot.program_id = program_id
            if "opmeta_index" in route:
                opmeta_index = cls._coerce_int(route.get("opmeta_index"))
                if opmeta_index is not None:
                    hot.route_opmeta_index = opmeta_index
                    if hot.route_program_id < 0:
                        hot.route_program_id = opmeta_index
                    if hot.program_id < 0:
                        hot.program_id = opmeta_index
            if "method_not_allowed" in route:
                hot.route_method_not_allowed = bool(route.get("method_not_allowed"))
            if "short_circuit" in route:
                hot.route_short_circuit = bool(route.get("short_circuit"))
            if "payload" in route:
                hot.route_payload = cls._coerce_dict(route.get("payload"))
            if "path_params" in route:
                path_params = cls._coerce_dict(route.get("path_params"))
                hot.route_path_params = path_params
                hot.path_params = path_params
            if "rpc_envelope" in route:
                route_rpc_envelope = cls._coerce_dict(route.get("rpc_envelope"))
                hot.route_rpc_envelope = route_rpc_envelope
                if route_rpc_envelope is not None:
                    hot.dispatch_jsonrpc_request_id = route_rpc_envelope.get("id")
                    method = route_rpc_envelope.get("method")
                    hot.dispatch_rpc_method = method if isinstance(method, str) else None

        dispatch = dict.get(temp, "dispatch")
        if isinstance(dispatch, dict):
            if "binding_protocol" in dispatch and isinstance(
                dispatch.get("binding_protocol"), str
            ):
                hot.dispatch_binding_protocol = str(dispatch.get("binding_protocol"))
            if "binding_selector" in dispatch and isinstance(
                dispatch.get("binding_selector"), str
            ):
                hot.dispatch_binding_selector = str(dispatch.get("binding_selector"))
            if "channel_protocol" in dispatch and isinstance(
                dispatch.get("channel_protocol"), str
            ):
                hot.dispatch_channel_protocol = str(dispatch.get("channel_protocol"))
            if "channel_selector" in dispatch and isinstance(
                dispatch.get("channel_selector"), str
            ):
                hot.dispatch_channel_selector = str(dispatch.get("channel_selector"))
            if "rpc" in dispatch:
                dispatch_rpc_envelope = cls._coerce_dict(dispatch.get("rpc"))
                hot.dispatch_rpc_envelope = dispatch_rpc_envelope
                if dispatch_rpc_envelope is not None:
                    hot.dispatch_jsonrpc_request_id = dispatch_rpc_envelope.get("id")
                    method = dispatch_rpc_envelope.get("method")
                    hot.dispatch_rpc_method = method if isinstance(method, str) else None
            if "rpc_method" in dispatch and isinstance(dispatch.get("rpc_method"), str):
                hot.dispatch_rpc_method = str(dispatch.get("rpc_method"))
            if "normalized_input" in dispatch or "parsed_payload" in dispatch:
                hot.route_payload = cls._coerce_dict(
                    dispatch.get("normalized_input", dispatch.get("parsed_payload"))
                )

        egress = dict.get(temp, "egress")
        if isinstance(egress, dict):
            if "transport_response" in egress:
                hot.egress_transport_response = cls._coerce_dict(
                    egress.get("transport_response")
                )
            if "sent" in egress:
                hot.egress_sent = bool(egress.get("sent"))

        if "jsonrpc_request_id" in temp:
            hot.dispatch_jsonrpc_request_id = dict.get(temp, "jsonrpc_request_id")

    @classmethod
    def _ensure_hot_ctx(cls, ctx: _Ctx, env: Any) -> HotCtx:
        temp = object.__getattribute__(ctx, "temp")
        if not isinstance(temp, dict):
            ctx.temp = {}
            temp = ctx.temp
        hot = temp.get("hot_ctx")
        if isinstance(hot, HotCtx):
            return hot

        scope = getattr(env, "scope", {}) or {}
        scope_dict = cls._coerce_dict(scope) or {}
        method = str(scope_dict.get("method") or "").upper()
        path = str(scope_dict.get("path") or "")
        scheme = str(scope_dict.get("scheme") or "").lower()
        scope_type = str(scope_dict.get("type") or "")
        protocol = ""
        selector = ""
        if scope_type == "http" and method and path:
            protocol = "https.rest" if scheme == "https" else "http.rest"
            selector = f"{method} {path}"
        elif scope_type in {"websocket", "webtransport"} and path:
            protocol = scheme or scope_type
            selector = path
        path_params = cls._coerce_dict(scope_dict.get("path_params"))
        raw_query_string = scope_dict.get("query_string", b"")

        hot = HotCtx(
            scope_type=scope_type,
            method=method,
            path=path,
            protocol=protocol,
            selector=selector,
            route_protocol=protocol,
            route_selector=selector,
            dispatch_binding_protocol=protocol,
            dispatch_binding_selector=selector,
            dispatch_channel_protocol=protocol if scope_type in {"websocket", "webtransport"} else "",
            dispatch_channel_selector=selector if scope_type in {"websocket", "webtransport"} else "",
            content_type="",
            raw_scope=scope_dict or None,
            raw_receive=getattr(env, "receive", None),
            raw_send=getattr(env, "send", None),
            raw_headers=cls._coerce_header_pairs(scope_dict or None),
            raw_query_string=bytes(raw_query_string)
            if isinstance(raw_query_string, (bytes, bytearray))
            else b"",
            path_params=path_params,
            route_path_params=path_params,
        )
        cls._sync_hot_from_temp(temp, hot)
        temp["hot_ctx"] = hot
        return hot

    @staticmethod
    def _coerce_model_column_keys(obj: Any) -> tuple[str, ...] | None:
        table = getattr(obj, "__table__", None)
        columns = getattr(table, "columns", None)
        if columns is None:
            return None
        out: list[str] = []
        for col in columns:
            key = getattr(col, "key", None)
            if isinstance(key, str) and key:
                out.append(key)
        return tuple(out)

    def _serialize_model_row(self, obj: Any) -> Any:
        if obj is None or isinstance(obj, Mapping):
            return obj
        model_type = type(obj)
        serializer = self._model_row_serializer_cache.get(model_type)
        if serializer is None:
            keys = self._coerce_model_column_keys(obj)
            if keys is None:
                return obj
            getter = attrgetter(*keys)
            serializer = (keys, getter)
            self._model_row_serializer_cache[model_type] = serializer
        keys, getter = serializer
        if not keys:
            return obj
        values = getter(obj)
        if len(keys) == 1:
            values = (values,)
        return dict(zip(keys, values))
