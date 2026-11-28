from __future__ import annotations

from collections.abc import Iterator, Mapping as ABCMapping
from dataclasses import dataclass, field
from typing import Any, Mapping


_LAZY_MISSING = object()


@dataclass(slots=True)
class HotCtx:
    scope_type: str = ""
    method: str = ""
    path: str = ""
    protocol: str = ""
    selector: str = ""
    proto_id: int = -1
    selector_id: int = -1
    program_id: int = -1
    route_protocol: str = ""
    route_selector: str = ""
    route_program_id: int = -1
    route_opmeta_index: int = -1
    route_method_not_allowed: bool = False
    route_short_circuit: bool = False
    dispatch_binding_protocol: str = ""
    dispatch_binding_selector: str = ""
    dispatch_channel_protocol: str = ""
    dispatch_channel_selector: str = ""
    dispatch_jsonrpc_request_id: Any = None
    dispatch_rpc_method: str | None = None
    egress_sent: bool = False
    content_type: str = ""
    status_code: int = 200
    raw_scope: dict[str, Any] | None = None
    raw_receive: Any = None
    raw_send: Any = None
    raw_headers: tuple[tuple[bytes, bytes], ...] | None = None
    raw_query_string: bytes = b""
    body_view: memoryview | None = None
    body_bytes: bytes | None = None
    parsed_json: Any = None
    parsed_json_loaded: bool = False
    body_hashed_items: dict[int, Any] | None = None
    header_hashed_pairs: tuple[tuple[int, bytes], ...] | None = None
    query_hashed_spans: tuple[tuple[int, int, int, int], ...] | None = None
    path_params: dict[str, Any] | None = None
    route_payload: dict[str, Any] | None = None
    route_path_params: dict[str, Any] | None = None
    route_rpc_envelope: dict[str, Any] | None = None
    dispatch_rpc_envelope: dict[str, Any] | None = None
    egress_transport_response: dict[str, Any] | None = None
    slot_values: list[Any] | None = None
    slot_present: bytearray | None = None
    slot_field_names: tuple[str, ...] = ()
    slot_field_index: dict[str, int] | None = None
    param_shape_id: int = -1
    transport_kind_id: int = 0
    compiled_input_ready: bool = False
    compiled_in_invalid: bool | None = None
    compiled_in_errors: tuple[dict[str, Any], ...] | None = None
    compiled_in_coerced: tuple[str, ...] = ()
    assembled_slot_values: list[Any] | None = None
    assembled_slot_present: bytearray | None = None
    virtual_slot_values: list[Any] | None = None
    virtual_slot_present: bytearray | None = None
    in_values_view: Mapping[str, Any] | None = None
    in_present_names: tuple[str, ...] = ()
    assembled_values_view: Mapping[str, Any] | None = None
    virtual_in_view: Mapping[str, Any] | None = None
    absent_fields: tuple[str, ...] = ()
    used_default_factory: tuple[str, ...] = ()
    lazy_published: bool = False
    headers: dict[str, str] | None = None
    query: dict[str, Any] | None = None
    flags: dict[str, Any] = field(default_factory=dict)


class _HotSlotMap(ABCMapping[str, Any]):
    __slots__ = ("_field_names", "_field_index", "_slot_values", "_slot_present")

    def __init__(
        self,
        field_names: tuple[str, ...],
        field_index: Mapping[str, int] | None,
        slot_values: list[Any],
        slot_present: bytearray,
    ) -> None:
        self._field_names = field_names
        self._field_index = field_index
        self._slot_values = slot_values
        self._slot_present = slot_present

    def __getitem__(self, key: str) -> Any:
        field_index = self._field_index
        if field_index is not None:
            idx = field_index.get(key, -1)
            if 0 <= idx < len(self._slot_present) and self._slot_present[idx]:
                return self._slot_values[idx]
            raise KeyError(key)
        for idx, field_name in enumerate(self._field_names):
            if (
                field_name == key
                and idx < len(self._slot_present)
                and self._slot_present[idx]
            ):
                return self._slot_values[idx]
        raise KeyError(key)

    def __iter__(self) -> Iterator[str]:
        for idx, field_name in enumerate(self._field_names):
            if idx < len(self._slot_present) and self._slot_present[idx]:
                yield field_name

    def __len__(self) -> int:
        return sum(1 for present in self._slot_present if present)

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self[key]
        except KeyError:
            return default

    def __setitem__(self, key: str, value: Any) -> None:
        field_index = self._field_index
        idx = -1
        if field_index is not None:
            idx = field_index.get(key, -1)
        else:
            for candidate_idx, field_name in enumerate(self._field_names):
                if field_name == key:
                    idx = candidate_idx
                    break
        if not (0 <= idx < len(self._slot_present)):
            raise KeyError(key)
        self._slot_values[idx] = value
        self._slot_present[idx] = 1

    def __delitem__(self, key: str) -> None:
        field_index = self._field_index
        idx = -1
        if field_index is not None:
            idx = field_index.get(key, -1)
        else:
            for candidate_idx, field_name in enumerate(self._field_names):
                if field_name == key:
                    idx = candidate_idx
                    break
        if not (0 <= idx < len(self._slot_present)):
            raise KeyError(key)
        self._slot_values[idx] = None
        self._slot_present[idx] = 0


def _slot_dict(
    field_names: tuple[str, ...],
    slot_values: list[Any] | None,
    slot_present: bytearray | None,
) -> dict[str, Any]:
    if not slot_values or slot_present is None:
        return {}
    return {
        field_names[idx]: slot_values[idx]
        for idx in range(min(len(field_names), len(slot_present), len(slot_values)))
        if slot_present[idx]
    }


def _ensure_hot_in_values_view(hot: HotCtx) -> Mapping[str, Any] | None:
    view = hot.in_values_view
    if view is not None:
        return view
    slot_values = hot.slot_values
    slot_present = hot.slot_present
    if slot_values is None or slot_present is None or not hot.slot_field_names:
        return None
    view = _HotSlotMap(
        hot.slot_field_names,
        hot.slot_field_index,
        slot_values,
        slot_present,
    )
    hot.in_values_view = view
    return view


def _ensure_hot_assembled_values_view(hot: HotCtx) -> Mapping[str, Any] | None:
    view = hot.assembled_values_view
    if view is not None:
        return view
    if hot.assembled_slot_values is None or hot.assembled_slot_present is None:
        return None
    view = _slot_dict(
        hot.slot_field_names,
        hot.assembled_slot_values,
        hot.assembled_slot_present,
    )
    hot.assembled_values_view = view
    return view


def _ensure_hot_virtual_in_view(hot: HotCtx) -> Mapping[str, Any] | None:
    view = hot.virtual_in_view
    if view is not None:
        return view
    if hot.virtual_slot_values is None or hot.virtual_slot_present is None:
        return None
    view = _slot_dict(
        hot.slot_field_names,
        hot.virtual_slot_values,
        hot.virtual_slot_present,
    )
    hot.virtual_in_view = view
    return view


__all__ = [
    "HotCtx",
    "_HotSlotMap",
    "_LAZY_MISSING",
    "_ensure_hot_assembled_values_view",
    "_ensure_hot_in_values_view",
    "_ensure_hot_virtual_in_view",
    "_slot_dict",
]
