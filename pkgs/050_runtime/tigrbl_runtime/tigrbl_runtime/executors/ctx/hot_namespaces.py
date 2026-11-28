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
from .hot_namespace_values import (
    _clear_hot_namespace_value,
    _coerce_optional_dict,
    _namespace_lazy_value,
    _sync_hot_namespace_value,
)


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
