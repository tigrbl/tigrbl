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

