from __future__ import annotations

from collections.abc import Mapping as ABCMapping
from typing import Any, Mapping

from .hot_state import (
    HotCtx,
    _ensure_hot_assembled_values_view,
    _ensure_hot_in_values_view,
    _ensure_hot_virtual_in_view,
    _LAZY_MISSING,
)


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
            value = (
                hot.route_program_id if hot.route_program_id >= 0 else hot.program_id
            )
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

    def __init__(
        self, kind: str, temp: "_HotTemp", initial: Mapping[str, Any] | None = None
    ) -> None:
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
        if (
            key in {"route", "dispatch", "egress"}
            and isinstance(value, dict)
            and not isinstance(value, _HotNamespaceDict)
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


__all__ = [
    "_HotNamespaceDict",
    "_HotTemp",
    "_clear_hot_namespace_value",
    "_coerce_optional_dict",
    "_namespace_lazy_value",
    "_sync_hot_namespace_value",
]
