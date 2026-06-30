from __future__ import annotations

from ._shared import *


class _PackedHotAccessMixin:
    @staticmethod
    def _hot_block_view(packed: PackedKernel) -> Mapping[str, Any]:
        return _kernel_hot_block_view(packed)

    @staticmethod
    def _hot_block_sections(packed: PackedKernel) -> PackedHotSectionDirectory | None:
        return _kernel_hot_block_sections(packed)

    @classmethod
    def _hot_section(cls, packed: PackedKernel, key: str) -> PackedHotSection | None:
        return _kernel_hot_section(packed, key)

    @classmethod
    def _hot_array(cls, packed: PackedKernel, key: str, fallback: tuple[Any, ...] | tuple[int, ...] | tuple[str, ...]) -> tuple[Any, ...]:
        return _kernel_hot_array(packed, key, fallback)

    @classmethod
    def _hot_int_at(
        cls,
        packed: PackedKernel,
        key: str,
        index: int,
        fallback: tuple[int, ...] | tuple[Any, ...],
    ) -> int | None:
        return _kernel_hot_int_at(packed, key, index, fallback)

    @classmethod
    def _hot_count(
        cls,
        packed: PackedKernel,
        key: str,
        fallback: tuple[int, ...] | tuple[Any, ...] | tuple[str, ...],
    ) -> int:
        return _kernel_hot_count(packed, key, fallback)

    @staticmethod
    def _stable_name_hash64(value: str, *, lowercase: bool = False) -> int:
        return _kernel_stable_name_hash64(value, lowercase=lowercase)

    @classmethod
    def _http_method_id(cls, method: str) -> int:
        return _kernel_http_method_id(method)

    @staticmethod
    def _coerce_header_pairs(
        raw_scope: Mapping[str, Any] | None,
    ) -> tuple[tuple[bytes, bytes], ...]:
        return _atom_coerce_header_pairs(raw_scope)

    @staticmethod
    def _content_type_from_raw_headers(raw_headers: tuple[tuple[bytes, bytes], ...]) -> str:
        return _atom_content_type_from_raw_headers(raw_headers)

    @staticmethod
    def _decode_scalar(value: Any, decoder_id: int) -> Any:
        return _atom_decode_scalar(value, decoder_id)

    @staticmethod
    def _parse_query_spans(raw_query: bytes) -> tuple[tuple[int, int, int, int], ...]:
        return _atom_parse_query_spans(
            raw_query,
            name_hash=_PackedHotAccessMixin._stable_name_hash64,
        )

    @staticmethod
    def _decode_query_span_value(
        raw_query: bytes, start: int, end: int, flags: int
    ) -> str:
        return _atom_decode_query_span_value(raw_query, start, end, flags)

    @classmethod
    def _ensure_hot_request(cls, ctx: _Ctx, hot: HotCtx) -> Request | Any | None:
        request = getattr(ctx, "request", None)
        if request is not None:
            return request
        raw_scope = hot.raw_scope
        if not isinstance(raw_scope, Mapping):
            return None
        request = Request(dict(raw_scope), app=getattr(ctx, "app", None))
        if hot.body_bytes is not None:
            request.body = hot.body_bytes
        ctx.request = request
        return request

    @staticmethod
    async def _ensure_body_bytes(ctx: _Ctx, hot: HotCtx) -> bytes:
        return await _atom_ensure_body_bytes(ctx, hot)

    @classmethod
    def _body_hash_items(cls, body: Any) -> Mapping[int, Any]:
        return _atom_body_hash_items(body, name_hash=cls._stable_name_hash64)

    @classmethod
    def _header_hash_pairs(
        cls, raw_headers: tuple[tuple[bytes, bytes], ...]
    ) -> tuple[tuple[int, bytes], ...]:
        return _atom_header_hash_pairs(
            raw_headers,
            name_hash=lambda value: cls._stable_name_hash64(value, lowercase=True),
        )

    @classmethod
    def _path_hash_items(cls, path_params: Mapping[str, Any] | None) -> Mapping[int, Any]:
        return _atom_path_hash_items(path_params, name_hash=cls._stable_name_hash64)

    @classmethod
    def _lookup_query_value(
        cls,
        raw_query: bytes,
        query_spans: tuple[tuple[int, int, int, int], ...],
        target_hash: int,
    ) -> tuple[bool, Any]:
        return _atom_lookup_query_value(raw_query, query_spans, target_hash)

    @staticmethod
    def _lookup_hashed_mapping(
        items: Mapping[int, Any], target_hash: int
    ) -> tuple[bool, Any]:
        return _atom_lookup_hashed_mapping(items, target_hash)

    @staticmethod
    def _lookup_hashed_pairs(
        items: tuple[tuple[int, bytes], ...], target_hash: int
    ) -> tuple[bool, Any]:
        return _atom_lookup_hashed_pairs(items, target_hash)

    @classmethod
    def _param_shape_descriptor_slice(
        cls,
        packed: PackedKernel,
        param_shape_id: int,
    ) -> tuple[int, int]:
        offsets_fallback = tuple(getattr(packed, "param_shape_offsets", ()) or ())
        lengths_fallback = tuple(getattr(packed, "param_shape_lengths", ()) or ())
        if not (0 <= param_shape_id < cls._hot_count(packed, "param_shape_offsets", offsets_fallback)):
            return (0, 0)
        offset = cls._hot_int_at(
            packed,
            "param_shape_offsets",
            param_shape_id,
            offsets_fallback,
        )
        length = cls._hot_int_at(
            packed,
            "param_shape_lengths",
            param_shape_id,
            lengths_fallback,
        )
        return int(offset or 0), int(length or 0)

    @classmethod
    def _segment_phase_names(cls, packed: PackedKernel) -> tuple[str, ...]:
        phase_names = tuple(getattr(packed, "phase_names", ()) or ())
        phase_ids = cls._hot_array(
            packed,
            "segment_phase_ids",
            tuple(getattr(packed, "segment_catalog_phase_ids", ()) or ()),
        )
        if phase_names and phase_ids:
            return tuple(
                str(phase_names[int(phase_id)]) if 0 <= int(phase_id) < len(phase_names) else str(phase_id)
                for phase_id in phase_ids
        )
        return tuple(getattr(packed, "segment_phases", ()) or ())

    @classmethod
    def _resolve_program_param_shape_id(
        cls, packed: PackedKernel, program_id: int, hot_op_plan: Any | None
    ) -> int:
        if hot_op_plan is not None:
            plan_value = cls._coerce_int(getattr(hot_op_plan, "param_shape_id", None))
            if plan_value is not None:
                return plan_value
        fallback = tuple(getattr(packed, "program_param_shape_ids", ()) or ())
        value = cls._hot_int_at(
            packed,
            "program_param_shape_ids",
            program_id,
            fallback,
        )
        return int(value) if value is not None else -1

    @classmethod
    def _resolve_program_transport_kind_id(
        cls, packed: PackedKernel, program_id: int, hot_op_plan: Any | None
    ) -> int:
        if hot_op_plan is not None:
            plan_value = cls._coerce_int(
                getattr(hot_op_plan, "transport_kind_id", None)
            )
            if plan_value is not None:
                return plan_value
        fallback = tuple(getattr(packed, "program_transport_kind_ids", ()) or ())
        value = cls._hot_int_at(
            packed,
            "program_transport_kind_ids",
            program_id,
            fallback,
        )
        return int(value) if value is not None else _TRANSPORT_KIND_GENERIC

    @staticmethod
    def _active_transport_kind(hot: HotCtx, fallback: int) -> int:
        protocol = str(
            hot.dispatch_binding_protocol or hot.route_protocol or hot.protocol or ""
        )
        if protocol.endswith(".jsonrpc"):
            return _TRANSPORT_KIND_JSONRPC
        if protocol.endswith(".rest"):
            return _TRANSPORT_KIND_REST
        if protocol in {"ws", "wss", "webtransport"} or hot.scope_type in {
            "websocket",
            "webtransport",
        }:
            return _TRANSPORT_KIND_CHANNEL
        return fallback
