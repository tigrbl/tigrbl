from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import MISSING, dataclass, field, fields, is_dataclass
from enum import Enum
from typing import Any, Awaitable, Callable, Final, Literal, Tuple, cast, final

from collections.abc import Mapping

from typing_extensions import Generic, TypeAlias, TypeVar

from .stages import (
    Boot,
    Failed,
)

from tigrbl_typing.protocols import (
    DependencyLike,
    ResponseLike,
    is_dependency_like,
    is_response_like,
)
from tigrbl_typing.phases import normalize_phase


S = TypeVar("S")
T = TypeVar("T")
U = TypeVar("U")
E = TypeVar("E", default=Exception)

EdgeKind: TypeAlias = Literal["ok", "err"]
EdgeTargetKind: TypeAlias = Literal["node", "terminal", "loop", "rollback", "noop"]

_EDGE_KINDS: Final[frozenset[str]] = frozenset(("ok", "err"))
_EDGE_TARGET_KINDS: Final[frozenset[str]] = frozenset(
    ("node", "terminal", "loop", "rollback", "noop")
)

_ERROR_PHASES: Final[frozenset[str]] = frozenset(
    (
        "ON_ERROR",
        "ON_PRE_TX_BEGIN_ERROR",
        "ON_START_TX_ERROR",
        "ON_PRE_HANDLER_ERROR",
        "ON_HANDLER_ERROR",
        "ON_POST_HANDLER_ERROR",
        "ON_PRE_COMMIT_ERROR",
        "ON_TX_COMMIT_ERROR",
        "ON_POST_COMMIT_ERROR",
        "ON_POST_RESPONSE_ERROR",
        "TX_ROLLBACK",
    )
)

_TX_PHASES: Final[frozenset[str]] = frozenset(
    (
        "START_TX",
        "PRE_HANDLER",
        "HANDLER",
        "POST_HANDLER",
        "PRE_COMMIT",
        "TX_COMMIT",
    )
)


@dataclass(frozen=True, slots=True)
class EdgeTarget:
    kind: EdgeTargetKind
    ref: str | None = None
    fallback: str | None = None

    def __post_init__(self) -> None:
        if self.ref is not None:
            object.__setattr__(self, "ref", normalize_phase(self.ref))
        if self.fallback is not None:
            object.__setattr__(self, "fallback", normalize_phase(self.fallback))
        if self.kind not in _EDGE_TARGET_KINDS:
            raise ValueError(f"unknown edge target kind: {self.kind!r}")
        if self.kind in {"node", "terminal", "loop", "rollback"} and not self.ref:
            raise ValueError(f"{self.kind} edge target requires ref")

    @classmethod
    def node(cls, node_id: str) -> "EdgeTarget":
        return cls(kind="node", ref=node_id)

    @classmethod
    def terminal(cls, name: str) -> "EdgeTarget":
        return cls(kind="terminal", ref=name)

    @classmethod
    def loop(cls, node_id: str) -> "EdgeTarget":
        return cls(kind="loop", ref=node_id)

    @classmethod
    def rollback(cls, phase: str = "TX_ROLLBACK", *, fallback: str = "ON_ERROR") -> "EdgeTarget":
        return cls(kind="rollback", ref=phase, fallback=fallback)

    @classmethod
    def noop(cls) -> "EdgeTarget":
        return cls(kind="noop")


@dataclass(frozen=True, slots=True)
class PhaseTreeEdge:
    kind: EdgeKind
    target: EdgeTarget

    def __post_init__(self) -> None:
        if self.kind not in _EDGE_KINDS:
            raise ValueError(f"unknown edge kind: {self.kind!r}")


@dataclass(frozen=True, slots=True)
class PhaseTreeNode:
    node_id: str
    phase: str
    stage_in: str | None
    stage_out: str | None
    segment_ids: tuple[int, ...]
    ok_child: PhaseTreeEdge
    err_child: PhaseTreeEdge
    terminal_behavior: str = "continue"
    linear_index: int = 0

    def __post_init__(self) -> None:
        if self.ok_child.kind != "ok":
            raise ValueError("PhaseTreeNode.ok_child must be an ok edge")
        if self.err_child.kind != "err":
            raise ValueError("PhaseTreeNode.err_child must be an err edge")


@dataclass(frozen=True, slots=True)
class TypedErr:
    exc_type: str
    code: str
    message: str
    status_code: int | None = None
    public_detail: object | None = None
    detail_is_public: bool = True
    sanitize_detail: bool = False
    retryable: bool = False
    cancellation: bool = False
    disconnect: bool = False

    @classmethod
    def from_error(cls, error: object, *, ctx: object | None = None) -> "TypedErr":
        if isinstance(error, TypedErr):
            return error

        exc_type = type(error).__name__
        code = str(getattr(error, "code", None) or exc_type)
        message = str(error) or exc_type
        status = getattr(error, "status", None)
        if status is None:
            status = getattr(error, "status_code", None)
        try:
            status_code = int(status) if status is not None else None
        except (TypeError, ValueError):
            status_code = None

        detail = getattr(error, "detail", None)
        if detail in (None, ""):
            detail = getattr(error, "details", None)
        if detail in (None, ""):
            detail = message

        sanitize = False
        try:
            from tigrbl_typing.status.utils import is_persistence_exception

            sanitize = bool(is_persistence_exception(error))
        except Exception:
            sanitize = False

        name = exc_type.lower()
        cancellation = "cancel" in name
        disconnect = "disconnect" in name or "connectionclosed" in name
        if sanitize:
            return cls(
                exc_type=exc_type,
                code=code,
                message=message,
                status_code=500,
                public_detail="Internal error",
                detail_is_public=False,
                sanitize_detail=True,
                cancellation=cancellation,
                disconnect=disconnect,
            )

        del ctx
        return cls(
            exc_type=exc_type,
            code=code,
            message=message,
            status_code=status_code,
            public_detail=detail,
            cancellation=cancellation,
            disconnect=disconnect,
        )


def normalize_typed_err(error: object, *, ctx: object | None = None) -> TypedErr:
    return TypedErr.from_error(error, ctx=ctx)


def error_phase_for(phase: str | None) -> str:
    if not phase:
        return "ON_ERROR"
    phase_name = str(normalize_phase(phase))
    if phase_name in _ERROR_PHASES:
        return phase_name
    candidate = f"ON_{phase_name}_ERROR"
    return candidate if candidate in _ERROR_PHASES else "ON_ERROR"


def phase_requires_rollback(
    phase: str | None,
    *,
    tx_open: bool = True,
    owns_tx: bool = True,
) -> bool:
    return bool(tx_open and owns_tx and normalize_phase(phase) in _TX_PHASES)


def select_error_edge(
    phase: str | None,
    *,
    rollback_required: bool = False,
) -> PhaseTreeEdge:
    err_phase = error_phase_for(phase)
    target = (
        EdgeTarget.rollback("TX_ROLLBACK", fallback=err_phase)
        if rollback_required
        else EdgeTarget.node(err_phase)
    )
    return PhaseTreeEdge(kind="err", target=target)


PHASE_SEQUENCE: Final[tuple[str, ...]] = (
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

INGRESS_PHASES: Final[tuple[str, ...]] = PHASE_SEQUENCE[:4]
HANDLER_PHASES: Final[tuple[str, ...]] = PHASE_SEQUENCE[5:8]
EGRESS_PHASES: Final[tuple[str, ...]] = PHASE_SEQUENCE[-3:]


@dataclass(slots=True)
class BaseCtx(Generic[S, E]):
    env: object | None = None
    bag: dict[str, object] = field(default_factory=dict)
    temp: dict[str, object] = field(default_factory=dict)
    error: E | None = None
    phase: str | None = None
    current_phase: str | None = None
    error_phase: str | None = None

    def __getattribute__(self, name: str) -> Any:
        """
        Keep core context methods callable even if runtime data shadows names.

        Some adapters may attach arbitrary attributes to ctx instances. If one of
        those attributes is named ``promote`` and set to ``None`` (or any
        non-callable), ``ctx.promote(...)`` would fail with ``NoneType is not
        callable``. Always resolving ``promote`` from ``BaseCtx`` preserves the
        invariant that every ctx remains promotable.
        """
        if name == "promote":
            return BaseCtx.promote.__get__(self, type(self))
        return object.__getattribute__(self, name)

    def promote(self, cls: type[U], /, **updates: object) -> U:
        if not is_dataclass(cls):
            raise TypeError(f"promote target must be a dataclass type, got {cls!r}")

        data: dict[str, object] = {}
        missing_required: list[str] = []

        for f in fields(cls):
            if f.name in updates:
                continue
            if hasattr(self, f.name):
                data[f.name] = getattr(self, f.name)
                continue
            if f.default is MISSING and f.default_factory is MISSING:
                missing_required.append(f.name)

        if missing_required:
            raise TypeError(
                f"cannot promote {type(self).__name__} -> {cls.__name__}; "
                f"missing required fields: {', '.join(missing_required)}"
            )

        data.update(updates)
        return cls(**data)

    def put_temp(self, key: str, value: object) -> None:
        self.temp[key] = value

    def require_temp(self, key: str) -> object:
        try:
            return self.temp[key]
        except KeyError as e:
            raise KeyError(f"missing temp field: {key!r}") from e

    def safe_view(
        self,
        *,
        include_temp: bool = False,
        temp_keys: tuple[str, ...] | None = None,
    ) -> Mapping[str, object]:
        """
        Return a compact read-only mapping intended for user callables.

        By default, temp is excluded to avoid exposing runtime internals.
        """
        base: dict[str, object] = {
            "op": getattr(self, "op", None),
            "persist": getattr(self, "persist", True),
            "model": getattr(self, "model", None),
            "specs": getattr(self, "specs", None),
            "user": getattr(self, "user", None),
            "tenant": getattr(self, "tenant", None),
            "now": getattr(self, "now", None),
        }
        if include_temp:
            allowed = set(temp_keys or ("assembled_values", "virtual_in"))
            exposed: dict[str, object] = {}
            for key in allowed:
                if key in self.temp:
                    exposed[key] = self.temp[key]
            base["temp"] = MappingProxy(exposed)
        return MappingProxy(base)


class MappingProxy(Mapping[str, object]):
    __slots__ = ("_d",)

    def __init__(self, data: Mapping[str, object]):
        self._d = dict(data)

    def __getitem__(self, key: str) -> object:
        return self._d[key]

    def __iter__(self):
        return iter(self._d)

    def __len__(self) -> int:
        return len(self._d)

    def get(self, key: str, default: object = None) -> object:
        return self._d.get(key, default)


Ctx: TypeAlias = BaseCtx[S, E]


class HookPhase(str, Enum):
    PRE_TX_BEGIN = "PRE_TX_BEGIN"
    START_TX = "START_TX"
    PRE_HANDLER = "PRE_HANDLER"
    HANDLER = "HANDLER"
    POST_HANDLER = "POST_HANDLER"
    PRE_COMMIT = "PRE_COMMIT"
    TX_COMMIT = "TX_COMMIT"
    END_TX = "TX_COMMIT"
    POST_COMMIT = "POST_COMMIT"
    POST_RESPONSE = "POST_RESPONSE"
    ON_ERROR = "ON_ERROR"
    ON_PRE_TX_BEGIN_ERROR = "ON_PRE_TX_BEGIN_ERROR"
    ON_START_TX_ERROR = "ON_START_TX_ERROR"
    ON_PRE_HANDLER_ERROR = "ON_PRE_HANDLER_ERROR"
    ON_HANDLER_ERROR = "ON_HANDLER_ERROR"
    ON_POST_HANDLER_ERROR = "ON_POST_HANDLER_ERROR"
    ON_PRE_COMMIT_ERROR = "ON_PRE_COMMIT_ERROR"
    ON_TX_COMMIT_ERROR = "ON_TX_COMMIT_ERROR"
    ON_END_TX_ERROR = "ON_TX_COMMIT_ERROR"
    ON_POST_COMMIT_ERROR = "ON_POST_COMMIT_ERROR"
    ON_POST_RESPONSE_ERROR = "ON_POST_RESPONSE_ERROR"
    TX_ROLLBACK = "TX_ROLLBACK"
    ON_ROLLBACK = "TX_ROLLBACK"

    @classmethod
    def _missing_(cls, value: object):
        normalized = normalize_phase(str(value)) if value is not None else None
        if normalized != value:
            return cls(normalized)
        return None


HookPhases: Tuple[HookPhase, ...] = tuple(HookPhase)
VALID_HOOK_PHASES: set[str] = {hook_phase.value for hook_phase in HookPhases}
StepFn = Callable[[Ctx[Any, Exception]], Awaitable[Any] | Any]
HookPredicate = Callable[[Ctx[Any, Exception]], bool]


def promote(ctx: Ctx[S, E], cls: type[U], /, **updates: object) -> U:
    return ctx.promote(cls, **updates)


def has_error(ctx: BaseCtx[S, E]) -> bool:
    return ctx.error is not None


@dataclass(slots=True)
class BootCtx(BaseCtx[Boot, E], Generic[E]):
    pass


@dataclass(slots=True)
class IngressCtx(BootCtx[E], Generic[E]):
    raw: object | None = None
    request: object | None = None
    method: str = ""
    path: str = ""
    headers: dict[str, object] = field(default_factory=dict)
    query: dict[str, object] = field(default_factory=dict)
    body: object | None = None


@dataclass(slots=True)
class RoutedCtx(IngressCtx[E], Generic[E]):
    protocol: str = ""
    path_params: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class BoundCtx(RoutedCtx[E], Generic[E]):
    binding: object | None = None
    model: object | None = None
    op: str = ""


@dataclass(slots=True)
class PlannedCtx(BoundCtx[E], Generic[E]):
    opmeta_index: object | None = None
    payload: object | None = None
    plan: object | None = None
    opmeta: object | None = None
    opview: object | None = None


@dataclass(slots=True)
class GuardedCtx(PlannedCtx[E], Generic[E]):
    authz: object | None = None


@dataclass(slots=True)
class ExecutingCtx(GuardedCtx[E], Generic[E]):
    pass


@dataclass(slots=True)
class ResolvedCtx(ExecutingCtx[E], Generic[E]):
    schema_in: object | None = None
    in_values: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class OperatedCtx(ResolvedCtx[E], Generic[E]):
    result: object | None = None


@dataclass(slots=True)
class EncodedCtx(OperatedCtx[E], Generic[E]):
    schema_out: object | None = None
    response_payload: object | None = None
    response_headers: dict[str, object] = field(default_factory=dict)
    status_code: int = 200


@dataclass(slots=True)
class EmittingCtx(EncodedCtx[E], Generic[E]):
    transport_response: object | None = None


@dataclass(slots=True)
class EgressedCtx(EmittingCtx[E], Generic[E]):
    pass


@dataclass(slots=True)
class FailedCtx(BaseCtx[Failed, E], Generic[E]):
    error: E | None = None
    typed_error: TypedErr | None = None


@dataclass(slots=True)
class ErrorCtx(FailedCtx[E], Generic[E]):
    failed_phase: str | None = None
    failed_node_id: str | None = None
    failing_atom_label: str | None = None
    failing_anchor: str | None = None
    source_stage: str | None = None
    err_target: EdgeTarget | None = None
    tx_open: bool = False
    owns_tx: bool = False
    rollback_required: bool = False
    transport_started: bool = False
    transport_complete: bool = False
    binding: str | None = None
    exchange: str | None = None
    family: str | None = None
    subevent: str | None = None
    scope_type: str | None = None
    channel_id: str | None = None
    stream_id: str | None = None
    datagram_id: str | None = None


AtomResult: TypeAlias = Ctx[T, E] | FailedCtx[E]


def fail(ctx: Ctx[S, E], error: E, /, **updates: object) -> FailedCtx[E]:
    return cast(
        FailedCtx[E],
        ctx.promote(
            FailedCtx,
            error=error,
            typed_error=normalize_typed_err(error, ctx=ctx),
            **updates,
        ),
    )


class AtomFailure(Exception):
    """
    Optional internal exception type for atoms that want to signal
    a mapped domain/runtime failure via raise instead of returning fail(...).
    """

    def __init__(self, error: object) -> None:
        super().__init__(str(error))
        self.error = error


def _string_or_none(value: object) -> str | None:
    return value if isinstance(value, str) and value else None


def _ctx_get(ctx: object, key: str, default: object = None) -> object:
    getter = getattr(ctx, "get", None)
    if callable(getter):
        try:
            return getter(key, default)
        except Exception:
            pass
    value = getattr(ctx, key, default)
    if value is not default:
        return value
    bag = getattr(ctx, "bag", None)
    if isinstance(bag, Mapping):
        return bag.get(key, default)
    return default


def _ctx_temp(ctx: object) -> dict[str, object]:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        try:
            setattr(ctx, "temp", temp)
        except Exception:
            return {}
    return temp


def _transport_state(ctx: object) -> tuple[bool, bool]:
    temp = getattr(ctx, "temp", None)
    egress = temp.get("egress") if isinstance(temp, dict) else None
    transport_started = bool(
        _ctx_get(ctx, "transport_started", False)
        or (
            isinstance(egress, dict)
            and bool(egress.get("transport_response") or egress.get("started"))
        )
    )
    transport_complete = bool(
        _ctx_get(ctx, "transport_complete", False)
        or _ctx_get(ctx, "current_phase") == "POST_EMIT"
        or (
            isinstance(egress, dict)
            and bool(egress.get("transport_complete") or egress.get("emit_complete"))
        )
    )
    return transport_started, transport_complete


def build_error_ctx(
    ctx: Ctx[S, E],
    error: object,
    *,
    failed_phase: str | None = None,
    failed_node_id: str | None = None,
    failing_atom_label: str | None = None,
    failing_anchor: str | None = None,
    err_target: EdgeTarget | None = None,
    rollback_required: bool = False,
) -> ErrorCtx[E]:
    phase = failed_phase or _string_or_none(_ctx_get(ctx, "phase"))
    phase = phase or _string_or_none(_ctx_get(ctx, "current_phase"))
    typed_error = normalize_typed_err(error, ctx=ctx)
    temp = _ctx_temp(ctx)
    tx_open = bool(
        _ctx_get(ctx, "tx_open", False)
        or _ctx_get(ctx, "owns_tx", False)
        or temp.get("__sys_tx_open__")
    )
    owns_tx = bool(_ctx_get(ctx, "owns_tx", False))
    rollback = bool(
        rollback_required
        or phase_requires_rollback(phase, tx_open=tx_open, owns_tx=owns_tx)
    )
    edge = err_target or select_error_edge(phase, rollback_required=rollback).target
    transport_started, transport_complete = _transport_state(ctx)
    raw = _ctx_get(ctx, "raw")
    scope = getattr(raw, "scope", None)
    scope_type = scope.get("type") if isinstance(scope, Mapping) else None
    channel = _ctx_get(ctx, "channel")

    error_ctx = ctx.promote(
        ErrorCtx,
        error=cast(E, error),
        typed_error=typed_error,
        failed_phase=phase,
        failed_node_id=failed_node_id,
        failing_atom_label=failing_atom_label,
        failing_anchor=failing_anchor,
        source_stage=_string_or_none(_ctx_get(ctx, "stage"))
        or type(ctx).__name__,
        err_target=edge,
        tx_open=tx_open,
        owns_tx=owns_tx,
        rollback_required=rollback,
        transport_started=transport_started,
        transport_complete=transport_complete,
        binding=_string_or_none(_ctx_get(ctx, "binding")),
        exchange=_string_or_none(_ctx_get(ctx, "exchange")),
        family=_string_or_none(_ctx_get(ctx, "family")),
        subevent=_string_or_none(_ctx_get(ctx, "subevent")),
        scope_type=_string_or_none(scope_type),
        channel_id=_string_or_none(getattr(channel, "channel_id", None))
        or _string_or_none(_ctx_get(ctx, "channel_id")),
        stream_id=_string_or_none(_ctx_get(ctx, "stream_id")),
        datagram_id=_string_or_none(_ctx_get(ctx, "datagram_id")),
    )
    try:
        ctx.error = cast(E, error)
        ctx.error_phase = error_phase_for(phase)
        setattr(ctx, "typed_error", typed_error)
        setattr(ctx, "error_ctx", error_ctx)
    except Exception:
        pass
    temp["typed_err"] = typed_error
    temp["error_ctx"] = error_ctx
    return error_ctx


class Atom(ABC, Generic[S, T, E]):
    name: str = "atom"
    anchor: str = ""

    @abstractmethod
    async def __call__(
        self,
        obj: object | None,
        ctx: Ctx[S, E],
    ) -> AtomResult[T, E]:
        raise NotImplementedError


class StandardAtom(Atom[S, T, E], ABC):
    """
    Template-method base:
      - handles pre-failed input
      - handles success promotion
      - handles fail normalization
      - optionally maps raised exceptions into E
    """

    target_ctx: type[BaseCtx[T, E]]

    @final
    async def __call__(
        self,
        obj: object | None,
        ctx: Ctx[S, E],
    ) -> AtomResult[T, E]:
        if has_error(ctx):
            assert ctx.error is not None
            return fail(ctx, ctx.error)

        try:
            result = await self._run(obj, ctx)
        except AtomFailure as ex:
            return fail(ctx, cast(E, ex.error))
        except Exception as ex:
            mapped = self._map_exception(ex)
            if mapped is None:
                raise
            return fail(ctx, mapped)

        if isinstance(result, FailedCtx):
            return result

        return promote(ctx, self.target_ctx, **result)

    @abstractmethod
    async def _run(
        self,
        obj: object | None,
        ctx: Ctx[S, E],
    ) -> dict[str, object] | FailedCtx[E]:
        raise NotImplementedError

    def _map_exception(self, ex: Exception) -> E | None:
        return None


__all__ = [
    "S",
    "T",
    "U",
    "E",
    "Ctx",
    "HookPhase",
    "HookPhases",
    "VALID_HOOK_PHASES",
    "StepFn",
    "HookPredicate",
    "EdgeKind",
    "EdgeTargetKind",
    "EdgeTarget",
    "PhaseTreeEdge",
    "PhaseTreeNode",
    "TypedErr",
    "AtomResult",
    "BaseCtx",
    "BootCtx",
    "IngressCtx",
    "RoutedCtx",
    "BoundCtx",
    "PlannedCtx",
    "GuardedCtx",
    "ExecutingCtx",
    "ResolvedCtx",
    "OperatedCtx",
    "EncodedCtx",
    "EmittingCtx",
    "EgressedCtx",
    "FailedCtx",
    "ErrorCtx",
    "AtomFailure",
    "Atom",
    "StandardAtom",
    "normalize_typed_err",
    "error_phase_for",
    "phase_requires_rollback",
    "select_error_edge",
    "build_error_ctx",
    "promote",
    "fail",
    "has_error",
    "DependencyLike",
    "ResponseLike",
    "is_dependency_like",
    "is_response_like",
]
