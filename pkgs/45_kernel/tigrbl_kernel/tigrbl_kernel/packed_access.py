from __future__ import annotations

from collections.abc import Mapping
from typing import Any
import zlib

from .models import PackedHotSection, PackedHotSectionDirectory, PackedKernel

HOT_RUNNER_GENERIC = 0
HOT_RUNNER_LINEAR_DIRECT = 1
HOT_RUNNER_COMPILED_PARAM = 2
HOT_RUNNER_WS_UNARY_TEXT = 3

DIRECT_INVOKE_STEP = 0
DIRECT_INVOKE_RUN = 1
DIRECT_INVOKE_RUN_WITH_NONE = 2
DIRECT_INVOKE_RUN_WITH_DEP = 3

TRANSPORT_KIND_GENERIC = 0
TRANSPORT_KIND_REST = 1
TRANSPORT_KIND_JSONRPC = 2
TRANSPORT_KIND_CHANNEL = 3

HTTP_METHOD_ID_BY_NAME = {
    "GET": 1,
    "HEAD": 2,
    "POST": 3,
    "PUT": 4,
    "PATCH": 5,
    "DELETE": 6,
    "OPTIONS": 7,
    "TRACE": 8,
    "CONNECT": 9,
}


def hot_block_view(packed: PackedKernel) -> Mapping[str, Any]:
    view = getattr(packed, "hot_block_view", None)
    return view if isinstance(view, Mapping) else {}


def hot_block_sections(packed: PackedKernel) -> PackedHotSectionDirectory | None:
    sections = getattr(packed, "hot_block_sections", None)
    return sections if isinstance(sections, PackedHotSectionDirectory) else None


def hot_section(packed: PackedKernel, key: str) -> PackedHotSection | None:
    directory = hot_block_sections(packed)
    if directory is None:
        return None
    return directory.get(key)


def hot_array(
    packed: PackedKernel,
    key: str,
    fallback: tuple[Any, ...] | tuple[int, ...] | tuple[str, ...],
) -> tuple[Any, ...]:
    values = hot_block_view(packed).get(key)
    if isinstance(values, tuple):
        return values
    if isinstance(values, list):
        return tuple(values)
    return fallback


def hot_int_at(
    packed: PackedKernel,
    key: str,
    index: int,
    fallback: tuple[int, ...] | tuple[Any, ...],
) -> int | None:
    section = hot_section(packed, key)
    if section is not None:
        if 0 <= index < int(section.count):
            return section.get_int(index)
        return None
    if 0 <= index < len(fallback):
        return int(fallback[index])
    return None


def hot_count(
    packed: PackedKernel,
    key: str,
    fallback: tuple[int, ...] | tuple[Any, ...] | tuple[str, ...],
) -> int:
    section = hot_section(packed, key)
    if section is not None:
        return int(section.count)
    return len(fallback)


def stable_name_hash64(value: str, *, lowercase: bool = False) -> int:
    normalized = value.lower() if lowercase else value
    encoded = normalized.encode("utf-8")
    lo = zlib.crc32(encoded) & 0xFFFFFFFF
    hi = zlib.crc32(encoded, 0x9E3779B9) & 0xFFFFFFFF
    return (hi << 32) | lo


def http_method_id(method: str) -> int:
    normalized = str(method or "").upper()
    cached = HTTP_METHOD_ID_BY_NAME.get(normalized)
    if cached is not None:
        return cached
    return 1024 + (stable_name_hash64(normalized) & 0xFFFF)


def coerce_int(value: Any) -> int | None:
    return value if isinstance(value, int) else None


def coerce_dict(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def resolve_program_hot_runner_id(
    packed: PackedKernel,
    program_id: int,
    hot_op_plan: Any | None,
) -> int:
    if hot_op_plan is not None:
        program_hot_runner_id = coerce_int(
            getattr(hot_op_plan, "program_hot_runner_id", None)
        )
        if program_hot_runner_id is not None:
            return program_hot_runner_id
    fallback = tuple(getattr(packed, "program_hot_runner_ids", ()) or ())
    value = hot_int_at(packed, "program_hot_runner_ids", program_id, fallback)
    return int(value) if value is not None else HOT_RUNNER_GENERIC
