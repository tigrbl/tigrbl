from __future__ import annotations

from tigrbl_kernel.measure import (
    build_packed_kernel_measurement_view,
    load_packed_kernel_hot_block,
    measure_packed_kernel,
    serialize_packed_kernel_measurement_view,
)
from tigrbl_kernel.models import HotOpPlan, PackedKernel


def _sample_packed_kernel() -> PackedKernel:
    hot_op_plan = HotOpPlan(
        program_id=0,
        alias="Widget.create",
        target="create",
        ordered_segment_ids=(0, 1),
        remaining_segment_ids=(2,),
        fusible_sync_segment_ids=(0, 1),
        nonfusible_segment_ids=(2,),
        error_segment_ids={"ON_ERROR": (3,)},
        dispatch_proto_ids=(0,),
        dispatch_selector_count=1,
        program_hot_runner_id=1,
    )
    return PackedKernel(
        atom_catalog_labels=("step0", "step1", "step2", "step3"),
        atom_catalog_opcode_ids=(0, 1, 2, 3),
        atom_opcode_keys=("step0", "step1", "step2", "step3"),
        atom_catalog_effect_ids=(0, 1, 2, 3),
        atom_catalog_effect_payloads=((0,), (1,), (2,), (3,)),
        atom_catalog_async_flags=(False, False, False, True),
        param_shape_offsets=(0,),
        param_shape_lengths=(1,),
        param_shape_source_masks=(1,),
        param_shape_slot_ids=(0,),
        param_shape_decoder_ids=(1,),
        param_shape_required_flags=(1,),
        param_shape_header_required_flags=(0,),
        param_shape_nullable_flags=(0,),
        param_shape_max_lengths=(32,),
        param_shape_lookup_hashes=(123456789,),
        param_shape_header_hashes=(0,),
        program_param_shape_ids=(0,),
        program_transport_kind_ids=(1,),
        proto_names=("http.rest",),
        selector_names=("POST /widgets",),
        op_names=("Widget.create",),
        proto_to_id={"http.rest": 0},
        selector_to_id={"POST /widgets": 0},
        op_to_id={"Widget.create": 0},
        route_to_program=((0,),),
        phase_names=("INGRESS_BEGIN", "HANDLER", "POST_RESPONSE", "ON_ERROR"),
        phase_to_id={
            "INGRESS_BEGIN": 0,
            "HANDLER": 1,
            "POST_RESPONSE": 2,
            "ON_ERROR": 3,
        },
        segment_offsets=(0, 2, 3),
        segment_lengths=(2, 1, 1),
        segment_step_ids=(0, 1, 2, 3),
        segment_phases=("INGRESS_BEGIN", "HANDLER", "POST_RESPONSE"),
        segment_executor_kinds=("sync.extractable", "sync.extractable", "async.direct"),
        segment_catalog_offsets=(0, 2, 3),
        segment_catalog_lengths=(2, 1, 1),
        segment_catalog_atom_ids=(0, 1, 2, 3),
        segment_catalog_phase_ids=(0, 1, 2),
        segment_catalog_executor_kinds=("sync.extractable", "sync.extractable", "async.direct"),
        op_segment_offsets=(0,),
        op_segment_lengths=(3,),
        op_to_segment_ids=(0, 1, 2),
        program_segment_ref_offsets=(0,),
        program_segment_ref_lengths=(3,),
        program_segment_refs=(0, 1, 2),
        program_hot_runner_ids=(1,),
        step_table=(lambda ctx: ctx, lambda ctx: ctx, lambda ctx: ctx, lambda ctx: ctx),
        step_labels=("step0", "step1", "step2", "step3"),
        numba_effect_ids=(0, 1, 2, 3),
        numba_effect_payloads=((0,), (1,), (2,), (3,)),
        step_async_flags=(False, False, False, True),
        rest_exact_route_to_program={("POST", "/widgets"): 0},
        hot_op_plans=(hot_op_plan,),
        error_profile_offsets=(0,),
        error_profile_lengths=(1,),
        error_profile_phase_ids=(3,),
        error_profile_segment_ref_offsets=(0,),
        error_profile_segment_ref_lengths=(1,),
        error_profile_segment_refs=(3,),
        program_error_profile_ids=(0,),
        phase_tree_nodes=(),
        program_phase_tree_offsets=(0,),
        program_phase_tree_lengths=(0,),
    )


def _template_heavy_packed_kernel() -> PackedKernel:
    hot_op_plans = tuple(
        HotOpPlan(
            program_id=idx,
            alias=f"Widget.create.{idx}",
            target="create",
            ordered_segment_ids=(0, 1, 2),
            remaining_segment_ids=(),
            fusible_sync_segment_ids=(0, 1, 2),
            nonfusible_segment_ids=(),
            error_segment_ids={},
            dispatch_proto_ids=(0,),
        dispatch_selector_count=1,
        program_hot_runner_id=1,
        param_shape_id=0,
        transport_kind_id=1,
    )
        for idx in range(10)
    )
    return PackedKernel(
        atom_catalog_labels=("step0", "step1", "step2"),
        atom_catalog_opcode_ids=(0, 1, 2),
        atom_opcode_keys=("step0", "step1", "step2"),
        atom_catalog_effect_ids=(0, 0, 0),
        atom_catalog_effect_payloads=((), (), ()),
        atom_catalog_async_flags=(False, False, False),
        proto_names=("http.rest",),
        selector_names=tuple(f"POST /widgets/{idx}" for idx in range(10)),
        op_names=tuple(f"Widget.create.{idx}" for idx in range(10)),
        proto_to_id={"http.rest": 0},
        selector_to_id={f"POST /widgets/{idx}": idx for idx in range(10)},
        op_to_id={f"Widget.create.{idx}": idx for idx in range(10)},
        route_to_program=(tuple(range(10)),),
        phase_names=("INGRESS_BEGIN", "HANDLER", "POST_RESPONSE"),
        phase_to_id={"INGRESS_BEGIN": 0, "HANDLER": 1, "POST_RESPONSE": 2},
        segment_offsets=(0, 1, 2),
        segment_lengths=(1, 1, 1),
        segment_step_ids=(0, 1, 2),
        segment_phases=("INGRESS_BEGIN", "HANDLER", "POST_RESPONSE"),
        segment_executor_kinds=("sync.extractable", "sync.extractable", "sync.extractable"),
        segment_catalog_offsets=(0, 1, 2),
        segment_catalog_lengths=(1, 1, 1),
        segment_catalog_atom_ids=(0, 1, 2),
        segment_catalog_phase_ids=(0, 1, 2),
        segment_catalog_executor_kinds=("sync.extractable", "sync.extractable", "sync.extractable"),
        op_segment_offsets=tuple(idx * 3 for idx in range(10)),
        op_segment_lengths=(3,) * 10,
        op_to_segment_ids=(0, 1, 2) * 10,
        program_segment_ref_offsets=tuple(idx * 3 for idx in range(10)),
        program_segment_ref_lengths=(3,) * 10,
        program_segment_refs=(0, 1, 2) * 10,
        program_hot_runner_ids=(1,) * 10,
        step_table=(lambda ctx: ctx, lambda ctx: ctx, lambda ctx: ctx),
        step_labels=("step0", "step1", "step2"),
        numba_effect_ids=(0, 0, 0),
        numba_effect_payloads=((), (), ()),
        step_async_flags=(False, False, False),
        rest_exact_route_to_program={
            ("POST", f"/widgets/{idx}"): idx for idx in range(10)
        },
        hot_op_plans=hot_op_plans,
        error_profile_offsets=(),
        error_profile_lengths=(),
        error_profile_phase_ids=(),
        error_profile_segment_ref_offsets=(),
        error_profile_segment_ref_lengths=(),
        error_profile_segment_refs=(),
        program_error_profile_ids=(),
        phase_tree_nodes=(),
        program_phase_tree_offsets=(0,) * 10,
        program_phase_tree_lengths=(0,) * 10,
    )


def test_packed_kernel_measurement_is_deterministic() -> None:
    packed = _sample_packed_kernel()

    first = measure_packed_kernel(packed)
    second = measure_packed_kernel(packed)

    assert first.raw_bytes == second.raw_bytes
    assert first.compressed_bytes == second.compressed_bytes
    assert first.segment_count == 3
    assert first.step_count == 4
    assert first.selector_count == 1
    assert first.proto_count == 1
    assert first.exact_route_count == 1
    assert first.fusible_sync_segment_count == 2
    assert first.compact_step_count <= first.step_count
    assert first.compact_segment_count <= first.segment_count
    assert first.max_index_width_bits == 16
    assert first.shared_error_profile_count == 1


def test_packed_kernel_measurement_view_and_serialization_are_stable() -> None:
    packed = _sample_packed_kernel()

    view = build_packed_kernel_measurement_view(packed)
    serialized_a = serialize_packed_kernel_measurement_view(packed)
    serialized_b = serialize_packed_kernel_measurement_view(packed)
    loaded = load_packed_kernel_hot_block(serialized_a)

    assert view["route_shape"]["exact_route_count"] == 1
    assert view["hot_op_plans"][0]["dispatch_selector_count"] == 1
    assert view["compact_image"]["compact_step_count"] >= 1
    assert serialized_a == serialized_b
    assert serialized_a.startswith(b"TGPKHOT1")
    assert b"step0" not in serialized_a
    assert loaded["atom_opcode_ids"] == (0, 1, 2, 3)
    assert loaded["program_hot_runner_ids"] == (1,)
    assert loaded["program_param_shape_ids"] == (0,)
    assert loaded["param_shape_slot_ids"] == (0,)
    assert loaded["segment_count"] == len(loaded["segment_phase_ids"])


def test_hot_block_uses_program_segment_templates_when_reuse_is_high() -> None:
    packed = _template_heavy_packed_kernel()

    serialized = serialize_packed_kernel_measurement_view(packed)
    loaded = load_packed_kernel_hot_block(serialized)

    assert loaded["program_segment_template_ids"] == (0,) * 10
    assert loaded["template_segment_lengths"] == (3,)
    assert loaded["template_segment_refs"] == (0, 1, 2)
    assert loaded["program_segment_offsets"] == tuple(idx * 3 for idx in range(10))
    assert loaded["program_segment_lengths"] == (3,) * 10
    assert loaded["program_segment_refs"] == (0, 1, 2) * 10
