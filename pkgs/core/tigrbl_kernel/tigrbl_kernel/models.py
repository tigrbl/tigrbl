from __future__ import annotations

import struct
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterator, Mapping, Tuple

from tigrbl_atoms.types import PhaseTreeNode

try:
    from tigrbl_typing.phases import MAINLINE_PHASES, ERROR_PHASES, phase_info
except Exception:  # pragma: no cover - compatibility fallback
    MAINLINE_PHASES = ()
    ERROR_PHASES = ()
    phase_info = None


StepFn = Callable[..., Any]


def _label_callable(fn: Any) -> str:
    name = getattr(fn, "__qualname__", getattr(fn, "__name__", repr(fn)))
    module = getattr(fn, "__module__", None)
    return f"{module}.{name}" if module else name


def _label_step(step: Any, phase: str) -> str:
    label = getattr(step, "__tigrbl_label", None)
    if isinstance(label, str) and "@" in label:
        return label
    module = getattr(step, "__module__", "") or ""
    name = getattr(step, "__name__", "") or ""
    if (
        module.startswith("tigrbl_ops_oltp.crud")
        or module.startswith("tigrbl_core.core.crud")
        and name
    ):
        return f"hook:wire:tigrbl:core:crud:ops:{name}@{phase}"
    return f"hook:wire:{_label_callable(step).replace('.', ':')}@{phase}"


@dataclass(frozen=True)
class SchemaIn:
    fields: Tuple[str, ...]
    by_field: Dict[str, Dict[str, object]]


@dataclass(frozen=True)
class SchemaOut:
    fields: Tuple[str, ...]
    by_field: Dict[str, Dict[str, object]]
    expose: Tuple[str, ...]


@dataclass(frozen=True)
class OpView:
    schema_in: SchemaIn
    schema_out: SchemaOut
    paired_index: Dict[str, Dict[str, object]]
    virtual_producers: Dict[str, Callable[[object, dict], object]]
    to_stored_transforms: Dict[str, Callable[[object, dict], object]]
    refresh_hints: Tuple[str, ...]


@dataclass(frozen=True, slots=True)
class OpKey:
    proto: str
    selector: str


@dataclass(frozen=True, slots=True)
class OpMeta:
    model: type
    alias: str
    target: str


@dataclass(frozen=True, slots=True)
class CompiledPhase:
    name: str
    stage_in: object | None
    stage_out: object | None
    in_tx: bool = False
    is_error: bool = False


@dataclass(frozen=True, slots=True)
class PackedSegment:
    id: int
    phase: str
    offset: int
    length: int
    label: str
    executor_kind: str = "python"


@dataclass(frozen=True, slots=True)
class HotOpPlan:
    program_id: int = -1
    model: type | None = None
    alias: str = ""
    target: str = ""
    opview: OpView | None = None
    ordered_segment_ids: tuple[int, ...] = ()
    remaining_segment_ids: tuple[int, ...] = ()
    error_segment_ids: Mapping[str, tuple[int, ...]] = field(default_factory=dict)
    fusible_sync_segment_ids: tuple[int, ...] = ()
    nonfusible_segment_ids: tuple[int, ...] = ()
    db_acquire_hint: str = "resolver"
    dispatch_proto_ids: tuple[int, ...] = ()
    dispatch_selector_count: int = 0
    program_error_profile_id: int = -1
    program_hot_runner_id: int = 0
    param_shape_id: int = -1
    transport_kind_id: int = 0
    compiled_param_phase_steps: tuple[tuple[str, tuple[Any, ...]], ...] = ()
    websocket_path: str = ""
    websocket_protocol: str = ""
    websocket_exchange: str = ""
    websocket_framing: str = ""
    websocket_direct_endpoint: Any = None


@dataclass(frozen=True, slots=True)
class PackedKernelMeasurement:
    raw_bytes: int
    compressed_bytes: int
    segment_count: int
    step_count: int
    phase_tree_node_count: int
    proto_count: int
    selector_count: int
    op_count: int
    route_row_count: int
    route_col_count: int
    route_slot_count: int
    exact_route_count: int
    fusible_sync_segment_count: int
    hot_op_count: int
    compact_step_count: int = 0
    compact_segment_count: int = 0
    compact_program_segment_ref_count: int = 0
    compact_route_entry_count: int = 0
    shared_error_profile_count: int = 0
    externalized_prelude_step_count: int = 0
    max_index_width_bits: int = 0
    measurement_view: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class PackedHotSection:
    name: str
    section_id: int
    width_bits: int
    count: int
    offset: int
    byte_length: int
    buffer: bytes
    signed: bool = False

    @property
    def item_size(self) -> int:
        return max(1, int(self.width_bits) // 8)

    @property
    def end_offset(self) -> int:
        return int(self.offset) + int(self.byte_length)

    @property
    def payload_view(self) -> memoryview:
        return memoryview(self.buffer)[self.offset : self.end_offset]

    def get_int(self, index: int) -> int:
        if not (0 <= index < int(self.count)):
            raise IndexError(index)
        if self.width_bits == 8:
            value = self.buffer[self.offset + index]
            if not self.signed:
                return int(value)
            return int(struct.unpack_from("<b", self.buffer, self.offset + index)[0])
        fmt = {
            (False, 16): "<H",
            (False, 32): "<I",
            (False, 64): "<Q",
            (True, 16): "<h",
            (True, 32): "<i",
        }.get((bool(self.signed), int(self.width_bits)))
        if fmt is None:
            raise ValueError(
                f"unsupported packed hot section width/sign: {self.width_bits}/{self.signed}"
            )
        return int(
            struct.unpack_from(fmt, self.buffer, self.offset + (index * self.item_size))[0]
        )

    def find_bytes(self, marker: bytes, *, start_byte: int = 0) -> int:
        start = int(self.offset) + max(0, int(start_byte))
        found = self.buffer.find(marker, start, self.end_offset)
        if found < 0:
            return -1
        return found - int(self.offset)

    def find_aligned_u64(
        self,
        value: int,
        *,
        start_index: int = 0,
        count: int | None = None,
    ) -> int:
        if self.width_bits != 64:
            raise ValueError("find_aligned_u64 requires a 64-bit unsigned section")
        if start_index < 0:
            start_index = 0
        available = max(0, int(self.count) - int(start_index))
        span = available if count is None else max(0, min(int(count), available))
        if span <= 0:
            return -1
        marker = struct.pack("<Q", int(value) & 0xFFFFFFFFFFFFFFFF)
        search_start = self.offset + (int(start_index) * self.item_size)
        search_end = search_start + (span * self.item_size)
        cursor = search_start
        while cursor < search_end:
            found = self.buffer.find(marker, cursor, search_end)
            if found < 0:
                return -1
            relative = found - self.offset
            if relative % self.item_size == 0:
                return relative // self.item_size
            cursor = found + 1
        return -1


@dataclass(frozen=True, slots=True)
class PackedHotSectionDirectory:
    version: int
    max_width_bits: int
    atom_count: int
    segment_count: int
    program_count: int
    error_profile_count: int
    route_entry_count: int
    sections: Mapping[str, PackedHotSection] = field(default_factory=dict)

    def __getitem__(self, name: str) -> PackedHotSection:
        section = self.get(name)
        if section is None:
            raise KeyError(name)
        return section

    def get(self, name: str) -> PackedHotSection | None:
        section = self.sections.get(name)
        return section if isinstance(section, PackedHotSection) else None


@dataclass(frozen=True, slots=True)
class PackedKernel:
    proto_names: tuple[str, ...] = ()
    selector_names: tuple[str, ...] = ()
    op_names: tuple[str, ...] = ()

    proto_to_id: Mapping[str, int] = field(default_factory=dict)
    selector_to_id: Mapping[str, int] = field(default_factory=dict)
    op_to_id: Mapping[str, int] = field(default_factory=dict)

    route_to_program: Any = None

    atom_catalog_labels: tuple[str, ...] = ()
    atom_catalog_opcode_ids: tuple[int, ...] = ()
    atom_opcode_keys: tuple[str, ...] = ()
    atom_catalog_effect_ids: tuple[int, ...] = ()
    atom_catalog_effect_payloads: tuple[tuple[int, ...], ...] = ()
    atom_catalog_async_flags: tuple[bool, ...] = ()

    param_shape_offsets: tuple[int, ...] = ()
    param_shape_lengths: tuple[int, ...] = ()
    param_shape_source_masks: tuple[int, ...] = ()
    param_shape_slot_ids: tuple[int, ...] = ()
    param_shape_decoder_ids: tuple[int, ...] = ()
    param_shape_required_flags: tuple[int, ...] = ()
    param_shape_header_required_flags: tuple[int, ...] = ()
    param_shape_nullable_flags: tuple[int, ...] = ()
    param_shape_max_lengths: tuple[int, ...] = ()
    param_shape_lookup_hashes: tuple[int, ...] = ()
    param_shape_header_hashes: tuple[int, ...] = ()
    program_param_shape_ids: tuple[int, ...] = ()
    program_transport_kind_ids: tuple[int, ...] = ()

    segment_offsets: tuple[int, ...] = ()
    segment_lengths: tuple[int, ...] = ()
    segment_step_ids: tuple[int, ...] = ()
    segment_phases: tuple[str, ...] = ()
    segment_executor_kinds: tuple[str, ...] = ()

    segment_catalog_offsets: tuple[int, ...] = ()
    segment_catalog_lengths: tuple[int, ...] = ()
    segment_catalog_atom_ids: tuple[int, ...] = ()
    segment_catalog_phase_ids: tuple[int, ...] = ()
    segment_catalog_executor_kinds: tuple[str, ...] = ()

    phase_names: tuple[str, ...] = ()
    phase_to_id: Mapping[str, int] = field(default_factory=dict)

    op_segment_offsets: tuple[int, ...] = ()
    op_segment_lengths: tuple[int, ...] = ()
    op_to_segment_ids: tuple[int, ...] = ()

    program_segment_ref_offsets: tuple[int, ...] = ()
    program_segment_ref_lengths: tuple[int, ...] = ()
    program_segment_refs: tuple[int, ...] = ()
    program_hot_runner_ids: tuple[int, ...] = ()

    error_profile_offsets: tuple[int, ...] = ()
    error_profile_lengths: tuple[int, ...] = ()
    error_profile_phase_ids: tuple[int, ...] = ()
    error_profile_segment_ref_offsets: tuple[int, ...] = ()
    error_profile_segment_ref_lengths: tuple[int, ...] = ()
    error_profile_segment_refs: tuple[int, ...] = ()
    program_error_profile_ids: tuple[int, ...] = ()

    step_table: tuple[StepFn, ...] = ()
    step_labels: tuple[str, ...] = ()

    numba_effect_ids: tuple[int, ...] = ()
    numba_effect_payloads: tuple[tuple[int, ...], ...] = ()
    step_async_flags: tuple[bool, ...] = ()
    rest_exact_route_to_program: Mapping[tuple[str, str], int] = field(
        default_factory=dict
    )
    hot_op_plans: tuple[HotOpPlan, ...] = ()

    phase_tree_nodes: tuple[PhaseTreeNode, ...] = ()
    program_phase_tree_offsets: tuple[int, ...] = ()
    program_phase_tree_lengths: tuple[int, ...] = ()

    ingress_program_id: int = -1
    egress_ok_program_id: int = -1
    egress_err_program_id: int = -1

    executor_kind: str = "python"
    executor: Callable[..., Any] | None = None
    numba_executor: Callable[..., Any] | None = None
    hot_block_bytes: bytes = b""
    hot_block_view: Mapping[str, Any] = field(default_factory=dict)
    hot_block_sections: PackedHotSectionDirectory | None = None
    measurement: PackedKernelMeasurement | None = None


@dataclass(frozen=True, slots=True)
class KernelPlan:
    proto_indices: Mapping[str, Any] = field(default_factory=dict)
    opmeta: tuple[OpMeta, ...] = ()
    opkey_to_meta: Mapping[OpKey, int] = field(default_factory=dict)
    ingress_chain: Mapping[str, list[StepFn]] = field(default_factory=dict)
    phase_chains: Mapping[int, Mapping[str, list[StepFn]]] = field(default_factory=dict)
    egress_chain: Mapping[str, list[StepFn]] = field(default_factory=dict)
    phases: Mapping[str, CompiledPhase] = field(default_factory=dict)
    mainline_phases: tuple[str, ...] = ()
    error_phases: tuple[str, ...] = ()
    phase_trees: Mapping[int, tuple[PhaseTreeNode, ...]] = field(default_factory=dict)
    packed: PackedKernel | None = None
    _appspec_mapping: Dict[str, Dict[str, list[str]]] = field(
        default_factory=dict, init=False, repr=False, compare=False
    )

    def _normalize_mappings(self) -> Dict[str, Dict[str, list[str]]]:
        if self._appspec_mapping:
            return self._appspec_mapping

        phase_order = self.mainline_phases or tuple(self.phases.keys())
        if not phase_order:
            phase_order = tuple(self.ingress_chain.keys()) or tuple()

        normalized: Dict[str, Dict[str, list[str]]] = {}
        for meta_index, meta in enumerate(self.opmeta):
            table_name = getattr(meta.model, "__name__", str(meta.model))
            labels: list[str] = []
            chains = self.phase_chains.get(meta_index, {})
            for phase in phase_order:
                phase_steps = chains.get(phase, ())
                for step in phase_steps or ():
                    labels.append(_label_step(step, phase))

            seen, deduped = set(), []
            for label in labels:
                if ":hook:wire:" in label:
                    if label in seen:
                        continue
                    seen.add(label)
                deduped.append(label)

            normalized.setdefault(table_name, {})[meta.alias] = deduped

        self._appspec_mapping.update(normalized)
        return self._appspec_mapping

    def __getitem__(self, key: str) -> Dict[str, list[str]]:
        return self._normalize_mappings()[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._normalize_mappings())

    def __len__(self) -> int:
        return len(self._normalize_mappings())

    def get(
        self, key: str, default: Dict[str, list[str]] | None = None
    ) -> Dict[str, list[str]] | None:
        return self._normalize_mappings().get(key, default)

    def items(self):
        return self._normalize_mappings().items()

    def keys(self):
        return self._normalize_mappings().keys()

    def values(self):
        return self._normalize_mappings().values()
