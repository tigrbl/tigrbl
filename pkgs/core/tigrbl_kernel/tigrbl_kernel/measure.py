from __future__ import annotations

import gzip
import hashlib
import json
import struct
from typing import Any, Mapping

from tigrbl_typing.phases import normalize_phase

from .models import HotOpPlan, PackedKernel, PackedKernelMeasurement

_BINDER_TOKEN = "SYS_PHASE_DB_BIND"
_EXECUTOR_KIND_IDS = {
    "sync.extractable": 1,
    "sync_extractable": 1,
    "split.extractable": 2,
    "split_extractable": 2,
    "async.direct": 3,
    "async_direct": 3,
}

_HOT_BLOCK_MAGIC = b"TGPKHOT1"
_HOT_BLOCK_VERSION = 1
_HOT_BLOCK_SECTION_IDS = {
    "atom_opcode_ids": 1,
    "atom_effect_ids": 2,
    "atom_payload_offsets": 3,
    "atom_payload_lengths": 4,
    "atom_payload_values": 5,
    "atom_flags": 6,
    "prelude_atom_ids": 7,
    "segment_executor_kind_ids": 8,
    "segment_phase_ids": 9,
    "segment_step_offsets": 10,
    "segment_step_lengths": 11,
    "segment_step_atom_refs": 12,
    "program_segment_offsets": 13,
    "program_segment_lengths": 14,
    "program_segment_refs": 15,
    "program_hot_runner_ids": 16,
    "error_profile_offsets": 17,
    "error_profile_lengths": 18,
    "error_profile_phase_ids": 19,
    "error_profile_segment_offsets": 20,
    "error_profile_segment_lengths": 21,
    "error_profile_segment_refs": 22,
    "program_error_profile_ids": 23,
    "route_proto_ids": 24,
    "route_selector_ids": 25,
    "route_program_ids": 26,
    "exact_method_ids": 27,
    "exact_path_hashes": 28,
    "exact_program_ids": 29,
}
_HOT_BLOCK_SECTION_NAMES = {
    section_id: name for name, section_id in _HOT_BLOCK_SECTION_IDS.items()
}


def _freeze_mapping(mapping: Mapping[str, Any]) -> dict[str, Any]:
    return {str(key): _freeze_value(value) for key, value in sorted(mapping.items())}


def _freeze_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return _freeze_mapping(value)
    if isinstance(value, tuple):
        return [_freeze_value(item) for item in value]
    if isinstance(value, list):
        return [_freeze_value(item) for item in value]
    if isinstance(value, set):
        return sorted(_freeze_value(item) for item in value)
    return value


def _phase_kind_id(phase: str) -> int:
    normalized = str(normalize_phase(phase))
    if normalized == "TX_ROLLBACK":
        return 2
    if normalized.startswith("ON_"):
        return 1
    return 0


def _stable_hash64(value: str) -> int:
    digest = hashlib.blake2b(value.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, "little", signed=False)


def _uses_u16(values: list[int]) -> bool:
    if not values:
        return True
    return max(values) <= 0xFFFF


def _pack_u16(values: list[int]) -> bytes:
    if not values:
        return b""
    return struct.pack(f"<{len(values)}H", *values)


def _pack_u32(values: list[int]) -> bytes:
    if not values:
        return b""
    return struct.pack(f"<{len(values)}I", *values)


def _pack_u64(values: list[int]) -> bytes:
    if not values:
        return b""
    return struct.pack(f"<{len(values)}Q", *values)


def _pack_i32(values: list[int]) -> bytes:
    if not values:
        return b""
    return struct.pack(f"<{len(values)}i", *values)


def _pack_i16(values: list[int]) -> bytes:
    if not values:
        return b""
    return struct.pack(f"<{len(values)}h", *values)


def _pack_i8(values: list[int]) -> bytes:
    if not values:
        return b""
    return struct.pack(f"<{len(values)}b", *values)


def _pack_u8(values: list[int]) -> bytes:
    if not values:
        return b""
    return bytes(values)


def _pack_index_array(values: list[int]) -> tuple[int, bytes]:
    if _uses_u16(values):
        return 16, _pack_u16(values)
    return 32, _pack_u32(values)


def _pack_unsigned_array(values: list[int]) -> tuple[int, bytes]:
    if not values:
        return 8, b""
    maximum = max(int(value) for value in values)
    if maximum <= 0xFF:
        return 8, _pack_u8(values)
    if maximum <= 0xFFFF:
        return 16, _pack_u16(values)
    return 32, _pack_u32(values)


def _pack_signed_array(values: list[int]) -> tuple[int, bytes]:
    if not values:
        return 8, b""
    minimum = min(int(value) for value in values)
    maximum = max(int(value) for value in values)
    if -128 <= minimum and maximum <= 127:
        return 8, _pack_i8(values)
    if -32768 <= minimum and maximum <= 32767:
        return 16, _pack_i16(values)
    return 32, _pack_i32(values)


def _unpack_unsigned_array(width_bits: int, payload: bytes, count: int) -> tuple[int, ...]:
    if count <= 0:
        return ()
    if width_bits == 8:
        return tuple(payload[:count])
    if width_bits == 16:
        return tuple(struct.unpack(f"<{count}H", payload))
    if width_bits == 32:
        return tuple(struct.unpack(f"<{count}I", payload))
    if width_bits == 64:
        return tuple(struct.unpack(f"<{count}Q", payload))
    raise ValueError(f"unsupported unsigned width: {width_bits}")


def _unpack_signed_array(width_bits: int, payload: bytes, count: int) -> tuple[int, ...]:
    if count <= 0:
        return ()
    if width_bits == 8:
        return tuple(struct.unpack(f"<{count}b", payload))
    if width_bits == 16:
        return tuple(struct.unpack(f"<{count}h", payload))
    if width_bits == 32:
        return tuple(struct.unpack(f"<{count}i", payload))
    raise ValueError(f"unsupported signed width: {width_bits}")


def _pack_section(section_id: int, payload: bytes) -> bytes:
    return struct.pack("<BI", int(section_id), len(payload)) + payload


def _segment_step_ids(packed: PackedKernel, seg_id: int) -> tuple[int, ...]:
    offsets = (
        getattr(packed, "segment_catalog_offsets", ()) or getattr(packed, "segment_offsets", ()) or ()
    )
    lengths = (
        getattr(packed, "segment_catalog_lengths", ()) or getattr(packed, "segment_lengths", ()) or ()
    )
    step_ids = (
        getattr(packed, "segment_catalog_atom_ids", ()) or getattr(packed, "segment_step_ids", ()) or ()
    )
    offset = int(offsets[seg_id])
    length = int(lengths[seg_id])
    return tuple(int(step_ids[offset + idx]) for idx in range(length))


def _build_compact_image_parts(packed: PackedKernel) -> dict[str, Any]:
    step_labels = tuple(
        str(label)
        for label in (
            getattr(packed, "atom_catalog_labels", ())
            or getattr(packed, "step_labels", ())
            or ()
        )
    )
    opcode_ids = [
        int(value)
        for value in (getattr(packed, "atom_catalog_opcode_ids", ()) or ())
    ]
    effect_ids = [
        int(value)
        for value in (
            getattr(packed, "atom_catalog_effect_ids", ())
            or getattr(packed, "numba_effect_ids", ())
            or ()
        )
    ]
    effect_payloads = [
        tuple(int(item) for item in payload)
        for payload in (
            getattr(packed, "atom_catalog_effect_payloads", ())
            or getattr(packed, "numba_effect_payloads", ())
            or ()
        )
    ]
    step_async_flags = [
        1 if bool(flag) else 0
        for flag in (
            getattr(packed, "atom_catalog_async_flags", ())
            or getattr(packed, "step_async_flags", ())
            or ()
        )
    ]

    semantic_step_index: dict[tuple[Any, ...], int] = {}
    compact_step_opcode_ids: list[int] = []
    compact_step_effect_ids: list[int] = []
    compact_step_payload_offsets: list[int] = []
    compact_step_payload_lengths: list[int] = []
    compact_step_flags: list[int] = []
    compact_step_payload_values: list[int] = []
    original_to_compact_step_id: list[int] = []

    for step_id, label in enumerate(step_labels):
        payload = effect_payloads[step_id] if step_id < len(effect_payloads) else ()
        opcode_id = opcode_ids[step_id] if step_id < len(opcode_ids) else step_id
        effect_id = effect_ids[step_id] if step_id < len(effect_ids) else 0
        async_flag = step_async_flags[step_id] if step_id < len(step_async_flags) else 0
        signature = (opcode_id, effect_id, payload, async_flag)
        compact_step_id = semantic_step_index.get(signature)
        if compact_step_id is None:
            compact_step_id = len(compact_step_opcode_ids)
            semantic_step_index[signature] = compact_step_id
            compact_step_opcode_ids.append(opcode_id)
            compact_step_effect_ids.append(effect_id)
            compact_step_payload_offsets.append(len(compact_step_payload_values))
            compact_step_payload_lengths.append(len(payload))
            compact_step_payload_values.extend(payload)
            compact_step_flags.append(async_flag)
        original_to_compact_step_id.append(compact_step_id)

    prelude_step_ids = sorted(
        {
            original_to_compact_step_id[step_id]
            for step_id, label in enumerate(step_labels)
            if _BINDER_TOKEN in label
        }
    )
    prelude_step_id_set = set(prelude_step_ids)

    phase_ids: dict[str, int] = {}

    def phase_id_for(phase: str) -> int:
        normalized = str(normalize_phase(phase))
        cached = phase_ids.get(normalized)
        if cached is not None:
            return cached
        cached = len(phase_ids)
        phase_ids[normalized] = cached
        return cached

    segment_catalog_index: dict[tuple[Any, ...], int] = {}
    compact_segment_executor_kinds: list[int] = []
    compact_segment_phase_ids: list[int] = []
    compact_segment_step_offsets: list[int] = []
    compact_segment_step_lengths: list[int] = []
    compact_segment_step_refs: list[int] = []

    def compact_segment_id_for(
        executor_kind_id: int, step_refs: tuple[int, ...], phase_id: int
    ) -> int:
        signature = (
            int(executor_kind_id),
            step_refs,
            int(phase_id),
        )
        cached = segment_catalog_index.get(signature)
        if cached is not None:
            return cached
        cached = len(compact_segment_executor_kinds)
        segment_catalog_index[signature] = cached
        compact_segment_executor_kinds.append(signature[0])
        compact_segment_phase_ids.append(signature[2])
        compact_segment_step_offsets.append(len(compact_segment_step_refs))
        compact_segment_step_lengths.append(len(step_refs))
        compact_segment_step_refs.extend(step_refs)
        return cached

    segment_phases = tuple(
        str(phase)
        for phase in (
            getattr(packed, "segment_phases", ())
            or tuple(
                (getattr(packed, "phase_names", ()) or ())[phase_id]
                for phase_id in (getattr(packed, "segment_catalog_phase_ids", ()) or ())
                if 0 <= int(phase_id) < len(getattr(packed, "phase_names", ()) or ())
            )
            or ()
        )
    )
    segment_executor_kinds = tuple(
        str(kind)
        for kind in (
            getattr(packed, "segment_catalog_executor_kinds", ())
            or getattr(packed, "segment_executor_kinds", ())
            or ()
        )
    )
    segment_compact_steps: list[tuple[int, ...]] = []
    segment_phase_ids: list[int] = []
    segment_phase_kind_ids: list[int] = []
    segment_executor_kind_ids: list[int] = []

    for seg_id, phase in enumerate(segment_phases):
        step_refs = tuple(
            original_to_compact_step_id[step_id]
            for step_id in _segment_step_ids(packed, seg_id)
            if original_to_compact_step_id[step_id] not in prelude_step_id_set
        )
        normalized = str(normalize_phase(phase))
        segment_compact_steps.append(step_refs)
        segment_phase_ids.append(phase_id_for(normalized))
        segment_phase_kind_ids.append(_phase_kind_id(normalized))
        segment_executor_kind_ids.append(_EXECUTOR_KIND_IDS.get(segment_executor_kinds[seg_id], 0))

    program_segment_offsets = [
        int(value)
        for value in (
            getattr(packed, "program_segment_ref_offsets", ())
            or getattr(packed, "op_segment_offsets", ())
            or ()
        )
    ]
    program_segment_lengths = [
        int(value)
        for value in (
            getattr(packed, "program_segment_ref_lengths", ())
            or getattr(packed, "op_segment_lengths", ())
            or ()
        )
    ]
    op_to_segment_ids = [
        int(value)
        for value in (
            getattr(packed, "program_segment_refs", ())
            or getattr(packed, "op_to_segment_ids", ())
            or ()
        )
    ]

    compact_program_segment_offsets: list[int] = []
    compact_program_segment_lengths: list[int] = []
    compact_program_segment_refs: list[int] = []

    compact_error_profile_offsets: list[int] = []
    compact_error_profile_lengths: list[int] = []
    compact_error_profile_phase_ids: list[int] = []
    compact_error_profile_segment_offsets: list[int] = []
    compact_error_profile_segment_lengths: list[int] = []
    compact_error_profile_segment_refs: list[int] = []
    compact_program_error_profile_ids: list[int] = []

    packed_error_profile_offsets = list(
        getattr(packed, "error_profile_offsets", ()) or ()
    )
    if packed_error_profile_offsets:
        packed_error_profile_lengths = list(
            getattr(packed, "error_profile_lengths", ()) or ()
        )
        packed_error_profile_phase_ids = list(
            getattr(packed, "error_profile_phase_ids", ()) or ()
        )
        packed_error_profile_segment_offsets = list(
            getattr(packed, "error_profile_segment_ref_offsets", ()) or ()
        )
        packed_error_profile_segment_lengths = list(
            getattr(packed, "error_profile_segment_ref_lengths", ()) or ()
        )
        packed_error_profile_segment_refs = list(
            getattr(packed, "error_profile_segment_refs", ()) or ()
        )
        compact_error_profile_offsets.extend(packed_error_profile_offsets)
        compact_error_profile_lengths.extend(packed_error_profile_lengths)
        compact_error_profile_phase_ids.extend(packed_error_profile_phase_ids)
        compact_error_profile_segment_offsets.extend(packed_error_profile_segment_offsets)
        compact_error_profile_segment_lengths.extend(packed_error_profile_segment_lengths)
        compact_error_profile_segment_refs.extend(packed_error_profile_segment_refs)
        compact_program_error_profile_ids.extend(
            int(value) for value in (getattr(packed, "program_error_profile_ids", ()) or ())
        )

    for program_id, seg_offset in enumerate(program_segment_offsets):
        seg_length = program_segment_lengths[program_id] if program_id < len(program_segment_lengths) else 0
        seg_ids = tuple(op_to_segment_ids[seg_offset : seg_offset + seg_length])
        compact_program_segment_offsets.append(len(compact_program_segment_refs))
        current_kind = -1
        current_steps: list[int] = []
        current_phases: list[int] = []
        error_phase_segments: dict[int, list[int]] = {}

        def flush_mainline() -> None:
            nonlocal current_kind, current_steps, current_phases
            if not current_steps:
                current_kind = -1
                current_phases = []
                return
            compact_program_segment_refs.append(
                compact_segment_id_for(
                    executor_kind_id=current_kind,
                    step_refs=tuple(current_steps),
                    phase_id=current_phases[0] if current_phases else 0,
                )
            )
            current_kind = -1
            current_steps = []
            current_phases = []

        for seg_id in seg_ids:
            step_refs = segment_compact_steps[seg_id]
            if not step_refs:
                continue
            phase_kind_id = segment_phase_kind_ids[seg_id]
            phase_id = segment_phase_ids[seg_id]
            executor_kind_id = segment_executor_kind_ids[seg_id]

            if phase_kind_id == 0:
                if current_kind == executor_kind_id:
                    current_steps.extend(step_refs)
                    current_phases.extend([phase_id] * len(step_refs))
                    continue
                flush_mainline()
                current_kind = executor_kind_id
                current_steps = list(step_refs)
                current_phases = [phase_id] * len(step_refs)
                continue

            flush_mainline()
            error_segment_id = compact_segment_id_for(
                executor_kind_id=executor_kind_id,
                step_refs=step_refs,
                phase_id=phase_id,
            )
            error_phase_segments.setdefault(phase_id, []).append(error_segment_id)

        flush_mainline()
        compact_program_segment_lengths.append(
            len(compact_program_segment_refs) - compact_program_segment_offsets[-1]
        )
        if not packed_error_profile_offsets:
            compact_program_error_profile_ids.append(len(compact_error_profile_offsets))
            compact_error_profile_offsets.append(len(compact_error_profile_phase_ids))
            compact_error_profile_lengths.append(len(error_phase_segments))
            for phase_id, seg_refs in sorted(error_phase_segments.items()):
                compact_error_profile_phase_ids.append(phase_id)
                compact_error_profile_segment_offsets.append(
                    len(compact_error_profile_segment_refs)
                )
                compact_error_profile_segment_lengths.append(len(seg_refs))
                compact_error_profile_segment_refs.extend(seg_refs)

    route_entries: list[tuple[int, int, int]] = []
    for proto_id, row in enumerate((getattr(packed, "route_to_program", ()) or ())):
        for selector_id, program_id in enumerate(row):
            if int(program_id) < 0:
                continue
            route_entries.append((int(proto_id), int(selector_id), int(program_id)))
    route_entries.sort()

    method_ids: dict[str, int] = {}

    def method_id_for(method: str) -> int:
        cached = method_ids.get(method)
        if cached is not None:
            return cached
        cached = len(method_ids)
        method_ids[method] = cached
        return cached

    exact_route_entries = [
        (
            method_id_for(str(method)),
            _stable_hash64(str(path)),
            int(program_id),
        )
        for (method, path), program_id in sorted(
            (getattr(packed, "rest_exact_route_to_program", {}) or {}).items()
        )
    ]

    return {
        "compact_step_opcode_ids": compact_step_opcode_ids,
        "compact_step_effect_ids": compact_step_effect_ids,
        "compact_step_payload_offsets": compact_step_payload_offsets,
        "compact_step_payload_lengths": compact_step_payload_lengths,
        "compact_step_payload_values": compact_step_payload_values,
        "compact_step_flags": compact_step_flags,
        "prelude_step_ids": prelude_step_ids,
        "compact_segment_executor_kinds": compact_segment_executor_kinds,
        "compact_segment_phase_ids": compact_segment_phase_ids,
        "compact_segment_step_offsets": compact_segment_step_offsets,
        "compact_segment_step_lengths": compact_segment_step_lengths,
        "compact_segment_step_refs": compact_segment_step_refs,
        "compact_program_segment_offsets": compact_program_segment_offsets,
        "compact_program_segment_lengths": compact_program_segment_lengths,
        "compact_program_segment_refs": compact_program_segment_refs,
        "compact_error_profile_offsets": compact_error_profile_offsets,
        "compact_error_profile_lengths": compact_error_profile_lengths,
        "compact_error_profile_phase_ids": compact_error_profile_phase_ids,
        "compact_error_profile_segment_offsets": compact_error_profile_segment_offsets,
        "compact_error_profile_segment_lengths": compact_error_profile_segment_lengths,
        "compact_error_profile_segment_refs": compact_error_profile_segment_refs,
        "compact_program_error_profile_ids": compact_program_error_profile_ids,
        "route_entries": route_entries,
        "exact_route_entries": exact_route_entries,
        "phase_count": len(phase_ids),
        "method_count": len(method_ids),
    }


def build_packed_kernel_measurement_view(packed: PackedKernel) -> dict[str, Any]:
    route_to_program = getattr(packed, "route_to_program", ()) or ()
    route_row_count = len(route_to_program)
    route_col_count = max((len(row) for row in route_to_program), default=0)
    exact_route_count = len(getattr(packed, "rest_exact_route_to_program", {}) or {})
    hot_plans = tuple(getattr(packed, "hot_op_plans", ()) or ())
    compact = _build_compact_image_parts(packed)

    hot_plan_view = [
        {
            "program_id": int(plan.program_id),
            "alias": str(plan.alias),
            "target": str(plan.target),
            "ordered_segment_ids": list(plan.ordered_segment_ids),
            "remaining_segment_ids": list(plan.remaining_segment_ids),
            "fusible_sync_segment_ids": list(plan.fusible_sync_segment_ids),
            "nonfusible_segment_ids": list(plan.nonfusible_segment_ids),
            "dispatch_proto_ids": list(plan.dispatch_proto_ids),
            "dispatch_selector_count": int(plan.dispatch_selector_count),
            "program_hot_runner_id": int(
                getattr(plan, "program_hot_runner_id", 0) or 0
            ),
            "error_segment_ids": {
                str(phase): list(seg_ids)
                for phase, seg_ids in sorted(plan.error_segment_ids.items())
            },
            "db_acquire_hint": str(plan.db_acquire_hint),
        }
        for plan in hot_plans
    ]

    return {
        "proto_names": list(getattr(packed, "proto_names", ()) or ()),
        "selector_names": list(getattr(packed, "selector_names", ()) or ()),
        "op_names": list(getattr(packed, "op_names", ()) or ()),
        "segment_offsets": list(getattr(packed, "segment_offsets", ()) or ()),
        "segment_lengths": list(getattr(packed, "segment_lengths", ()) or ()),
        "segment_step_ids": list(getattr(packed, "segment_step_ids", ()) or ()),
        "segment_phases": list(getattr(packed, "segment_phases", ()) or ()),
        "segment_executor_kinds": list(
            getattr(packed, "segment_executor_kinds", ()) or ()
        ),
        "op_segment_offsets": list(getattr(packed, "op_segment_offsets", ()) or ()),
        "op_segment_lengths": list(getattr(packed, "op_segment_lengths", ()) or ()),
        "op_to_segment_ids": list(getattr(packed, "op_to_segment_ids", ()) or ()),
        "step_labels": list(getattr(packed, "step_labels", ()) or ()),
        "step_async_flags": [
            bool(flag) for flag in getattr(packed, "step_async_flags", ()) or ()
        ],
        "numba_effect_ids": list(getattr(packed, "numba_effect_ids", ()) or ()),
        "numba_effect_payloads": [
            list(payload)
            for payload in (getattr(packed, "numba_effect_payloads", ()) or ())
        ],
        "phase_tree_nodes": [
            {
                "node_id": str(node.node_id),
                "phase": str(node.phase),
                "stage_in": node.stage_in,
                "stage_out": node.stage_out,
                "segment_ids": list(node.segment_ids),
                "terminal_behavior": str(node.terminal_behavior),
                "linear_index": int(node.linear_index),
                "ok_child": {
                    "kind": str(node.ok_child.kind),
                    "target_kind": str(node.ok_child.target.kind),
                    "target_value": node.ok_child.target.ref,
                    "target_fallback": node.ok_child.target.fallback,
                },
                "err_child": {
                    "kind": str(node.err_child.kind),
                    "target_kind": str(node.err_child.target.kind),
                    "target_value": node.err_child.target.ref,
                    "target_fallback": node.err_child.target.fallback,
                },
            }
            for node in (getattr(packed, "phase_tree_nodes", ()) or ())
        ],
        "program_phase_tree_offsets": list(
            getattr(packed, "program_phase_tree_offsets", ()) or ()
        ),
        "program_phase_tree_lengths": list(
            getattr(packed, "program_phase_tree_lengths", ()) or ()
        ),
        "route_to_program": [list(row) for row in route_to_program],
        "rest_exact_route_to_program": [
            {"method": method, "path": path, "program_id": int(program_id)}
            for (method, path), program_id in sorted(
                (getattr(packed, "rest_exact_route_to_program", {}) or {}).items()
            )
        ],
        "route_shape": {
            "rows": route_row_count,
            "cols": route_col_count,
            "slots": route_row_count * route_col_count,
            "exact_route_count": exact_route_count,
        },
        "hot_op_plans": hot_plan_view,
        "executor_kind": str(getattr(packed, "executor_kind", "python")),
        "program_hot_runner_ids": list(
            getattr(packed, "program_hot_runner_ids", ()) or ()
        ),
        "compact_image": {
            "compact_step_count": len(compact["compact_step_opcode_ids"]),
            "compact_segment_count": len(compact["compact_segment_executor_kinds"]),
            "compact_program_segment_ref_count": len(
                compact["compact_program_segment_refs"]
            ),
            "compact_route_entry_count": len(compact["route_entries"])
            + len(compact["exact_route_entries"]),
            "shared_error_profile_count": len(
                compact["compact_error_profile_offsets"]
            ),
            "externalized_prelude_step_count": len(compact["prelude_step_ids"]),
            "phase_count": int(compact["phase_count"]),
            "method_count": int(compact["method_count"]),
            "compact_opcode_count": len(
                set(int(value) for value in compact["compact_step_opcode_ids"])
            ),
        },
    }


def serialize_packed_kernel_measurement_view(packed: PackedKernel) -> bytes:
    compact = _build_compact_image_parts(packed)
    atom_labels = tuple(
        str(label)
        for label in (
            getattr(packed, "atom_catalog_labels", ())
            or getattr(packed, "step_labels", ())
            or ()
        )
    )
    atom_opcode_ids = [
        int(value)
        for value in (
            getattr(packed, "atom_catalog_opcode_ids", ())
            or tuple(range(len(atom_labels)))
        )
    ]
    atom_effect_ids = [
        int(value)
        for value in (
            getattr(packed, "atom_catalog_effect_ids", ())
            or getattr(packed, "numba_effect_ids", ())
            or ()
        )
    ]
    atom_effect_payloads = [
        tuple(int(item) for item in payload)
        for payload in (
            getattr(packed, "atom_catalog_effect_payloads", ())
            or getattr(packed, "numba_effect_payloads", ())
            or ()
        )
    ]
    atom_flags = [
        1 if bool(flag) else 0
        for flag in (
            getattr(packed, "atom_catalog_async_flags", ())
            or getattr(packed, "step_async_flags", ())
            or ()
        )
    ]
    atom_payload_offsets: list[int] = []
    atom_payload_lengths: list[int] = []
    atom_payload_values: list[int] = []
    for payload in atom_effect_payloads:
        atom_payload_offsets.append(len(atom_payload_values))
        atom_payload_lengths.append(len(payload))
        atom_payload_values.extend(int(item) for item in payload)

    prelude_atom_ids = [
        index for index, label in enumerate(atom_labels) if _BINDER_TOKEN in label
    ]
    segment_step_offsets = [
        int(value)
        for value in (
            getattr(packed, "segment_catalog_offsets", ())
            or getattr(packed, "segment_offsets", ())
            or ()
        )
    ]
    segment_step_lengths = [
        int(value)
        for value in (
            getattr(packed, "segment_catalog_lengths", ())
            or getattr(packed, "segment_lengths", ())
            or ()
        )
    ]
    segment_step_atom_refs = [
        int(value)
        for value in (
            getattr(packed, "segment_catalog_atom_ids", ())
            or getattr(packed, "segment_step_ids", ())
            or ()
        )
    ]
    segment_executor_kind_ids = [
        int(
            _EXECUTOR_KIND_IDS.get(str(kind), int(kind) if isinstance(kind, int) else 0)
        )
        for kind in (
            getattr(packed, "segment_catalog_executor_kinds", ())
            or getattr(packed, "segment_executor_kinds", ())
            or ()
        )
    ]
    packed_phase_ids = tuple(getattr(packed, "segment_catalog_phase_ids", ()) or ())
    if packed_phase_ids:
        segment_phase_ids = [int(value) for value in packed_phase_ids]
    else:
        phase_to_id = {
            str(key): int(value)
            for key, value in (getattr(packed, "phase_to_id", {}) or {}).items()
        }
        segment_phase_ids = [
            int(phase_to_id.get(str(normalize_phase(phase)), 0))
            for phase in (getattr(packed, "segment_phases", ()) or ())
        ]

    program_segment_offsets = [
        int(value)
        for value in (
            getattr(packed, "program_segment_ref_offsets", ())
            or getattr(packed, "op_segment_offsets", ())
            or ()
        )
    ]
    program_segment_lengths = [
        int(value)
        for value in (
            getattr(packed, "program_segment_ref_lengths", ())
            or getattr(packed, "op_segment_lengths", ())
            or ()
        )
    ]
    program_segment_refs = [
        int(value)
        for value in (
            getattr(packed, "program_segment_refs", ())
            or getattr(packed, "op_to_segment_ids", ())
            or ()
        )
    ]
    program_hot_runner_ids = [
        int(value) for value in (getattr(packed, "program_hot_runner_ids", ()) or ())
    ]
    error_profile_offsets = [int(value) for value in (getattr(packed, "error_profile_offsets", ()) or ())]
    error_profile_lengths = [int(value) for value in (getattr(packed, "error_profile_lengths", ()) or ())]
    error_profile_phase_ids = [int(value) for value in (getattr(packed, "error_profile_phase_ids", ()) or ())]
    error_profile_segment_offsets = [int(value) for value in (getattr(packed, "error_profile_segment_ref_offsets", ()) or ())]
    error_profile_segment_lengths = [int(value) for value in (getattr(packed, "error_profile_segment_ref_lengths", ()) or ())]
    error_profile_segment_refs = [int(value) for value in (getattr(packed, "error_profile_segment_refs", ()) or ())]
    program_error_profile_ids = [int(value) for value in (getattr(packed, "program_error_profile_ids", ()) or ())]

    route_entries = []
    for proto_id, row in enumerate((getattr(packed, "route_to_program", ()) or ())):
        for selector_id, program_id in enumerate(row):
            if int(program_id) < 0:
                continue
            route_entries.append((int(proto_id), int(selector_id), int(program_id)))
    route_entries.sort()
    route_proto_ids = [entry[0] for entry in route_entries]
    route_selector_ids = [entry[1] for entry in route_entries]
    route_program_ids = [entry[2] for entry in route_entries]
    method_ids: dict[str, int] = {}
    def method_id_for(method: str) -> int:
        cached = method_ids.get(method)
        if cached is not None:
            return cached
        cached = len(method_ids)
        method_ids[method] = cached
        return cached
    exact_route_entries = [
        (method_id_for(str(method)), _stable_hash64(str(path)), int(program_id))
        for (method, path), program_id in sorted(
            (getattr(packed, "rest_exact_route_to_program", {}) or {}).items()
        )
    ]
    exact_method_ids = [entry[0] for entry in exact_route_entries]
    exact_path_hashes = [entry[1] for entry in exact_route_entries]
    exact_program_ids = [entry[2] for entry in exact_route_entries]

    section_specs: list[tuple[int, int, int, bytes]] = []

    def _add_unsigned(name: str, values: list[int]) -> None:
        width_bits, payload = _pack_unsigned_array(values)
        section_specs.append((_HOT_BLOCK_SECTION_IDS[name], width_bits, len(values), payload))

    def _add_signed(name: str, values: list[int]) -> None:
        width_bits, payload = _pack_signed_array(values)
        section_specs.append((_HOT_BLOCK_SECTION_IDS[name], width_bits, len(values), payload))

    _add_unsigned("atom_opcode_ids", atom_opcode_ids)
    _add_unsigned("atom_effect_ids", atom_effect_ids)
    _add_unsigned("atom_payload_offsets", atom_payload_offsets)
    _add_unsigned("atom_payload_lengths", atom_payload_lengths)
    _add_signed("atom_payload_values", atom_payload_values)
    _add_unsigned("atom_flags", atom_flags)
    _add_unsigned("prelude_atom_ids", prelude_atom_ids)
    _add_unsigned("segment_executor_kind_ids", segment_executor_kind_ids)
    _add_unsigned("segment_phase_ids", segment_phase_ids)
    _add_unsigned("segment_step_offsets", segment_step_offsets)
    _add_unsigned("segment_step_lengths", segment_step_lengths)
    _add_unsigned("segment_step_atom_refs", segment_step_atom_refs)
    _add_unsigned("program_segment_offsets", program_segment_offsets)
    _add_unsigned("program_segment_lengths", program_segment_lengths)
    _add_unsigned("program_segment_refs", program_segment_refs)
    _add_unsigned("program_hot_runner_ids", program_hot_runner_ids)
    _add_unsigned("error_profile_offsets", error_profile_offsets)
    _add_unsigned("error_profile_lengths", error_profile_lengths)
    _add_unsigned("error_profile_phase_ids", error_profile_phase_ids)
    _add_unsigned("error_profile_segment_offsets", error_profile_segment_offsets)
    _add_unsigned("error_profile_segment_lengths", error_profile_segment_lengths)
    _add_unsigned("error_profile_segment_refs", error_profile_segment_refs)
    _add_unsigned("program_error_profile_ids", program_error_profile_ids)
    _add_unsigned("route_proto_ids", route_proto_ids)
    _add_unsigned("route_selector_ids", route_selector_ids)
    _add_unsigned("route_program_ids", route_program_ids)
    _add_unsigned("exact_method_ids", exact_method_ids)
    section_specs.append((_HOT_BLOCK_SECTION_IDS["exact_path_hashes"], 64, len(exact_path_hashes), _pack_u64(exact_path_hashes)))
    _add_unsigned("exact_program_ids", exact_program_ids)

    max_width_bits = max((spec[1] for spec in section_specs), default=16)
    section_count = len(section_specs)
    header_size = struct.calcsize("<8sHHIHHHHHHH")
    directory_entry_size = struct.calcsize("<HBBII")
    directory_offset = header_size
    data_offset = directory_offset + (section_count * directory_entry_size)
    directory_entries: list[bytes] = []
    payload_chunks: list[bytes] = []
    cursor = data_offset
    for section_id, width_bits, count, payload in section_specs:
        directory_entries.append(
            struct.pack("<HBBII", int(section_id), int(width_bits), 0, int(count), int(cursor))
        )
        payload_chunks.append(payload)
        cursor += len(payload)

    total_bytes = cursor
    header = struct.pack(
        "<8sHHIHHHHHHH",
        _HOT_BLOCK_MAGIC,
        _HOT_BLOCK_VERSION,
        int(max_width_bits),
        int(total_bytes),
        int(section_count),
        int(directory_offset),
        len(atom_opcode_ids),
        len(segment_step_offsets),
        len(program_segment_offsets),
        len(error_profile_offsets),
        len(route_entries) + len(exact_route_entries),
    )
    return header + b"".join(directory_entries) + b"".join(payload_chunks)


def load_packed_kernel_hot_block(payload: bytes) -> dict[str, Any]:
    header_size = struct.calcsize("<8sHHIHHHHHHH")
    if len(payload) < header_size:
        raise ValueError("hot block payload is truncated")
    (
        magic,
        version,
        max_width_bits,
        total_bytes,
        section_count,
        directory_offset,
        atom_count,
        segment_count,
        program_count,
        error_profile_count,
        route_entry_count,
    ) = struct.unpack("<8sHHIHHHHHHH", payload[:header_size])
    if magic != _HOT_BLOCK_MAGIC:
        raise ValueError("invalid hot block magic")
    if version != _HOT_BLOCK_VERSION:
        raise ValueError(f"unsupported hot block version: {version}")
    if total_bytes != len(payload):
        raise ValueError("hot block length mismatch")
    entry_size = struct.calcsize("<HBBII")
    directory_size = section_count * entry_size
    data_start = directory_offset + directory_size
    if data_start > len(payload):
        raise ValueError("hot block directory exceeds payload length")

    out: dict[str, Any] = {
        "version": int(version),
        "max_width_bits": int(max_width_bits),
        "atom_count": int(atom_count),
        "segment_count": int(segment_count),
        "program_count": int(program_count),
        "error_profile_count": int(error_profile_count),
        "route_entry_count": int(route_entry_count),
    }
    for index in range(section_count):
        start = directory_offset + (index * entry_size)
        end = start + entry_size
        section_id, width_bits, _flags, count, offset = struct.unpack(
            "<HBBII", payload[start:end]
        )
        name = _HOT_BLOCK_SECTION_NAMES.get(int(section_id))
        if not name:
            continue
        next_offset = (
            struct.unpack("<HBBII", payload[end : end + entry_size])[4]
            if index + 1 < section_count
            else len(payload)
        )
        if offset > next_offset or next_offset > len(payload):
            raise ValueError("hot block section offset is invalid")
        section_payload = payload[offset:next_offset]
        if name == "atom_payload_values":
            out[name] = _unpack_signed_array(int(width_bits), section_payload, int(count))
        else:
            out[name] = _unpack_unsigned_array(int(width_bits), section_payload, int(count))
    return out


def measure_packed_kernel(packed: PackedKernel) -> PackedKernelMeasurement:
    payload = getattr(packed, "hot_block_bytes", b"") or serialize_packed_kernel_measurement_view(packed)
    compressed = gzip.compress(payload, compresslevel=9, mtime=0)
    hot_plans = tuple(getattr(packed, "hot_op_plans", ()) or ())
    route_to_program = getattr(packed, "route_to_program", ()) or ()
    route_row_count = len(route_to_program)
    route_col_count = max((len(row) for row in route_to_program), default=0)
    exact_route_count = len(getattr(packed, "rest_exact_route_to_program", {}) or {})
    fusible_sync_segment_count = sum(
        len(plan.fusible_sync_segment_ids)
        for plan in hot_plans
        if isinstance(plan, HotOpPlan)
    )
    view = build_packed_kernel_measurement_view(packed)
    compact = view.get("compact_image", {})
    compact_parts = _build_compact_image_parts(packed)
    max_index_width_bits = max(
        _pack_unsigned_array(compact_parts["compact_step_opcode_ids"])[0],
        _pack_unsigned_array(compact_parts["compact_segment_phase_ids"])[0],
        _pack_unsigned_array(compact_parts["compact_segment_step_refs"])[0],
        _pack_unsigned_array(compact_parts["compact_program_segment_refs"])[0],
        _pack_unsigned_array(compact_parts["compact_error_profile_segment_refs"])[0],
        _pack_unsigned_array(compact_parts["compact_program_error_profile_ids"])[0],
        _pack_unsigned_array(compact_parts["prelude_step_ids"])[0],
        _pack_unsigned_array([entry[2] for entry in compact_parts["route_entries"]])[0],
        _pack_unsigned_array([entry[2] for entry in compact_parts["exact_route_entries"]])[0],
        16,
    )
    return PackedKernelMeasurement(
        raw_bytes=len(payload),
        compressed_bytes=len(compressed),
        segment_count=len(getattr(packed, "segment_offsets", ()) or ()),
        step_count=len(getattr(packed, "step_table", ()) or ()),
        phase_tree_node_count=len(getattr(packed, "phase_tree_nodes", ()) or ()),
        proto_count=len(getattr(packed, "proto_names", ()) or ()),
        selector_count=len(getattr(packed, "selector_names", ()) or ()),
        op_count=len(getattr(packed, "op_names", ()) or ()),
        route_row_count=route_row_count,
        route_col_count=route_col_count,
        route_slot_count=route_row_count * route_col_count,
        exact_route_count=exact_route_count,
        fusible_sync_segment_count=fusible_sync_segment_count,
        hot_op_count=len(hot_plans),
        compact_step_count=int(compact.get("compact_step_count", 0)),
        compact_segment_count=int(compact.get("compact_segment_count", 0)),
        compact_program_segment_ref_count=int(
            compact.get("compact_program_segment_ref_count", 0)
        ),
        compact_route_entry_count=int(compact.get("compact_route_entry_count", 0)),
        shared_error_profile_count=int(
            compact.get("shared_error_profile_count", 0)
        ),
        externalized_prelude_step_count=int(
            compact.get("externalized_prelude_step_count", 0)
        ),
        max_index_width_bits=max_index_width_bits,
        measurement_view=view,
    )


__all__ = [
    "build_packed_kernel_measurement_view",
    "load_packed_kernel_hot_block",
    "measure_packed_kernel",
    "serialize_packed_kernel_measurement_view",
]
