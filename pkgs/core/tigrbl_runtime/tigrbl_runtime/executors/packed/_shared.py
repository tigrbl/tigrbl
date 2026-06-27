from __future__ import annotations

import asyncio
from collections.abc import Mapping
from dataclasses import dataclass, fields, is_dataclass
import inspect
import json
from importlib import import_module
from typing import Any, ClassVar
from operator import attrgetter
from types import SimpleNamespace

from tigrbl_atoms._ctx import _ctx_view
from tigrbl_core.config.constants import __JSONRPC_DEFAULT_ENDPOINT_MAPPINGS__
from tigrbl_atoms.types import build_error_ctx, error_phase_for, select_error_edge
from tigrbl_atoms.atoms.wire.validate_in import _coerce_if_needed
from tigrbl_atoms.atoms.transport.websocket_unary import (
    DirectWebSocketUnary as _DirectWebSocketUnary,
)
from tigrbl_atoms.packed_inputs import (
    DECODER_BOOL as _DECODER_BOOL,
    DECODER_DATE as _DECODER_DATE,
    DECODER_DATETIME as _DECODER_DATETIME,
    DECODER_DECIMAL as _DECODER_DECIMAL,
    DECODER_FLOAT as _DECODER_FLOAT,
    DECODER_INT as _DECODER_INT,
    DECODER_NONE as _DECODER_NONE,
    DECODER_STR as _DECODER_STR,
    DECODER_TIME as _DECODER_TIME,
    DECODER_UUID as _DECODER_UUID,
    DECODE_STRATEGY_BODY_ONLY_MAPPING as _DECODE_STRATEGY_BODY_ONLY_MAPPING,
    DECODE_STRATEGY_BODY_ONLY_SINGLE_FIELD as _DECODE_STRATEGY_BODY_ONLY_SINGLE_FIELD,
    DECODE_STRATEGY_GENERIC_HASHED as _DECODE_STRATEGY_GENERIC_HASHED,
    PARAM_SOURCE_BODY as _PARAM_SOURCE_BODY,
    PARAM_SOURCE_HEADER as _PARAM_SOURCE_HEADER,
    PARAM_SOURCE_PATH as _PARAM_SOURCE_PATH,
    PARAM_SOURCE_QUERY as _PARAM_SOURCE_QUERY,
    QUERY_VALUE_HAS_PERCENT as _QUERY_VALUE_HAS_PERCENT,
    QUERY_VALUE_HAS_PLUS as _QUERY_VALUE_HAS_PLUS,
    body_hash_items as _atom_body_hash_items,
    coerce_header_pairs as _atom_coerce_header_pairs,
    compiled_lookup_name as _atom_compiled_lookup_name,
    content_type_from_raw_headers as _atom_content_type_from_raw_headers,
    decode_query_span_value as _atom_decode_query_span_value,
    decode_scalar as _atom_decode_scalar,
    ensure_body_bytes as _atom_ensure_body_bytes,
    header_hash_pairs as _atom_header_hash_pairs,
    lookup_hashed_mapping as _atom_lookup_hashed_mapping,
    lookup_hashed_pairs as _atom_lookup_hashed_pairs,
    lookup_query_value as _atom_lookup_query_value,
    parse_query_spans as _atom_parse_query_spans,
    path_hash_items as _atom_path_hash_items,
    publish_compiled_slots as _atom_publish_compiled_slots,
)
from tigrbl_kernel.models import (
    KernelPlan,
    OpKey,
    PackedHotSection,
    PackedHotSectionDirectory,
    PackedKernel,
)
from tigrbl_kernel.packed_access import (
    DIRECT_INVOKE_RUN as _DIRECT_INVOKE_RUN,
    DIRECT_INVOKE_RUN_WITH_DEP as _DIRECT_INVOKE_RUN_WITH_DEP,
    DIRECT_INVOKE_RUN_WITH_NONE as _DIRECT_INVOKE_RUN_WITH_NONE,
    DIRECT_INVOKE_STEP as _DIRECT_INVOKE_STEP,
    HOT_RUNNER_COMPILED_PARAM as _HOT_RUNNER_COMPILED_PARAM,
    HOT_RUNNER_GENERIC as _HOT_RUNNER_GENERIC,
    HOT_RUNNER_LINEAR_DIRECT as _HOT_RUNNER_LINEAR_DIRECT,
    HOT_RUNNER_WS_UNARY_TEXT as _HOT_RUNNER_WS_UNARY_TEXT,
    HTTP_METHOD_ID_BY_NAME as _HTTP_METHOD_ID_BY_NAME,
    TRANSPORT_KIND_CHANNEL as _TRANSPORT_KIND_CHANNEL,
    TRANSPORT_KIND_GENERIC as _TRANSPORT_KIND_GENERIC,
    TRANSPORT_KIND_JSONRPC as _TRANSPORT_KIND_JSONRPC,
    TRANSPORT_KIND_REST as _TRANSPORT_KIND_REST,
    hot_array as _kernel_hot_array,
    hot_block_sections as _kernel_hot_block_sections,
    hot_block_view as _kernel_hot_block_view,
    hot_count as _kernel_hot_count,
    hot_int_at as _kernel_hot_int_at,
    hot_section as _kernel_hot_section,
    http_method_id as _kernel_http_method_id,
    resolve_program_hot_runner_id as _kernel_resolve_program_hot_runner_id,
    stable_name_hash64 as _kernel_stable_name_hash64,
)
from tigrbl_kernel.packed_selectors import (
    normalize_jsonrpc_mount_path as _kernel_normalize_jsonrpc_mount_path,
    resolve_hot_exact_jsonrpc_routes as _kernel_resolve_hot_exact_jsonrpc_routes,
    resolve_hot_exact_route_slices as _kernel_resolve_hot_exact_route_slices,
    resolve_hot_exact_route_verify as _kernel_resolve_hot_exact_route_verify,
    resolve_hot_exact_websocket_routes as _kernel_resolve_hot_exact_websocket_routes,
    resolve_program_id_from_exact_route as _kernel_resolve_program_id_from_exact_route,
    resolve_program_id_from_exact_websocket as _kernel_resolve_program_id_from_exact_websocket,
)
from tigrbl_typing.status.exceptions import HTTPException
from tigrbl_typing.phases import canonicalize_phase_input as normalize_phase
from tigrbl_typing.status.mappings import status as _status
from tigrbl_atoms._request import Request

from ..base import ExecutorBase
from ..types import HotCtx, _Ctx

_WRAPPER_KEYS = frozenset({"data", "payload", "body", "item"})
_COMPAT_CONSTANTS = (
    _DECODER_BOOL,
    _DECODER_DATE,
    _DECODER_DATETIME,
    _DECODER_DECIMAL,
    _DECODER_FLOAT,
    _DECODER_INT,
    _DECODER_NONE,
    _DECODER_STR,
    _DECODER_TIME,
    _DECODER_UUID,
    _QUERY_VALUE_HAS_PERCENT,
    _QUERY_VALUE_HAS_PLUS,
    _HTTP_METHOD_ID_BY_NAME,
)


@dataclass(frozen=True, slots=True)
class _CompiledInputDescriptor:
    slot_id: int
    lookup_name: str
    source_mask: int
    decoder_id: int
    max_length: int
    lookup_hash: int
    header_hash: int


@dataclass(frozen=True, slots=True)
class _CompiledFieldPlan:
    slot_id: int
    field_name: str
    required: bool
    nullable: bool | None
    py_type: Any
    coerce: bool
    max_length: int
    validator: Any
    in_enabled: bool
    is_virtual: bool
    default_factory: Any


@dataclass(frozen=True, slots=True)
class _CompiledParamPlan:
    field_names: tuple[str, ...]
    field_index: Mapping[str, int]
    field_plans: tuple[_CompiledFieldPlan, ...]
    descriptor_plans: tuple[_CompiledInputDescriptor, ...]
    strategy_kind: int
    strategy_rows: tuple[tuple[int, str, int, int], ...]
    assemble_order: tuple[int, ...]
    body_lookup_names: frozenset[str]
    reserved_input_keys: frozenset[str]
    needs_query: bool
    needs_header: bool
    needs_path: bool


__all__ = [
    name
    for name in globals()
    if not name.startswith("__") or name == "__JSONRPC_DEFAULT_ENDPOINT_MAPPINGS__"
]


