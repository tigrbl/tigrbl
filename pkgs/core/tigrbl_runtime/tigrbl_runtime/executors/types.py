# tigrbl/runtime/executor/types.py
from __future__ import annotations

from collections.abc import Iterator, Mapping as ABCMapping
from dataclasses import MISSING, dataclass, field, fields, is_dataclass
from functools import lru_cache
from typing import (
    Any,
    Awaitable,
    Callable,
    Mapping,
    MutableMapping,
    Optional,
    Protocol,
    Sequence,
    Union,
    runtime_checkable,
)

try:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import Session
except Exception:  # pragma: no cover - optional ORM dependency for runtime typing
    AsyncSession = Session = Any  # type: ignore[assignment]
from tigrbl_base._base import AttrDict
from tigrbl_atoms.types import BaseCtx


@runtime_checkable
class Request(Protocol):
    state: Any


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


_LAZY_MISSING = object()


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
            if field_name == key and idx < len(self._slot_present) and self._slot_present[idx]:
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


def _coerce_optional_dict(value: Any) -> dict[str, Any] | None:
    if isinstance(value, dict):
        return value
    if isinstance(value, ABCMapping):
        return dict(value)
    return None


def _namespace_lazy_value(kind: str, hot: HotCtx, key: str) -> Any:
    if kind == "route":
        if key == "selector":
            value = hot.route_selector
            return value if value else _LAZY_MISSING
        if key == "protocol":
            value = hot.route_protocol
            return value if value else _LAZY_MISSING
        if key == "program_id":
            value = hot.route_program_id if hot.route_program_id >= 0 else hot.program_id
            return value if value >= 0 else _LAZY_MISSING
        if key == "opmeta_index":
            value = (
                hot.route_opmeta_index
                if hot.route_opmeta_index >= 0
                else hot.route_program_id
            )
            return value if value >= 0 else _LAZY_MISSING
        if key == "method_not_allowed":
            return True if hot.route_method_not_allowed else _LAZY_MISSING
        if key == "short_circuit":
            return True if hot.route_short_circuit else _LAZY_MISSING
        if key == "payload":
            if hot.route_payload is not None:
                return hot.route_payload
            value = _ensure_hot_in_values_view(hot)
            return value if value is not None else _LAZY_MISSING
        if key == "path_params":
            value = hot.route_path_params or hot.path_params
            return value if value is not None else _LAZY_MISSING
        if key == "rpc_envelope":
            value = hot.route_rpc_envelope or hot.dispatch_rpc_envelope
            return value if value is not None else _LAZY_MISSING
        return _LAZY_MISSING
    if kind == "dispatch":
        if key == "binding_protocol":
            value = hot.dispatch_binding_protocol
            return value if value else _LAZY_MISSING
        if key == "binding_selector":
            value = hot.dispatch_binding_selector
            return value if value else _LAZY_MISSING
        if key == "channel_protocol":
            value = hot.dispatch_channel_protocol
            return value if value else _LAZY_MISSING
        if key == "channel_selector":
            value = hot.dispatch_channel_selector
            return value if value else _LAZY_MISSING
        if key in {"normalized_input", "parsed_payload"}:
            value = _ensure_hot_in_values_view(hot)
            return value if value is not None else _LAZY_MISSING
        if key == "rpc":
            value = hot.dispatch_rpc_envelope or hot.route_rpc_envelope
            return value if value is not None else _LAZY_MISSING
        if key == "rpc_method":
            value = hot.dispatch_rpc_method
            return value if value is not None else _LAZY_MISSING
        return _LAZY_MISSING
    if kind == "egress":
        if key == "transport_response":
            value = hot.egress_transport_response
            return value if value is not None else _LAZY_MISSING
        if key == "sent":
            return True if hot.egress_sent else _LAZY_MISSING
        return _LAZY_MISSING
    return _LAZY_MISSING


def _sync_hot_namespace_value(kind: str, hot: HotCtx, key: str, value: Any) -> None:
    if kind == "route":
        if key == "selector" and isinstance(value, str):
            hot.route_selector = value
        elif key == "protocol" and isinstance(value, str):
            hot.route_protocol = value
        elif key == "program_id" and isinstance(value, int):
            hot.route_program_id = value
            hot.program_id = value
        elif key == "opmeta_index" and isinstance(value, int):
            hot.route_opmeta_index = value
            if hot.route_program_id < 0:
                hot.route_program_id = value
            if hot.program_id < 0:
                hot.program_id = value
        elif key == "method_not_allowed":
            hot.route_method_not_allowed = bool(value)
        elif key == "short_circuit":
            hot.route_short_circuit = bool(value)
        elif key == "payload":
            hot.route_payload = _coerce_optional_dict(value)
        elif key == "path_params":
            path_params = _coerce_optional_dict(value)
            hot.route_path_params = path_params
            hot.path_params = path_params
        elif key == "rpc_envelope":
            envelope = _coerce_optional_dict(value)
            hot.route_rpc_envelope = envelope
            if envelope is not None:
                hot.dispatch_jsonrpc_request_id = envelope.get("id")
                method = envelope.get("method")
                hot.dispatch_rpc_method = method if isinstance(method, str) else None
    elif kind == "dispatch":
        if key == "binding_protocol" and isinstance(value, str):
            hot.dispatch_binding_protocol = value
        elif key == "binding_selector" and isinstance(value, str):
            hot.dispatch_binding_selector = value
        elif key == "channel_protocol" and isinstance(value, str):
            hot.dispatch_channel_protocol = value
        elif key == "channel_selector" and isinstance(value, str):
            hot.dispatch_channel_selector = value
        elif key == "rpc":
            envelope = _coerce_optional_dict(value)
            hot.dispatch_rpc_envelope = envelope
            if envelope is not None:
                hot.dispatch_jsonrpc_request_id = envelope.get("id")
                method = envelope.get("method")
                hot.dispatch_rpc_method = method if isinstance(method, str) else None
        elif key == "rpc_method":
            hot.dispatch_rpc_method = value if isinstance(value, str) else None
        elif key in {"normalized_input", "parsed_payload"}:
            route_payload = _coerce_optional_dict(value)
            if route_payload is not None:
                hot.route_payload = route_payload
        elif key == "jsonrpc_request_id":
            hot.dispatch_jsonrpc_request_id = value
    elif kind == "egress":
        if key == "transport_response":
            hot.egress_transport_response = _coerce_optional_dict(value)
        elif key == "sent":
            hot.egress_sent = bool(value)


def _clear_hot_namespace_value(kind: str, hot: HotCtx, key: str) -> None:
    if kind == "route":
        if key == "selector":
            hot.route_selector = ""
        elif key == "protocol":
            hot.route_protocol = ""
        elif key == "program_id":
            hot.route_program_id = -1
        elif key == "opmeta_index":
            hot.route_opmeta_index = -1
        elif key == "method_not_allowed":
            hot.route_method_not_allowed = False
        elif key == "short_circuit":
            hot.route_short_circuit = False
        elif key == "payload":
            hot.route_payload = None
        elif key == "path_params":
            hot.route_path_params = None
            hot.path_params = None
        elif key == "rpc_envelope":
            hot.route_rpc_envelope = None
            hot.dispatch_jsonrpc_request_id = None
            hot.dispatch_rpc_method = None
    elif kind == "dispatch":
        if key == "binding_protocol":
            hot.dispatch_binding_protocol = ""
        elif key == "binding_selector":
            hot.dispatch_binding_selector = ""
        elif key == "channel_protocol":
            hot.dispatch_channel_protocol = ""
        elif key == "channel_selector":
            hot.dispatch_channel_selector = ""
        elif key == "rpc":
            hot.dispatch_rpc_envelope = None
            hot.dispatch_jsonrpc_request_id = None
            hot.dispatch_rpc_method = None
        elif key == "rpc_method":
            hot.dispatch_rpc_method = None
        elif key == "jsonrpc_request_id":
            hot.dispatch_jsonrpc_request_id = None
    elif kind == "egress":
        if key == "transport_response":
            hot.egress_transport_response = None
        elif key == "sent":
            hot.egress_sent = False


class _HotNamespaceDict(dict[str, Any]):
    __slots__ = ("_kind", "_temp")

    def __init__(self, kind: str, temp: "_HotTemp", initial: Mapping[str, Any] | None = None) -> None:
        super().__init__(initial or {})
        self._kind = kind
        self._temp = temp
        hot = temp._hot_ctx()
        if hot is not None and initial:
            for key, value in initial.items():
                _sync_hot_namespace_value(kind, hot, key, value)

    def _lazy_value(self, key: str) -> Any:
        hot = self._temp._hot_ctx()
        if hot is None:
            return _LAZY_MISSING
        return _namespace_lazy_value(self._kind, hot, key)

    def __setitem__(self, key: str, value: Any) -> None:
        dict.__setitem__(self, key, value)
        hot = self._temp._hot_ctx()
        if hot is not None:
            _sync_hot_namespace_value(self._kind, hot, key, value)

    def __delitem__(self, key: str) -> None:
        dict.__delitem__(self, key)
        hot = self._temp._hot_ctx()
        if hot is not None:
            _clear_hot_namespace_value(self._kind, hot, key)

    def __getitem__(self, key: str) -> Any:
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            value = self._lazy_value(key)
            if value is _LAZY_MISSING:
                raise
            dict.__setitem__(self, key, value)
            return value

    def get(self, key: str, default: Any = None) -> Any:
        if dict.__contains__(self, key):
            return dict.get(self, key, default)
        value = self._lazy_value(key)
        if value is _LAZY_MISSING:
            return default
        dict.__setitem__(self, key, value)
        return value

    def setdefault(self, key: str, default: Any = None) -> Any:
        if dict.__contains__(self, key):
            return dict.__getitem__(self, key)
        self[key] = default
        return default

    def update(self, *args: Any, **kwargs: Any) -> None:
        for mapping in args:
            if isinstance(mapping, ABCMapping):
                for key, value in mapping.items():
                    self[key] = value
            else:
                for key, value in dict(mapping).items():
                    self[key] = value
        for key, value in kwargs.items():
            self[key] = value

    def pop(self, key: str, default: Any = _LAZY_MISSING) -> Any:
        if dict.__contains__(self, key):
            value = dict.pop(self, key)
            hot = self._temp._hot_ctx()
            if hot is not None:
                _clear_hot_namespace_value(self._kind, hot, key)
            return value
        if default is _LAZY_MISSING:
            raise KeyError(key)
        return default

    def __contains__(self, key: object) -> bool:
        if dict.__contains__(self, key):
            return True
        if not isinstance(key, str):
            return False
        return self._lazy_value(key) is not _LAZY_MISSING


class _HotTemp(dict[str, Any]):
    __slots__ = ()

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any] | None) -> "_HotTemp":
        if isinstance(value, cls):
            return value
        temp = cls()
        if value:
            temp.update(value)
        return temp

    def _hot_ctx(self) -> HotCtx | None:
        hot = dict.get(self, "hot_ctx")
        return hot if isinstance(hot, HotCtx) else None

    def _wrap_namespace(self, key: str, value: Any) -> Any:
        if key in {"route", "dispatch", "egress"} and isinstance(value, dict) and not isinstance(
            value, _HotNamespaceDict
        ):
            return _HotNamespaceDict(key, self, value)
        return value

    def _lazy_value(self, key: str) -> Any:
        hot = self._hot_ctx()
        if hot is None:
            return _LAZY_MISSING
        if key in {"route", "dispatch", "egress"}:
            return _HotNamespaceDict(key, self)
        if key == "jsonrpc_request_id":
            if hot.dispatch_jsonrpc_request_id is not None:
                return hot.dispatch_jsonrpc_request_id
            envelope = hot.dispatch_rpc_envelope or hot.route_rpc_envelope
            if envelope is not None and "id" in envelope:
                return envelope["id"]
        if key == "compiled_in_values_ready" and hot.compiled_input_ready:
            return True
        if key == "in_values":
            value = _ensure_hot_in_values_view(hot)
            if value is not None:
                return value
        if key == "in_present" and hot.in_present_names:
            return hot.in_present_names
        if key == "assembled_values":
            value = _ensure_hot_assembled_values_view(hot)
            if value is not None:
                return value
        if key == "virtual_in":
            value = _ensure_hot_virtual_in_view(hot)
            if value is not None:
                return value
        if key == "absent_fields" and hot.absent_fields:
            return hot.absent_fields
        if key == "used_default_factory" and hot.used_default_factory:
            return hot.used_default_factory
        if key == "in_invalid" and hot.compiled_in_invalid is not None:
            return hot.compiled_in_invalid
        if key == "in_errors" and hot.compiled_in_errors is not None:
            return [dict(error) for error in hot.compiled_in_errors]
        if key == "in_coerced" and hot.compiled_in_coerced:
            return hot.compiled_in_coerced
        return _LAZY_MISSING

    def __setitem__(self, key: str, value: Any) -> None:
        value = self._wrap_namespace(key, value)
        dict.__setitem__(self, key, value)
        if key == "jsonrpc_request_id":
            hot = self._hot_ctx()
            if hot is not None:
                hot.dispatch_jsonrpc_request_id = value

    def update(self, *args: Any, **kwargs: Any) -> None:
        for mapping in args:
            if isinstance(mapping, ABCMapping):
                for key, value in mapping.items():
                    self[key] = value
            else:
                for key, value in dict(mapping).items():
                    self[key] = value
        for key, value in kwargs.items():
            self[key] = value

    def setdefault(self, key: str, default: Any = None) -> Any:
        if dict.__contains__(self, key):
            return dict.__getitem__(self, key)
        value = self._wrap_namespace(key, default)
        dict.__setitem__(self, key, value)
        return value

    def __getitem__(self, key: str) -> Any:
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            value = self._lazy_value(key)
            if value is _LAZY_MISSING:
                raise
            dict.__setitem__(self, key, value)
            return value

    def get(self, key: str, default: Any = None) -> Any:
        if dict.__contains__(self, key):
            return dict.get(self, key, default)
        value = self._lazy_value(key)
        if value is _LAZY_MISSING:
            return default
        dict.__setitem__(self, key, value)
        return value

    def __contains__(self, key: object) -> bool:
        if dict.__contains__(self, key):
            return True
        if not isinstance(key, str):
            return False
        return self._lazy_value(key) is not _LAZY_MISSING

    def __delitem__(self, key: str) -> None:
        dict.__delitem__(self, key)
        if key == "jsonrpc_request_id":
            hot = self._hot_ctx()
            if hot is not None:
                hot.dispatch_jsonrpc_request_id = None


class _ResponseState:
    """Context-bound response namespace.

    Keeps ``ctx['result']`` synchronized with ``ctx.response.result`` updates so
    POST_RESPONSE hooks can safely shape egress payloads.
    """

    __slots__ = ("_ctx", "_data")

    def __init__(self, ctx: "_Ctx", value: Any = None) -> None:
        object.__setattr__(self, "_ctx", ctx)
        object.__setattr__(self, "_data", {})

        source = getattr(value, "__dict__", None)
        if isinstance(source, dict):
            for key, item in source.items():
                setattr(self, key, item)
        elif value is not None:
            result = getattr(value, "result", None)
            setattr(self, "result", result)

    def __getattr__(self, name: str) -> Any:
        data = object.__getattribute__(self, "_data")
        return data.get(name)

    def __delitem__(self, key: str) -> None:
        if key in self._FIELD_NAMES:
            object.__setattr__(self, key, None)
            return
        del object.__getattribute__(self, "bag")[key]

    def __setattr__(self, name: str, value: Any) -> None:
        if (
            name == "result"
            and isinstance(value, Mapping)
            and not isinstance(value, AttrDict)
        ):
            value = AttrDict(value)
        data = object.__getattribute__(self, "_data")
        data[name] = value
        if name == "result":
            ctx = object.__getattribute__(self, "_ctx")
            ctx["result"] = value


@runtime_checkable
class _Step(Protocol):
    def __call__(self, ctx: "_Ctx") -> Union[Any, Awaitable[Any]]: ...


HandlerStep = Union[
    _Step,
    Callable[["_Ctx"], Any],
    Callable[["_Ctx"], Awaitable[Any]],
]
PhaseChains = Mapping[str, Sequence[HandlerStep]]


@lru_cache(maxsize=256)
def _promotion_field_plan(
    cls: type[Any],
) -> tuple[tuple[str, ...], frozenset[str]]:
    cls_fields = fields(cls)
    names = tuple(f.name for f in cls_fields)
    required = frozenset(
        f.name
        for f in cls_fields
        if f.default is MISSING and f.default_factory is MISSING
    )
    return names, required


class _Ctx(BaseCtx[Any, Any], MutableMapping[str, Any]):
    """Dict-like runtime context with attribute access and atom promotion support."""

    __slots__ = ()

    _FIELD_NAMES = {
        "env",
        "bag",
        "temp",
        "error",
        "current_phase",
        "error_phase",
        "phase",
        "stage",
        "capability_mask",
        "exact_route",
        "route_family",
        "route_subevents",
        "binding",
        "exchange",
        "tx_scope",
        "plan",
    }
    _BASE_FIELD_NAMES = frozenset(field.name for field in fields(BaseCtx))

    @staticmethod
    def _field_exists(name: str) -> bool:
        return name in _Ctx._BASE_FIELD_NAMES

    def _get_field_value(self, name: str) -> Any:
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return object.__getattribute__(self, "bag").get(name)

    def _set_field_value(self, name: str, value: Any) -> None:
        if name == "temp":
            value = _HotTemp.from_mapping(value if isinstance(value, ABCMapping) else {})
        if self._field_exists(name):
            object.__setattr__(self, name, value)
            return
        object.__getattribute__(self, "bag")[name] = value

    def _hot_ctx(self) -> HotCtx | None:
        temp = object.__getattribute__(self, "temp")
        if isinstance(temp, dict):
            hot = temp.get("hot_ctx")
            return hot if isinstance(hot, HotCtx) else None
        return None

    def _lazy_bag_value(self, name: str, *, cache: bool) -> Any:
        hot = self._hot_ctx()
        if hot is None:
            return _LAZY_MISSING
        if name == "payload":
            value = hot.route_payload
            if value is None:
                parsed = hot.parsed_json
                if isinstance(parsed, dict) and parsed.get("jsonrpc") == "2.0":
                    params = parsed.get("params")
                    if isinstance(params, (Mapping, list)):
                        value = params
                elif isinstance(parsed, (Mapping, list)):
                    value = parsed
            if value is None:
                value = _ensure_hot_in_values_view(hot)
            if value is None:
                return _LAZY_MISSING
        elif name == "path_params":
            value = hot.route_path_params or hot.path_params
            if value is None:
                return _LAZY_MISSING
        else:
            return _LAZY_MISSING
        if cache:
            object.__getattribute__(self, "bag")[name] = value
        return value

    def __getattr__(self, name: str) -> Any:
        bag = object.__getattribute__(self, "bag")
        if name in bag:
            return bag.get(name)
        value = self._lazy_bag_value(name, cache=True)
        return None if value is _LAZY_MISSING else value

    def __contains__(self, key: str) -> bool:
        if key in self._FIELD_NAMES:
            return True
        bag = object.__getattribute__(self, "bag")
        return key in bag or self._lazy_bag_value(key, cache=False) is not _LAZY_MISSING

    def __getitem__(self, key: str) -> Any:
        if key in self._FIELD_NAMES:
            return self._get_field_value(key)
        bag = object.__getattribute__(self, "bag")
        if key == "response" and key not in bag:
            bag[key] = _ResponseState(self)
        if key in bag:
            return bag[key]
        value = self._lazy_bag_value(key, cache=True)
        if value is _LAZY_MISSING:
            raise KeyError(key)
        return value

    def get(self, key: str, default: Any = None) -> Any:
        if key in self._FIELD_NAMES:
            value = self._get_field_value(key)
            return default if value is None else value
        bag = object.__getattribute__(self, "bag")
        if key == "response" and key not in bag:
            bag[key] = _ResponseState(self)
        if key in bag:
            return bag.get(key, default)
        value = self._lazy_bag_value(key, cache=True)
        return default if value is _LAZY_MISSING else value

    def items(self):
        merged = {name: self._get_field_value(name) for name in self._FIELD_NAMES}
        merged.update(object.__getattribute__(self, "bag"))
        return merged.items()

    def keys(self):
        return dict(self.items()).keys()

    def values(self):
        return dict(self.items()).values()

    def __iter__(self):
        return iter(dict(self.items()))

    def __len__(self) -> int:
        return len(dict(self.items()))

    def setdefault(self, key: str, default: Any = None) -> Any:
        return object.__getattribute__(self, "bag").setdefault(key, default)

    def update(self, *args: Any, **kwargs: Any) -> None:
        object.__getattribute__(self, "bag").update(*args, **kwargs)

    def pop(self, key: str, default: Any = None) -> Any:
        return object.__getattribute__(self, "bag").pop(key, default)

    def clear(self) -> None:
        object.__getattribute__(self, "bag").clear()

    def __setitem__(self, key: str, value: Any) -> None:
        if key in self._FIELD_NAMES:
            self._set_field_value(key, value)
            return

        bag = object.__getattribute__(self, "bag")
        if (
            key == "response"
            and value is not None
            and not isinstance(value, _ResponseState)
            and (
                (isinstance(value, Mapping) and "result" in value)
                or hasattr(value, "result")
            )
        ):
            value = _ResponseState(self, value)
        if key == "result":
            response = bag.get("response")
            if isinstance(response, _ResponseState):
                data = object.__getattribute__(response, "_data")
                data["result"] = value
        bag[key] = value

    def __delitem__(self, key: str) -> None:
        if key in self._FIELD_NAMES:
            raise KeyError(key)
        del object.__getattribute__(self, "bag")[key]

    def __setattr__(self, name: str, value: Any) -> None:
        if name in self._FIELD_NAMES:
            self._set_field_value(name, value)
            return
        self.__setitem__(name, value)

    def promote(self, cls: type[Any], /, **updates: object) -> Any:
        """Promote runtime contexts into atom dataclass contexts."""
        if not is_dataclass(cls):
            raise TypeError(f"promote target must be a dataclass type, got {cls!r}")

        field_names, required_names = _promotion_field_plan(cls)
        bag = object.__getattribute__(self, "bag")
        data: dict[str, object] = {}
        missing_required: list[str] = []

        for name in field_names:
            if name in updates:
                continue
            if name in self._FIELD_NAMES:
                data[name] = self._get_field_value(name)
                continue
            if name in bag:
                data[name] = bag[name]
                continue
            if name in required_names:
                missing_required.append(name)

        if missing_required:
            raise TypeError(
                f"cannot promote {type(self).__name__} -> {cls.__name__}; "
                f"missing required fields: {', '.join(missing_required)}"
            )

        data.update(updates)
        return cls(**data)

    @classmethod
    def ensure(
        cls,
        *,
        request: Optional[Request],
        db: Union[Session, AsyncSession, None],
        seed: Optional[MutableMapping[str, Any] | BaseCtx[Any, Any]] = None,
    ) -> "_Ctx":
        if seed is None:
            ctx = cls()
        elif isinstance(seed, _Ctx):
            ctx = seed
        elif isinstance(seed, BaseCtx):
            seed_values = {f.name: getattr(seed, f.name) for f in fields(type(seed))}
            bag = dict(seed_values.pop("bag", {}) or {})
            for key, value in seed_values.items():
                if key in cls._FIELD_NAMES:
                    continue
                bag[key] = value
            ctx = cls(
                env=seed_values.get("env"),
                bag=bag,
                temp=_HotTemp.from_mapping(seed_values.get("temp") or {}),
                error=seed_values.get("error"),
                current_phase=seed_values.get("current_phase"),
                error_phase=seed_values.get("error_phase"),
            )
        else:
            seed_values = dict(seed)
            seed_fields = {
                name: seed_values.pop(name)
                for name in cls._FIELD_NAMES
                if name in seed_values
            }
            ctx = cls(
                env=seed_fields.get("env"),
                bag=seed_values,
                temp=_HotTemp.from_mapping(seed_fields.get("temp") or {}),
                error=seed_fields.get("error"),
                current_phase=seed_fields.get("current_phase"),
                error_phase=seed_fields.get("error_phase"),
            )

        if request is not None:
            ctx.request = request
            state = getattr(request, "state", None)
            if state is not None and getattr(state, "ctx", None) is None:
                try:
                    state.ctx = ctx  # make ctx available to deps
                except Exception:  # pragma: no cover
                    pass
        if db is not None:
            ctx._raw_db = db
            if "db" not in ctx:
                ctx.db = db
        if not isinstance(getattr(ctx, "temp", None), dict):
            ctx.temp = {}
        return ctx


__all__ = ["_Ctx", "HandlerStep", "PhaseChains", "Request", "Session", "AsyncSession"]
