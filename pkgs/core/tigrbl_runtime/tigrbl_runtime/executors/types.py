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
    content_type: str = ""
    status_code: int = 200
    raw_scope: Mapping[str, Any] | None = None
    raw_receive: Any = None
    raw_send: Any = None
    raw_headers: tuple[tuple[bytes, bytes], ...] | None = None
    raw_query_string: bytes = b""
    body_view: memoryview | None = None
    body_bytes: bytes | None = None
    parsed_json: Any = None
    parsed_json_loaded: bool = False
    body_hashed_items: Mapping[int, Any] | None = None
    header_hashed_pairs: tuple[tuple[int, bytes], ...] | None = None
    query_hashed_spans: tuple[tuple[int, int, int, int], ...] | None = None
    path_params: Mapping[str, Any] | None = None
    slot_values: list[Any] | None = None
    slot_present: bytearray | None = None
    slot_field_names: tuple[str, ...] = ()
    slot_field_index: Mapping[str, int] | None = None
    param_shape_id: int = -1
    transport_kind_id: int = 0
    compiled_input_ready: bool = False
    compiled_in_invalid: bool | None = None
    compiled_in_errors: tuple[Mapping[str, Any], ...] | None = None
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
    headers: Mapping[str, str] | None = None
    query: Mapping[str, Any] | None = None
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
        if isinstance(field_index, ABCMapping):
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


class _HotNamespaceDict(dict[str, Any]):
    __slots__ = ("_kind", "_temp")

    def __init__(self, kind: str, temp: "_HotTemp", initial: Mapping[str, Any] | None = None) -> None:
        super().__init__(initial or {})
        self._kind = kind
        self._temp = temp

    def _lazy_value(self, key: str) -> Any:
        hot = self._temp._hot_ctx()
        if hot is None:
            return _LAZY_MISSING
        if self._kind == "route":
            if key == "selector" and hot.selector:
                return hot.selector
            if key == "protocol" and hot.protocol:
                return hot.protocol
            if key in {"program_id", "opmeta_index"} and hot.program_id >= 0:
                return hot.program_id
            if key == "payload":
                value = _ensure_hot_in_values_view(hot)
                if value is not None:
                    return value
            if key == "path_params" and isinstance(hot.path_params, ABCMapping):
                return hot.path_params
            if key == "rpc_envelope" and isinstance(hot.parsed_json, ABCMapping):
                return hot.parsed_json
            return _LAZY_MISSING
        if key == "binding_protocol" and hot.protocol:
            return hot.protocol
        if key == "binding_selector" and hot.selector:
            return hot.selector
        if key == "channel_protocol" and hot.protocol:
            return hot.protocol
        if key == "channel_selector" and hot.selector:
            return hot.selector
        if key in {"normalized_input", "parsed_payload"}:
            value = _ensure_hot_in_values_view(hot)
            if value is not None:
                return value
        if key == "rpc" and isinstance(hot.parsed_json, ABCMapping):
            return hot.parsed_json
        if key == "rpc_method" and isinstance(hot.parsed_json, ABCMapping):
            method = hot.parsed_json.get("method")
            return method if method is not None else _LAZY_MISSING
        return _LAZY_MISSING

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
        if key in {"route", "dispatch"} and isinstance(value, dict) and not isinstance(
            value, _HotNamespaceDict
        ):
            return _HotNamespaceDict(key, self, value)
        return value

    def _lazy_value(self, key: str) -> Any:
        hot = self._hot_ctx()
        if hot is None:
            return _LAZY_MISSING
        if key in {"route", "dispatch"}:
            return _HotNamespaceDict(key, self)
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
        dict.__setitem__(self, key, self._wrap_namespace(key, value))

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
        if isinstance(temp, ABCMapping):
            hot = temp.get("hot_ctx")
            return hot if isinstance(hot, HotCtx) else None
        return None

    def _lazy_bag_value(self, name: str, *, cache: bool) -> Any:
        hot = self._hot_ctx()
        if hot is None:
            return _LAZY_MISSING
        if name == "payload":
            value = _ensure_hot_in_values_view(hot)
            if value is None:
                return _LAZY_MISSING
        elif name == "path_params" and isinstance(hot.path_params, ABCMapping):
            value = hot.path_params
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
