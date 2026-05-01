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


def _pack_u8(values: list[int]) -> bytes:
    if not values:
        return b""
    return bytes(values)


def _pack_index_array(values: list[int]) -> tuple[int, bytes]:
    if _uses_u16(values):
        return 16, _pack_u16(values)
    return 32, _pack_u32(values)


def _pack_section(section_id: int, payload: bytes) -> bytes:
    return struct.pack("<BI", int(section_id), len(payload)) + payload


def _segment_step_ids(packed: PackedKernel, seg_id: int) -> tuple[int, ...]:
    offset = int((getattr(packed, "segment_offsets", ()) or ())[seg_id])
    length = int((getattr(packed, "segment_lengths", ()) or ())[seg_id])
    step_ids = getattr(packed, "segment_step_ids", ()) or ()
    return tuple(int(step_ids[offset + idx]) for idx in range(length))


def _build_compact_image_parts(packed: PackedKernel) -> dict[str, Any]:
    step_labels = tuple(str(label) for label in (getattr(packed, "step_labels", ()) or ()))
    effect_ids = [int(value) for value in (getattr(packed, "numba_effect_ids", ()) or ())]
    effect_payloads = [
        tuple(int(item) for item in payload)
        for payload in (getattr(packed, "numba_effect_payloads", ()) or ())
    ]
    step_async_flags = [1 if bool(flag) else 0 for flag in (getattr(packed, "step_async_flags", ()) or ())]

    semantic_step_index: dict[tuple[Any, ...], int] = {}
    compact_step_label_hashes: list[int] = []
    compact_step_effect_ids: list[int] = []
    compact_step_payload_offsets: list[int] = []
    compact_step_payload_lengths: list[int] = []
    compact_step_flags: list[int] = []
    compact_step_payload_values: list[int] = []
    original_to_compact_step_id: list[int] = []

    for step_id, label in enumerate(step_labels):
        payload = effect_payloads[step_id] if step_id < len(effect_payloads) else ()
        effect_id = effect_ids[step_id] if step_id < len(effect_ids) else 0
        async_flag = step_async_flags[step_id] if step_id < len(step_async_flags) else 0
        signature = (label, effect_id, payload, async_flag)
        compact_step_id = semantic_step_index.get(signature)
        if compact_step_id is None:
            compact_step_id = len(compact_step_label_hashes)
            semantic_step_index[signature] = compact_step_id
            compact_step_label_hashes.append(_stable_hash64(label))
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
    compact_segment_step_offsets: list[int] = []
    compact_segment_step_lengths: list[int] = []
    compact_segment_step_refs: list[int] = []
    compact_segment_phase_offsets: list[int] = []
    compact_segment_phase_lengths: list[int] = []
    compact_segment_phase_refs: list[int] = []

    def compact_segment_id_for(
        executor_kind_id: int, step_refs: tuple[int, ...], phase_refs: tuple[int, ...]
    ) -> int:
        signature = (
            int(executor_kind_id),
            step_refs,
            phase_refs,
        )
        cached = segment_catalog_index.get(signature)
        if cached is not None:
            return cached
        cached = len(compact_segment_executor_kinds)
        segment_catalog_index[signature] = cached
        compact_segment_executor_kinds.append(signature[0])
        compact_segment_step_offsets.append(len(compact_segment_step_refs))
        compact_segment_step_lengths.append(len(step_refs))
        compact_segment_step_refs.extend(step_refs)
        compact_segment_phase_offsets.append(len(compact_segment_phase_refs))
        compact_segment_phase_lengths.append(len(phase_refs))
        compact_segment_phase_refs.extend(phase_refs)
        return cached

    segment_phases = tuple(str(phase) for phase in (getattr(packed, "segment_phases", ()) or ()))
    segment_executor_kinds = tuple(
        str(kind) for kind in (getattr(packed, "segment_executor_kinds", ()) or ())
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

    program_segment_offsets = [int(value) for value in (getattr(packed, "op_segment_offsets", ()) or ())]
    program_segment_lengths = [int(value) for value in (getattr(packed, "op_segment_lengths", ()) or ())]
    op_to_segment_ids = [int(value) for value in (getattr(packed, "op_to_segment_ids", ()) or ())]

    compact_program_segment_offsets: list[int] = []
    compact_program_segment_lengths: list[int] = []
    compact_program_segment_refs: list[int] = []

    error_profile_index: dict[tuple[Any, ...], int] = {}
    compact_error_profile_offsets: list[int] = []
    compact_error_profile_lengths: list[int] = []
    compact_error_profile_phase_ids: list[int] = []
    compact_error_profile_segment_offsets: list[int] = []
    compact_error_profile_segment_lengths: list[int] = []
    compact_error_profile_segment_refs: list[int] = []
    compact_program_error_profile_ids: list[int] = []

    def compact_error_profile_id_for(profile_entries: tuple[tuple[int, tuple[int, ...]], ...]) -> int:
        cached = error_profile_index.get(profile_entries)
        if cached is not None:
            return cached
        cached = len(compact_error_profile_offsets)
        error_profile_index[profile_entries] = cached
        compact_error_profile_offsets.append(len(compact_error_profile_phase_ids))
        compact_error_profile_lengths.append(len(profile_entries))
        for phase_id, seg_refs in profile_entries:
            compact_error_profile_phase_ids.append(phase_id)
            compact_error_profile_segment_offsets.append(len(compact_error_profile_segment_refs))
            compact_error_profile_segment_lengths.append(len(seg_refs))
            compact_error_profile_segment_refs.extend(seg_refs)
        return cached

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
                    phase_refs=tuple(current_phases),
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
                phase_refs=tuple([phase_id] * len(step_refs)),
            )
            error_phase_segments.setdefault(phase_id, []).append(error_segment_id)

        flush_mainline()
        compact_program_segment_lengths.append(
            len(compact_program_segment_refs) - compact_program_segment_offsets[-1]
        )
        error_profile_entries = tuple(
            (phase_id, tuple(seg_refs))
            for phase_id, seg_refs in sorted(error_phase_segments.items())
        )
        compact_program_error_profile_ids.append(
            compact_error_profile_id_for(error_profile_entries)
        )

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
        "compact_step_label_hashes": compact_step_label_hashes,
        "compact_step_effect_ids": compact_step_effect_ids,
        "compact_step_payload_offsets": compact_step_payload_offsets,
        "compact_step_payload_lengths": compact_step_payload_lengths,
        "compact_step_payload_values": compact_step_payload_values,
        "compact_step_flags": compact_step_flags,
        "prelude_step_ids": prelude_step_ids,
        "compact_segment_executor_kinds": compact_segment_executor_kinds,
        "compact_segment_step_offsets": compact_segment_step_offsets,
        "compact_segment_step_lengths": compact_segment_step_lengths,
        "compact_segment_step_refs": compact_segment_step_refs,
        "compact_segment_phase_offsets": compact_segment_phase_offsets,
        "compact_segment_phase_lengths": compact_segment_phase_lengths,
        "compact_segment_phase_refs": compact_segment_phase_refs,
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
        "compact_image": {
            "compact_step_count": len(compact["compact_step_label_hashes"]),
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
        },
    }


def serialize_packed_kernel_measurement_view(packed: PackedKernel) -> bytes:
    compact = _build_compact_image_parts(packed)
    step_width_bits, step_payload = _pack_index_array(compact["compact_segment_step_refs"])
    phase_width_bits, phase_payload = _pack_index_array(compact["compact_segment_phase_refs"])
    program_ref_width_bits, program_ref_payload = _pack_index_array(
        compact["compact_program_segment_refs"]
    )
    error_ref_width_bits, error_ref_payload = _pack_index_array(
        compact["compact_error_profile_segment_refs"]
    )
    error_profile_id_width_bits, error_profile_id_payload = _pack_index_array(
        compact["compact_program_error_profile_ids"]
    )
    prelude_width_bits, prelude_payload = _pack_index_array(compact["prelude_step_ids"])

    route_proto_ids = [entry[0] for entry in compact["route_entries"]]
    route_selector_ids = [entry[1] for entry in compact["route_entries"]]
    route_program_ids = [entry[2] for entry in compact["route_entries"]]
    route_program_width_bits, route_program_payload = _pack_index_array(route_program_ids)

    exact_method_ids = [entry[0] for entry in compact["exact_route_entries"]]
    exact_path_hashes = [entry[1] for entry in compact["exact_route_entries"]]
    exact_program_ids = [entry[2] for entry in compact["exact_route_entries"]]
    exact_program_width_bits, exact_program_payload = _pack_index_array(exact_program_ids)

    max_index_width_bits = max(
        step_width_bits,
        phase_width_bits,
        program_ref_width_bits,
        error_ref_width_bits,
        error_profile_id_width_bits,
        prelude_width_bits,
        route_program_width_bits,
        exact_program_width_bits,
        16,
    )

    header = struct.pack(
        "<8sHHHHHHHHHHH",
        b"TGPKSOA1",
        1,
        max_index_width_bits,
        len(compact["compact_step_label_hashes"]),
        len(compact["compact_segment_executor_kinds"]),
        len(compact["compact_program_segment_offsets"]),
        len(compact["compact_error_profile_offsets"]),
        len(compact["route_entries"]),
        len(compact["exact_route_entries"]),
        len(compact["prelude_step_ids"]),
        int(compact["phase_count"]),
        int(compact["method_count"]),
    )

    sections = [
        _pack_section(1, _pack_u64(compact["compact_step_label_hashes"])),
        _pack_section(2, _pack_u16(compact["compact_step_effect_ids"])),
        _pack_section(3, _pack_u32(compact["compact_step_payload_offsets"])),
        _pack_section(4, _pack_u16(compact["compact_step_payload_lengths"])),
        _pack_section(5, _pack_i32(compact["compact_step_payload_values"])),
        _pack_section(6, _pack_u8(compact["compact_step_flags"])),
        _pack_section(7, struct.pack("<H", prelude_width_bits) + prelude_payload),
        _pack_section(8, _pack_u8(compact["compact_segment_executor_kinds"])),
        _pack_section(9, _pack_u32(compact["compact_segment_step_offsets"])),
        _pack_section(10, _pack_u16(compact["compact_segment_step_lengths"])),
        _pack_section(11, struct.pack("<H", step_width_bits) + step_payload),
        _pack_section(12, _pack_u32(compact["compact_segment_phase_offsets"])),
        _pack_section(13, _pack_u16(compact["compact_segment_phase_lengths"])),
        _pack_section(14, struct.pack("<H", phase_width_bits) + phase_payload),
        _pack_section(15, _pack_u32(compact["compact_program_segment_offsets"])),
        _pack_section(16, _pack_u16(compact["compact_program_segment_lengths"])),
        _pack_section(17, struct.pack("<H", program_ref_width_bits) + program_ref_payload),
        _pack_section(18, _pack_u32(compact["compact_error_profile_offsets"])),
        _pack_section(19, _pack_u16(compact["compact_error_profile_lengths"])),
        _pack_section(20, _pack_u16(compact["compact_error_profile_phase_ids"])),
        _pack_section(21, _pack_u32(compact["compact_error_profile_segment_offsets"])),
        _pack_section(22, _pack_u16(compact["compact_error_profile_segment_lengths"])),
        _pack_section(23, struct.pack("<H", error_ref_width_bits) + error_ref_payload),
        _pack_section(
            24,
            struct.pack("<H", error_profile_id_width_bits) + error_profile_id_payload,
        ),
        _pack_section(25, _pack_u16(route_proto_ids)),
        _pack_section(26, _pack_u16(route_selector_ids)),
        _pack_section(27, struct.pack("<H", route_program_width_bits) + route_program_payload),
        _pack_section(28, _pack_u16(exact_method_ids)),
        _pack_section(29, _pack_u64(exact_path_hashes)),
        _pack_section(30, struct.pack("<H", exact_program_width_bits) + exact_program_payload),
    ]
    return header + b"".join(sections)


def measure_packed_kernel(packed: PackedKernel) -> PackedKernelMeasurement:
    payload = serialize_packed_kernel_measurement_view(packed)
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
        _pack_index_array(compact_parts["compact_segment_step_refs"])[0],
        _pack_index_array(compact_parts["compact_segment_phase_refs"])[0],
        _pack_index_array(compact_parts["compact_program_segment_refs"])[0],
        _pack_index_array(compact_parts["compact_error_profile_segment_refs"])[0],
        _pack_index_array(compact_parts["compact_program_error_profile_ids"])[0],
        _pack_index_array(compact_parts["prelude_step_ids"])[0],
        _pack_index_array([entry[2] for entry in compact_parts["route_entries"]])[0],
        _pack_index_array([entry[2] for entry in compact_parts["exact_route_entries"]])[0],
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
    "measure_packed_kernel",
    "serialize_packed_kernel_measurement_view",
]
