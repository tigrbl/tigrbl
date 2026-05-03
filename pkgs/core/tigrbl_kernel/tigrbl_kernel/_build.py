from __future__ import annotations

import datetime as _dt
import decimal as _dc
import logging
import uuid as _uuid
import zlib
from dataclasses import replace
from types import SimpleNamespace
from typing import Any, Dict, List, Mapping

from tigrbl_atoms import StepFn
from tigrbl_atoms.atoms.sys.phase_db import run as _bind_phase_db
from tigrbl_atoms.phases import phase_info
from tigrbl_atoms.types import EdgeTarget, PhaseTreeEdge, PhaseTreeNode, error_phase_for
from tigrbl_typing.phases import normalize_phase

from . import events as _ev
from .atoms import (
    _hook_phase_chains,
    _inject_atoms,
    _inject_pre_tx_dep_atoms,
    _is_persistent,
    _wrap_atom,
)
from .models import HotOpPlan, KernelPlan, OpKey, OpView, PackedKernel
from .measure import (
    load_packed_kernel_hot_block,
    measure_packed_kernel,
    serialize_packed_kernel_measurement_view,
)
from .types import (
    EGRESS_PHASES,
    INGRESS_PHASES,
    LOWER_KIND_ASYNC_DIRECT,
    LOWER_KIND_SPLIT_EXTRACTABLE,
    LOWER_KIND_SYNC_EXTRACTABLE,
)
from .utils import (
    _atom_name,
    _classify_step_lowering,
    _effect_descriptor_for_step,
    _label_step,
    _opspecs,
)

logger = logging.getLogger(__name__)


_PHASE_DB_LABEL = "atom:sys:phase_db@SYS_PHASE_DB_BIND"
_RUNTIME_EXECUTION_ORDER = (
    "INGRESS_BEGIN",
    "INGRESS_PARSE",
    "INGRESS_DISPATCH",
    "PRE_TX_BEGIN",
    "START_TX",
    "PRE_HANDLER",
    "HANDLER",
    "POST_HANDLER",
    "PRE_COMMIT",
    "TX_COMMIT",
    "POST_COMMIT",
    "POST_RESPONSE",
    "EGRESS_SHAPE",
    "EGRESS_FINALIZE",
)
_HOT_RUNNER_GENERIC = 0
_HOT_RUNNER_LINEAR_DIRECT = 1
_HOT_RUNNER_COMPILED_PARAM = 2
_HOT_RUNNER_WS_UNARY_TEXT = 3
_TRANSPORT_KIND_GENERIC = 0
_TRANSPORT_KIND_REST = 1
_TRANSPORT_KIND_JSONRPC = 2
_TRANSPORT_KIND_CHANNEL = 3
_PARAM_SOURCE_BODY = 1
_PARAM_SOURCE_QUERY = 2
_PARAM_SOURCE_PATH = 4
_PARAM_SOURCE_HEADER = 8
_DECODER_NONE = 0
_DECODER_STR = 1
_DECODER_INT = 2
_DECODER_FLOAT = 3
_DECODER_BOOL = 4
_DECODER_UUID = 5
_DECODER_DECIMAL = 6
_DECODER_DATETIME = 7
_DECODER_DATE = 8
_DECODER_TIME = 9
_WS_FAST_PATH_BYPASS_ATOM_NAMES = frozenset(
    {
        "ingress.ctx_init",
        "dispatch.op_resolve",
        "schema.collect_in",
        "handler.custom",
        "sys.handler_persistence",
        "schema.collect_out",
        "wire.build_out",
        "response.headers_from_payload",
        "emit.readtime_alias",
        "wire.dump",
        "out.masking",
        "response.negotiate",
        "response.render",
        "response.template",
        "response.error_to_transport",
        "egress.result_normalize",
        "egress.out_dump",
        "egress.envelope_apply",
        "egress.headers_apply",
        "egress.http_finalize",
        "egress.to_transport_response",
        "egress.asgi_send",
    }
)


def _phase_stamp(self: Any, model: type, alias: str) -> tuple[Any, ...]:
    hooks_root = getattr(model, "hooks", None) or SimpleNamespace()
    alias_ns = getattr(hooks_root, alias, None)
    specs = getattr(getattr(model, "ops", SimpleNamespace()), "by_alias", {})
    sp_list = specs.get(alias) or ()
    sp = sp_list[0] if sp_list else None
    phase_lists = tuple(
        (
            phase,
            id(getattr(alias_ns, phase, None)),
            len(getattr(alias_ns, phase, ()) or ()),
        )
        for phase in _ev.PHASES
    )
    return (
        id(hooks_root),
        id(alias_ns),
        phase_lists,
        id(specs),
        id(sp_list),
        id(sp),
        id(self._atoms()),
    )


def _dedupe_consecutive_steps(steps: list[StepFn]) -> list[StepFn]:
    """Remove adjacent duplicate callables introduced by chain composition."""
    if len(steps) < 2:
        return steps
    deduped: list[StepFn] = [steps[0]]
    last_id = id(steps[0])
    for step in steps[1:]:
        step_id = id(step)
        if step_id == last_id:
            continue
        deduped.append(step)
        last_id = step_id
    if len(deduped) % 2 == 0:
        half = len(deduped) // 2
        lhs = tuple(
            getattr(step, "__tigrbl_label", None) or _label_step(step, "")
            for step in deduped[:half]
        )
        rhs = tuple(
            getattr(step, "__tigrbl_label", None) or _label_step(step, "")
            for step in deduped[half:]
        )
        if lhs == rhs:
            return deduped[:half]
    return deduped


def _phase_db_step() -> StepFn:
    step = _wrap_atom(_bind_phase_db, anchor="SYS_PHASE_DB_BIND")
    setattr(step, "__tigrbl_label", _PHASE_DB_LABEL)
    return step


def _prepend_phase_db_binding(
    chains: Dict[str, List[StepFn]],
    phases: tuple[str, ...] | list[str],
) -> None:
    for phase in phases:
        steps = list(chains.get(phase, ()) or ())
        if steps and getattr(steps[0], "__tigrbl_label", None) == _PHASE_DB_LABEL:
            chains[phase] = steps
            continue
        chains[phase] = [_phase_db_step(), *steps]


def _build_op(self, model: type, alias: str) -> Dict[str, List[StepFn]]:
    from .core import DEFAULT_PHASE_ORDER

    try:
        cache = self._phase_chains.setdefault(model, {})
    except TypeError:
        cache = self._phase_chains_by_id.setdefault(id(model), {})
    stamp = _phase_stamp(self, model, alias)
    cached = cache.get(alias)
    if cached is not None and cached[0] == stamp:
        return cached[1]

    chains = _hook_phase_chains(model, alias)
    specs = getattr(getattr(model, "ops", SimpleNamespace()), "by_alias", {})
    sp_list = specs.get(alias) or ()
    sp = sp_list[0] if sp_list else None
    target = (getattr(sp, "target", alias) or "").lower()
    persist_policy = getattr(sp, "persist", "default")
    persistent = (
        persist_policy != "skip" and target not in {"read", "list"}
    ) or _is_persistent(chains)

    try:
        _inject_atoms(
            chains,
            self._atoms() or (),
            persistent=persistent,
            target=target,
        )
    except Exception:
        logger.exception(
            "kernel: atom injection failed for %s.%s",
            getattr(model, "__name__", model),
            alias,
        )

    _inject_pre_tx_dep_atoms(chains, sp)

    for phase in DEFAULT_PHASE_ORDER:
        chains.setdefault(phase, [])
    phase_db_phases = list(DEFAULT_PHASE_ORDER)
    _prepend_phase_db_binding(chains, phase_db_phases)
    cache[alias] = (stamp, chains)
    return chains


def _build(self, model: type, alias: str) -> Dict[str, List[StepFn]]:
    return self._build_op(model, alias)


def _build_ingress(self, app: Any) -> Dict[str, List[StepFn]]:
    del app
    order = {name: idx for idx, name in enumerate(_ev.all_events_ordered())}
    ingress_atoms: Dict[str, List[tuple[str, Any]]] = {}
    for anchor, run in self._atoms() or ():
        if not _ev.is_valid_event(anchor):
            continue
        phase = _ev.phase_for_event(anchor)
        if phase not in INGRESS_PHASES:
            continue
        ingress_atoms.setdefault(phase, []).append((anchor, run))

    out: Dict[str, List[StepFn]] = {}
    for phase, atoms in ingress_atoms.items():
        ordered = sorted(atoms, key=lambda item: order.get(item[0], 10_000))
        out[phase] = [_wrap_atom(run, anchor=anchor) for anchor, run in ordered]
    for phase in INGRESS_PHASES:
        out.setdefault(phase, [])
    _prepend_phase_db_binding(out, list(INGRESS_PHASES))
    return out


def _build_egress(self, app: Any) -> Dict[str, List[StepFn]]:
    del app
    order = {name: idx for idx, name in enumerate(_ev.all_events_ordered())}
    egress_atoms: Dict[str, List[tuple[str, Any]]] = {}
    for anchor, run in self._atoms() or ():
        if not _ev.is_valid_event(anchor):
            continue
        phase = _ev.phase_for_event(anchor)
        if phase not in EGRESS_PHASES:
            continue
        egress_atoms.setdefault(phase, []).append((anchor, run))

    out: Dict[str, List[StepFn]] = {}
    for phase, atoms in egress_atoms.items():
        ordered = sorted(atoms, key=lambda item: order.get(item[0], 10_000))
        out[phase] = [_wrap_atom(run, anchor=anchor) for anchor, run in ordered]
    for phase in EGRESS_PHASES:
        out.setdefault(phase, [])
    _prepend_phase_db_binding(out, list(EGRESS_PHASES))
    return out


def _plan_labels(self, model: type, alias: str) -> list[str]:
    from .core import DEFAULT_PHASE_ORDER

    labels: list[str] = []
    chains = self._build(model, alias)
    opspec = next(
        (sp for sp in _opspecs(model) if getattr(sp, "alias", None) == alias),
        None,
    )
    persist = getattr(opspec, "persist", "default") != "skip"

    tx_begin = "START_TX:hook:sys:txn:begin@START_TX"
    tx_end = "TX_COMMIT:hook:sys:txn:commit@TX_COMMIT"
    if persist:
        labels.append(tx_begin)

    def _display_phase(phase: str, step_label: str) -> str:
        if phase != "POST_COMMIT":
            return phase
        if "@out:build" in step_label:
            return "POST_HANDLER"
        if "@out:dump" in step_label:
            return "POST_RESPONSE"
        return phase

    for phase in DEFAULT_PHASE_ORDER:
        if phase in {"START_TX", "TX_COMMIT"}:
            continue
        for step in chains.get(phase, ()) or ():
            step_label = _label_step(step, phase)
            if "SYS_PHASE_DB_BIND" in str(step_label):
                continue
            labels.append(f"{_display_phase(phase, step_label)}:{step_label}")

    if persist:
        labels.append(tx_end)

    return labels


def _segment_label(self, program_id: int, phase: str) -> str:
    return f"program:{program_id}:{phase}"


def _structural_atom_signature(
    step: StepFn,
    phase: str,
) -> tuple[str, int, tuple[int, ...], bool]:
    raw_label = getattr(step, "__tigrbl_label", None) or _label_step(step, phase)
    label = str(raw_label)
    label_prefix, marker, label_suffix = label.rpartition("@")
    if marker and str(normalize_phase(label_suffix)) == str(normalize_phase(phase)):
        label = label_prefix
    effect_id, payload = _effect_descriptor_for_step(step)
    is_async = bool(getattr(step, "_tigrbl_is_async", False))
    if not is_async:
        marker = getattr(step, "__code__", None)
        is_async = bool(getattr(marker, "co_flags", 0) & 0x80)
    return (label, effect_id, payload, is_async)


def _structural_atom_opcode_key(step: StepFn, phase: str) -> str:
    atom_name = _atom_name(step)
    if isinstance(atom_name, str) and atom_name:
        return atom_name
    raw_label = getattr(step, "__tigrbl_label", None) or _label_step(step, phase)
    label = str(raw_label)
    label_prefix, marker, _ = label.rpartition("@")
    if marker:
        return label_prefix
    return label


def _stable_name_hash64(value: str, *, lowercase: bool = False) -> int:
    normalized = value.lower() if lowercase else value
    encoded = normalized.encode("utf-8")
    lo = zlib.crc32(encoded) & 0xFFFFFFFF
    hi = zlib.crc32(encoded, 0x9E3779B9) & 0xFFFFFFFF
    return (hi << 32) | lo


def _decoder_id_for_py_type(py_type: object) -> int:
    if py_type is str:
        return _DECODER_STR
    if py_type is int:
        return _DECODER_INT
    if py_type is float:
        return _DECODER_FLOAT
    if py_type is bool:
        return _DECODER_BOOL
    if py_type is _uuid.UUID:
        return _DECODER_UUID
    if py_type is _dc.Decimal:
        return _DECODER_DECIMAL
    if py_type is _dt.datetime:
        return _DECODER_DATETIME
    if py_type is _dt.date:
        return _DECODER_DATE
    if py_type is _dt.time:
        return _DECODER_TIME
    return _DECODER_NONE


def _program_binding_protos(plan: KernelPlan, program_id: int) -> tuple[str, ...]:
    out: list[str] = []
    seen: set[str] = set()
    for opkey, meta_index in plan.opkey_to_meta.items():
        if meta_index != program_id:
            continue
        proto = str(opkey.proto)
        if proto in seen:
            continue
        seen.add(proto)
        out.append(proto)
    return tuple(out)


def _program_transport_kind_id(proto_names: tuple[str, ...]) -> int:
    has_jsonrpc = any(proto.endswith(".jsonrpc") for proto in proto_names)
    has_rest = any(proto.endswith(".rest") for proto in proto_names)
    has_channel = any(proto in {"ws", "wss", "webtransport"} for proto in proto_names)
    families = sum(1 for flag in (has_jsonrpc, has_rest, has_channel) if flag)
    if families > 1:
        return _TRANSPORT_KIND_GENERIC
    if has_jsonrpc:
        return _TRANSPORT_KIND_JSONRPC
    if has_rest:
        return _TRANSPORT_KIND_REST
    if has_channel:
        return _TRANSPORT_KIND_CHANNEL
    return _TRANSPORT_KIND_GENERIC


def _program_path_param_names(plan: KernelPlan, program_id: int) -> frozenset[str]:
    names: set[str] = set()
    for bucket in plan.proto_indices.values():
        if not isinstance(bucket, Mapping):
            continue
        templated = bucket.get("templated")
        if not isinstance(templated, list):
            continue
        for entry in templated:
            if not isinstance(entry, Mapping):
                continue
            if entry.get("meta_index") != program_id:
                continue
            raw_names = entry.get("names")
            if not isinstance(raw_names, (list, tuple)):
                continue
            for name in raw_names:
                if isinstance(name, str) and name:
                    names.add(name)
    return frozenset(names)


def _compile_program_param_shape(
    opview: OpView | None,
    *,
    path_param_names: frozenset[str],
) -> tuple[tuple[int, int, int, int, int, int, int, int], ...]:
    if opview is None:
        return ()
    fields = tuple(getattr(opview.schema_in, "fields", ()) or ())
    by_field = getattr(opview.schema_in, "by_field", {}) or {}
    descriptors: list[tuple[int, int, int, int, int, int, int, int]] = []
    for slot_id, field_name in enumerate(fields):
        if not isinstance(field_name, str):
            continue
        meta = by_field.get(field_name, {}) or {}
        lookup_name = str(meta.get("alias_in") or field_name)
        header_name = meta.get("header_in")
        source_mask = _PARAM_SOURCE_BODY | _PARAM_SOURCE_QUERY
        if field_name in path_param_names or lookup_name in path_param_names:
            source_mask |= _PARAM_SOURCE_PATH
        if isinstance(header_name, str) and header_name:
            source_mask |= _PARAM_SOURCE_HEADER
            header_hash = _stable_name_hash64(header_name, lowercase=True)
        else:
            header_hash = 0
        max_length = meta.get("max_length")
        descriptors.append(
            (
                _stable_name_hash64(lookup_name),
                int(header_hash),
                int(source_mask),
                int(slot_id),
                int(_decoder_id_for_py_type(meta.get("py_type"))),
                1 if bool(meta.get("required")) else 0,
                1 if bool(meta.get("header_required_in")) else 0,
                int(max_length) if isinstance(max_length, int) and max_length > 0 else 0,
            )
        )
    return tuple(descriptors)


def _program_hot_runner_id(
    *,
    proto_names: tuple[str, ...],
    ordered_segments: tuple[int, ...],
    remaining_segments: tuple[int, ...],
    param_shape_id: int,
    transport_kind_id: int,
    websocket_fast_path: bool,
) -> int:
    if websocket_fast_path and (ordered_segments or remaining_segments):
        return _HOT_RUNNER_WS_UNARY_TEXT
    if (
        param_shape_id >= 0
        and (
            transport_kind_id in {_TRANSPORT_KIND_REST, _TRANSPORT_KIND_JSONRPC}
            or any(
                proto.endswith(".rest") or proto.endswith(".jsonrpc")
                for proto in proto_names
            )
        )
        and (ordered_segments or remaining_segments)
    ):
        return _HOT_RUNNER_COMPILED_PARAM
    if ordered_segments or remaining_segments:
        return _HOT_RUNNER_LINEAR_DIRECT
    return _HOT_RUNNER_GENERIC


def _runtime_websocket_fast_path_spec(
    steps: tuple[StepFn, ...],
) -> tuple[str, str, str, str, Any] | None:
    websocket_step: tuple[str, str, str, str, Any] | None = None
    for step in steps:
        atom_name = getattr(step, "__tigrbl_atom_name__", None)
        if bool(getattr(step, "__tigrbl_skip_in_compiled_param", False)) or atom_name == "sys.phase_db":
            continue
        for candidate_run in (step, getattr(step, "__tigrbl_direct_run", None)):
            endpoint = getattr(candidate_run, "__tigrbl_websocket_endpoint__", None)
            if not callable(endpoint):
                continue
            path = getattr(candidate_run, "__tigrbl_websocket_path__", None)
            protocol = getattr(candidate_run, "__tigrbl_websocket_protocol__", None)
            exchange = getattr(candidate_run, "__tigrbl_websocket_exchange__", None)
            framing = getattr(candidate_run, "__tigrbl_websocket_framing__", None)
            exact = bool(getattr(candidate_run, "__tigrbl_websocket_exact__", False))
            if (
                exact
                and isinstance(path, str)
                and path
                and isinstance(protocol, str)
                and protocol in {"ws", "wss"}
                and isinstance(framing, str)
                and framing == "text"
            ):
                candidate = (
                    path,
                    protocol,
                    str(exchange or "bidirectional_stream"),
                    framing,
                    endpoint,
                )
                if websocket_step is None:
                    websocket_step = candidate
                    break
                if websocket_step != candidate:
                    return None
                break
            return None
        if websocket_step is not None and any(
            callable(getattr(candidate_run, "__tigrbl_websocket_endpoint__", None))
            for candidate_run in (step, getattr(step, "__tigrbl_direct_run", None))
        ):
            continue
        if atom_name in {"dep.security", "dep.extra"} and not bool(
            getattr(step, "__tigrbl_has_direct_dep", True)
        ):
            continue
        if atom_name in _WS_FAST_PATH_BYPASS_ATOM_NAMES:
            continue
        return None
    return websocket_step


def _build_route_matrix(
    self,
    *,
    proto_names: tuple[str, ...],
    selector_names: tuple[str, ...],
    opkey_to_meta: Mapping[OpKey, int],
) -> tuple[tuple[int, ...], ...]:
    proto_to_id = {name: idx for idx, name in enumerate(proto_names)}
    selector_to_id = {name: idx for idx, name in enumerate(selector_names)}
    matrix = [[-1 for _ in selector_names] for _ in proto_names]
    for key, meta_index in opkey_to_meta.items():
        proto_id = proto_to_id.get(key.proto)
        selector_id = selector_to_id.get(key.selector)
        if proto_id is None or selector_id is None:
            continue
        matrix[proto_id][selector_id] = int(meta_index)
    return tuple(tuple(row) for row in matrix)


def _stage_name(value: Any) -> str | None:
    return getattr(value, "__name__", None) if value is not None else None


def _phase_tree_nodes_for_program(
    *,
    program_id: int,
    segment_ids: tuple[int, ...],
    segment_phases: tuple[str, ...],
) -> tuple[PhaseTreeNode, ...]:
    phase_to_segments: dict[str, list[int]] = {}
    ordered_phases: list[str] = []
    for seg_id in segment_ids:
        phase = str(normalize_phase(segment_phases[seg_id]))
        if phase.startswith("ON_") or phase == "TX_ROLLBACK":
            continue
        if phase not in phase_to_segments:
            phase_to_segments[phase] = []
            ordered_phases.append(phase)
        phase_to_segments[phase].append(seg_id)

    nodes: list[PhaseTreeNode] = []
    for idx, phase in enumerate(ordered_phases):
        node_id = f"program:{program_id}:{phase}"
        next_node_id = (
            f"program:{program_id}:{ordered_phases[idx + 1]}"
            if idx + 1 < len(ordered_phases)
            else None
        )
        try:
            pinfo = phase_info(phase)  # type: ignore[arg-type]
            stage_in = _stage_name(pinfo.stage_in)
            stage_out = _stage_name(pinfo.stage_out)
            rollback_required = bool(pinfo.in_tx)
        except Exception:
            stage_in = None
            stage_out = None
            rollback_required = False

        err_phase = error_phase_for(phase)
        err_target = (
            EdgeTarget.rollback("TX_ROLLBACK", fallback=err_phase)
            if rollback_required
            else EdgeTarget.node(err_phase)
        )
        nodes.append(
            PhaseTreeNode(
                node_id=node_id,
                phase=phase,
                stage_in=stage_in,
                stage_out=stage_out,
                segment_ids=tuple(phase_to_segments[phase]),
                ok_child=PhaseTreeEdge(
                    kind="ok",
                    target=(
                        EdgeTarget.node(next_node_id)
                        if next_node_id is not None
                        else EdgeTarget.terminal("ok")
                    ),
                ),
                err_child=PhaseTreeEdge(kind="err", target=err_target),
                terminal_behavior="continue" if next_node_id is not None else "terminal",
                linear_index=idx,
            )
        )
    return tuple(nodes)


def _pack_kernel_plan(
    self,
    plan: KernelPlan,
    *,
    opviews: tuple[OpView | None, ...] = (),
    rest_exact_route_to_program: Mapping[tuple[str, str], int] | None = None,
) -> PackedKernel:
    from .core import DEFAULT_PHASE_ORDER

    selector_names = tuple(sorted({key.selector for key in plan.opkey_to_meta.keys()}))
    proto_names = tuple(sorted(plan.proto_indices.keys()))
    op_names = tuple(
        f"{getattr(meta.model, '__name__', None) or getattr(meta.model, 'model_ref', None) or str(meta.model)}.{meta.alias}"
        for meta in plan.opmeta
    )

    proto_to_id = {name: idx for idx, name in enumerate(proto_names)}
    selector_to_id = {name: idx for idx, name in enumerate(selector_names)}
    op_to_id = {name: idx for idx, name in enumerate(op_names)}

    phase_names: tuple[str, ...] = tuple(
        str(normalize_phase(phase)) for phase in DEFAULT_PHASE_ORDER
    )
    phase_to_id = {name: idx for idx, name in enumerate(phase_names)}

    param_shape_index: dict[
        tuple[tuple[int, int, int, int, int, int, int, int], ...], int
    ] = {}
    param_shape_offsets: list[int] = []
    param_shape_lengths: list[int] = []
    param_shape_source_masks: list[int] = []
    param_shape_slot_ids: list[int] = []
    param_shape_decoder_ids: list[int] = []
    param_shape_required_flags: list[int] = []
    param_shape_header_required_flags: list[int] = []
    param_shape_nullable_flags: list[int] = []
    param_shape_max_lengths: list[int] = []
    param_shape_lookup_hashes: list[int] = []
    param_shape_header_hashes: list[int] = []
    program_param_shape_ids: list[int] = []
    program_transport_kind_ids: list[int] = []

    for program_id, _meta in enumerate(plan.opmeta):
        program_proto_names = _program_binding_protos(plan, program_id)
        transport_kind_id = _program_transport_kind_id(program_proto_names)
        program_transport_kind_ids.append(transport_kind_id)
        program_path_names = _program_path_param_names(plan, program_id)
        opview = opviews[program_id] if program_id < len(opviews) else None
        shape = _compile_program_param_shape(
            opview,
            path_param_names=program_path_names,
        )
        if not shape:
            program_param_shape_ids.append(-1)
            continue
        param_shape_id = param_shape_index.get(shape)
        if param_shape_id is None:
            param_shape_id = len(param_shape_offsets)
            param_shape_index[shape] = param_shape_id
            param_shape_offsets.append(len(param_shape_slot_ids))
            param_shape_lengths.append(len(shape))
            for (
                lookup_hash,
                header_hash,
                source_mask,
                slot_id,
                decoder_id,
                required_flag,
                header_required_flag,
                max_length,
            ) in shape:
                param_shape_lookup_hashes.append(lookup_hash)
                param_shape_header_hashes.append(header_hash)
                param_shape_source_masks.append(source_mask)
                param_shape_slot_ids.append(slot_id)
                param_shape_decoder_ids.append(decoder_id)
                param_shape_required_flags.append(required_flag)
                param_shape_header_required_flags.append(header_required_flag)
                nullable = bool(
                    getattr(opview, "schema_in", None)
                    and getattr(opview.schema_in, "by_field", {}).get(
                        getattr(opview.schema_in, "fields", ())[slot_id], {}
                    ).get("nullable", True)
                )
                param_shape_nullable_flags.append(1 if nullable else 0)
                param_shape_max_lengths.append(max_length)
        program_param_shape_ids.append(param_shape_id)

    atom_index: dict[tuple[str, int, tuple[int, ...], bool], int] = {}
    atom_opcode_index: dict[str, int] = {}
    step_table: list[StepFn] = []
    atom_catalog_labels: list[str] = []
    atom_catalog_opcode_ids: list[int] = []
    atom_opcode_keys: list[str] = []
    effect_ids: list[int] = []
    effect_payloads: list[tuple[int, ...]] = []
    step_async_flags: list[bool] = []

    segment_index: dict[tuple[tuple[int, ...], int, str], int] = {}
    segment_offsets: list[int] = []
    segment_lengths: list[int] = []
    segment_step_ids: list[int] = []
    segment_phases: list[str] = []
    segment_executor_kinds: list[str] = []

    op_segment_offsets: list[int] = []
    op_segment_lengths: list[int] = []
    op_to_segment_ids: list[int] = []

    for program_id, _meta in enumerate(plan.opmeta):
        chains = dict(plan.phase_chains.get(program_id, {}) or {})
        op_segment_offsets.append(len(op_to_segment_ids))
        seg_count = 0
        for phase in DEFAULT_PHASE_ORDER:
            steps = _dedupe_consecutive_steps(list(chains.get(phase, ()) or ()))
            if not steps:
                continue

            kinds = {_classify_step_lowering(step, phase) for step in steps}
            if len(kinds) == 1 and LOWER_KIND_SYNC_EXTRACTABLE in kinds:
                segment_executor_kind = LOWER_KIND_SYNC_EXTRACTABLE
            elif LOWER_KIND_ASYNC_DIRECT in kinds:
                segment_executor_kind = LOWER_KIND_ASYNC_DIRECT
            else:
                segment_executor_kind = LOWER_KIND_SPLIT_EXTRACTABLE

            atom_ids: list[int] = []
            for step in steps:
                signature = _structural_atom_signature(step, phase)
                step_id = atom_index.get(signature)
                if step_id is None:
                    step_id = len(step_table)
                    atom_index[signature] = step_id
                    opcode_key = _structural_atom_opcode_key(step, phase)
                    opcode_id = atom_opcode_index.get(opcode_key)
                    if opcode_id is None:
                        opcode_id = len(atom_opcode_keys)
                        atom_opcode_index[opcode_key] = opcode_id
                        atom_opcode_keys.append(opcode_key)
                    step_table.append(step)
                    atom_catalog_labels.append(signature[0])
                    atom_catalog_opcode_ids.append(opcode_id)
                    effect_ids.append(signature[1])
                    effect_payloads.append(signature[2])
                    step_async_flags.append(signature[3])
                atom_ids.append(step_id)

            normalized_phase = str(normalize_phase(phase))
            phase_id = phase_to_id.get(normalized_phase)
            if phase_id is None:
                phase_id = len(phase_names)
            segment_signature = (tuple(atom_ids), phase_id, segment_executor_kind)
            seg_id = segment_index.get(segment_signature)
            if seg_id is None:
                seg_id = len(segment_offsets)
                segment_index[segment_signature] = seg_id
                segment_offsets.append(len(segment_step_ids))
                segment_lengths.append(len(atom_ids))
                segment_step_ids.extend(atom_ids)
                segment_phases.append(normalized_phase)
                segment_executor_kinds.append(segment_executor_kind)
            seg_count += 1
            op_to_segment_ids.append(seg_id)
        op_segment_lengths.append(seg_count)

    route_to_program = self._build_route_matrix(
        proto_names=proto_names,
        selector_names=selector_names,
        opkey_to_meta=plan.opkey_to_meta,
    )

    hot_op_plans: list[HotOpPlan] = []
    phase_tree_nodes: list[PhaseTreeNode] = []
    program_phase_tree_offsets: list[int] = []
    program_phase_tree_lengths: list[int] = []
    error_profile_index: dict[tuple[tuple[str, tuple[int, ...]], ...], int] = {}
    error_profile_offsets: list[int] = []
    error_profile_lengths: list[int] = []
    error_profile_phase_ids: list[int] = []
    error_profile_segment_ref_offsets: list[int] = []
    error_profile_segment_ref_lengths: list[int] = []
    error_profile_segment_refs: list[int] = []
    program_error_profile_ids: list[int] = []
    program_hot_runner_ids: list[int] = []
    for program_id, _meta in enumerate(plan.opmeta):
        meta = plan.opmeta[program_id]
        seg_offset = op_segment_offsets[program_id]
        seg_length = op_segment_lengths[program_id]
        by_phase: dict[str, list[int]] = {}
        ordered_segments: list[int] = []
        remaining_segments: list[int] = []
        seen_segment_ids: set[int] = set()
        error_segment_ids: dict[str, list[int]] = {}
        fusible_sync_segment_ids: list[int] = []
        nonfusible_segment_ids: list[int] = []
        dispatch_proto_ids: set[int] = set()
        dispatch_selector_count = 0

        for opkey, meta_index in plan.opkey_to_meta.items():
            if meta_index != program_id:
                continue
            proto_id = proto_to_id.get(opkey.proto)
            if proto_id is not None:
                dispatch_proto_ids.add(proto_id)
            dispatch_selector_count += 1

        for idx in range(seg_offset, seg_offset + seg_length):
            seg_id = op_to_segment_ids[idx]
            phase = str(normalize_phase(segment_phases[seg_id]))
            if phase.startswith("ON_") or phase == "TX_ROLLBACK":
                error_segment_ids.setdefault(phase, []).append(seg_id)
                continue
            by_phase.setdefault(phase, []).append(seg_id)

        for phase in _RUNTIME_EXECUTION_ORDER:
            for seg_id in by_phase.pop(phase, ()):
                if seg_id in seen_segment_ids:
                    continue
                seen_segment_ids.add(seg_id)
                ordered_segments.append(seg_id)

        for idx in range(seg_offset, seg_offset + seg_length):
            seg_id = op_to_segment_ids[idx]
            if seg_id in seen_segment_ids:
                continue
            phase = str(normalize_phase(segment_phases[seg_id]))
            if phase.startswith("ON_") or phase == "TX_ROLLBACK":
                continue
            seen_segment_ids.add(seg_id)
            remaining_segments.append(seg_id)

        websocket_fast_path = _runtime_websocket_fast_path_spec(
            tuple(
                step_table[step_id]
                for seg_id in (*ordered_segments, *remaining_segments)
                for step_id in segment_step_ids[
                    segment_offsets[seg_id] : segment_offsets[seg_id] + segment_lengths[seg_id]
                ]
            )
        )

        for seg_id in (*ordered_segments, *remaining_segments):
            if segment_executor_kinds[seg_id] == LOWER_KIND_SYNC_EXTRACTABLE:
                fusible_sync_segment_ids.append(seg_id)
                continue
            nonfusible_segment_ids.append(seg_id)

        program_phase_tree_offsets.append(len(phase_tree_nodes))
        program_nodes = _phase_tree_nodes_for_program(
            program_id=program_id,
            segment_ids=tuple((*ordered_segments, *remaining_segments)),
            segment_phases=tuple(segment_phases),
        )
        phase_tree_nodes.extend(program_nodes)
        program_phase_tree_lengths.append(len(program_nodes))

        error_profile_signature = tuple(
            (phase, tuple(seg_ids))
            for phase, seg_ids in sorted(error_segment_ids.items())
        )
        error_profile_id = error_profile_index.get(error_profile_signature)
        if error_profile_id is None:
            error_profile_id = len(error_profile_offsets)
            error_profile_index[error_profile_signature] = error_profile_id
            error_profile_offsets.append(len(error_profile_phase_ids))
            error_profile_lengths.append(len(error_profile_signature))
            for phase, seg_ids in error_profile_signature:
                normalized_phase = str(normalize_phase(phase))
                phase_id = phase_to_id.get(normalized_phase)
                if phase_id is None:
                    phase_id = len(phase_names)
                error_profile_phase_ids.append(phase_id)
                error_profile_segment_ref_offsets.append(len(error_profile_segment_refs))
                error_profile_segment_ref_lengths.append(len(seg_ids))
                error_profile_segment_refs.extend(seg_ids)
        program_error_profile_ids.append(error_profile_id)
        param_shape_id = (
            program_param_shape_ids[program_id]
            if program_id < len(program_param_shape_ids)
            else -1
        )
        transport_kind_id = (
            program_transport_kind_ids[program_id]
            if program_id < len(program_transport_kind_ids)
            else _TRANSPORT_KIND_GENERIC
        )
        hot_runner_id = _program_hot_runner_id(
            proto_names=program_proto_names,
            ordered_segments=tuple(ordered_segments),
            remaining_segments=tuple(remaining_segments),
            param_shape_id=param_shape_id,
            transport_kind_id=transport_kind_id,
            websocket_fast_path=websocket_fast_path is not None,
        )
        program_hot_runner_ids.append(hot_runner_id)

        hot_op_plans.append(
            HotOpPlan(
                program_id=program_id,
                model=getattr(meta, "model", None),
                alias=str(getattr(meta, "alias", "") or ""),
                target=str(getattr(meta, "target", "") or ""),
                opview=opviews[program_id] if program_id < len(opviews) else None,
                ordered_segment_ids=tuple(ordered_segments),
                remaining_segment_ids=tuple(remaining_segments),
                error_segment_ids={
                    phase: tuple(seg_ids)
                    for phase, seg_ids in error_segment_ids.items()
                },
                fusible_sync_segment_ids=tuple(fusible_sync_segment_ids),
                nonfusible_segment_ids=tuple(nonfusible_segment_ids),
                db_acquire_hint=(
                    "model_get_db"
                    if callable(
                        getattr(getattr(meta, "model", None), "__tigrbl_get_db__", None)
                    )
                    else "resolver"
                ),
                dispatch_proto_ids=tuple(sorted(dispatch_proto_ids)),
                dispatch_selector_count=dispatch_selector_count,
                program_error_profile_id=error_profile_id,
                program_hot_runner_id=hot_runner_id,
                param_shape_id=param_shape_id,
                transport_kind_id=transport_kind_id,
                websocket_path=websocket_fast_path[0] if websocket_fast_path is not None else "",
                websocket_protocol=websocket_fast_path[1] if websocket_fast_path is not None else "",
                websocket_exchange=websocket_fast_path[2] if websocket_fast_path is not None else "",
                websocket_framing=websocket_fast_path[3] if websocket_fast_path is not None else "",
                websocket_direct_endpoint=websocket_fast_path[4] if websocket_fast_path is not None else None,
            )
        )

    packed = PackedKernel(
        proto_names=proto_names,
        selector_names=selector_names,
        op_names=op_names,
        proto_to_id=proto_to_id,
        selector_to_id=selector_to_id,
        op_to_id=op_to_id,
        route_to_program=route_to_program,
        atom_catalog_labels=tuple(atom_catalog_labels),
        atom_catalog_opcode_ids=tuple(atom_catalog_opcode_ids),
        atom_opcode_keys=tuple(atom_opcode_keys),
        atom_catalog_effect_ids=tuple(effect_ids),
        atom_catalog_effect_payloads=tuple(effect_payloads),
        atom_catalog_async_flags=tuple(step_async_flags),
        param_shape_offsets=tuple(param_shape_offsets),
        param_shape_lengths=tuple(param_shape_lengths),
        param_shape_source_masks=tuple(param_shape_source_masks),
        param_shape_slot_ids=tuple(param_shape_slot_ids),
        param_shape_decoder_ids=tuple(param_shape_decoder_ids),
        param_shape_required_flags=tuple(param_shape_required_flags),
        param_shape_header_required_flags=tuple(param_shape_header_required_flags),
        param_shape_nullable_flags=tuple(param_shape_nullable_flags),
        param_shape_max_lengths=tuple(param_shape_max_lengths),
        param_shape_lookup_hashes=tuple(param_shape_lookup_hashes),
        param_shape_header_hashes=tuple(param_shape_header_hashes),
        program_param_shape_ids=tuple(program_param_shape_ids),
        program_transport_kind_ids=tuple(program_transport_kind_ids),
        segment_offsets=tuple(segment_offsets),
        segment_lengths=tuple(segment_lengths),
        segment_step_ids=tuple(segment_step_ids),
        segment_phases=tuple(segment_phases),
        segment_executor_kinds=tuple(segment_executor_kinds),
        segment_catalog_offsets=tuple(segment_offsets),
        segment_catalog_lengths=tuple(segment_lengths),
        segment_catalog_atom_ids=tuple(segment_step_ids),
        segment_catalog_phase_ids=tuple(
            phase_to_id.get(str(normalize_phase(phase)), 0) for phase in segment_phases
        ),
        segment_catalog_executor_kinds=tuple(segment_executor_kinds),
        phase_names=tuple(phase_names),
        phase_to_id=phase_to_id,
        op_segment_offsets=tuple(op_segment_offsets),
        op_segment_lengths=tuple(op_segment_lengths),
        op_to_segment_ids=tuple(op_to_segment_ids),
        program_segment_ref_offsets=tuple(op_segment_offsets),
        program_segment_ref_lengths=tuple(op_segment_lengths),
        program_segment_refs=tuple(op_to_segment_ids),
        program_hot_runner_ids=tuple(program_hot_runner_ids),
        error_profile_offsets=tuple(error_profile_offsets),
        error_profile_lengths=tuple(error_profile_lengths),
        error_profile_phase_ids=tuple(error_profile_phase_ids),
        error_profile_segment_ref_offsets=tuple(error_profile_segment_ref_offsets),
        error_profile_segment_ref_lengths=tuple(error_profile_segment_ref_lengths),
        error_profile_segment_refs=tuple(error_profile_segment_refs),
        program_error_profile_ids=tuple(program_error_profile_ids),
        step_table=tuple(step_table),
        step_labels=tuple(atom_catalog_labels),
        numba_effect_ids=tuple(effect_ids),
        numba_effect_payloads=tuple(effect_payloads),
        step_async_flags=tuple(step_async_flags),
        rest_exact_route_to_program=dict(rest_exact_route_to_program or {}),
        hot_op_plans=tuple(hot_op_plans),
        phase_tree_nodes=tuple(phase_tree_nodes),
        program_phase_tree_offsets=tuple(program_phase_tree_offsets),
        program_phase_tree_lengths=tuple(program_phase_tree_lengths),
        executor_kind="python",
    )
    build_python_executor = getattr(self, "_build_python_packed_executor", None)
    build_numba_executor = getattr(self, "_build_numba_packed_executor", None)
    measured = replace(
        packed,
        executor=build_python_executor(packed)
        if callable(build_python_executor)
        else None,
        numba_executor=build_numba_executor(packed)
        if callable(build_numba_executor)
        else None,
    )
    hot_block_bytes = serialize_packed_kernel_measurement_view(measured)
    hot_block_view = load_packed_kernel_hot_block(hot_block_bytes)
    measured = replace(
        measured,
        hot_block_bytes=hot_block_bytes,
        hot_block_view=hot_block_view,
    )
    return replace(measured, measurement=measure_packed_kernel(measured))


def _compile_bootstrap_plan(self, app: Any) -> Dict[str, List[StepFn]]:
    return self._build_ingress(app)
