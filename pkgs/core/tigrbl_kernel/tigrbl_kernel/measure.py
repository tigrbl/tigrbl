from __future__ import annotations

import gzip
import json
from typing import Any, Mapping

from .models import HotOpPlan, PackedKernel, PackedKernelMeasurement


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


def build_packed_kernel_measurement_view(packed: PackedKernel) -> dict[str, Any]:
    route_to_program = getattr(packed, "route_to_program", ()) or ()
    route_row_count = len(route_to_program)
    route_col_count = max((len(row) for row in route_to_program), default=0)
    exact_route_count = len(getattr(packed, "rest_exact_route_to_program", {}) or {})
    hot_plans = tuple(getattr(packed, "hot_op_plans", ()) or ())

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
        "step_async_flags": [bool(flag) for flag in getattr(packed, "step_async_flags", ()) or ()],
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
    }


def serialize_packed_kernel_measurement_view(packed: PackedKernel) -> bytes:
    view = build_packed_kernel_measurement_view(packed)
    canonical = _freeze_value(view)
    return json.dumps(
        canonical,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


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
        measurement_view=view,
    )


__all__ = [
    "build_packed_kernel_measurement_view",
    "measure_packed_kernel",
    "serialize_packed_kernel_measurement_view",
]
