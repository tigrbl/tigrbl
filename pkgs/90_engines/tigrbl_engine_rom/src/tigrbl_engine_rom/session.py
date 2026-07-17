from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from typing import Any, Callable, Iterable, Mapping, Sequence

from tigrbl_base._base import EngineSessionBase
from tigrbl_core._spec.engine_session_spec import EngineSessionSpec

from .engine import ROMEngine


READ_ONLY_ERROR = "write attempted against read-only memory engine"


class ROMResult:
    """Small result facade compatible with Tigrbl's scalar query helpers."""

    def __init__(self, items: Sequence[Any]) -> None:
        self._items = tuple(items)
        self.rowcount = len(self._items)

    def scalars(self) -> "ROMResult":
        return self

    def all(self) -> list[Any]:
        return list(self._items)

    def first(self) -> Any | None:
        return self._items[0] if self._items else None

    def scalar_one(self) -> Any:
        if len(self._items) != 1:
            raise RuntimeError(f"expected exactly one row, found {len(self._items)}")
        return self._items[0]


class ROMSession(EngineSessionBase):
    """Async Tigrbl session over an immutable :class:`ROMEngine` snapshot."""

    def __init__(
        self, engine: ROMEngine, spec: EngineSessionSpec | None = None
    ) -> None:
        enforced = replace(spec or EngineSessionSpec(), read_only=True)
        super().__init__(enforced)
        self._engine = engine
        self._closed = False
        self._tracked: dict[int, tuple[Any, dict[str, Any]]] = {}

    def apply_spec(self, spec: EngineSessionSpec | None) -> None:
        enforced = replace(spec or EngineSessionSpec(), read_only=True)
        super().apply_spec(enforced)

    def get_row(self, ident: Any) -> dict[str, Any] | None:
        self._require_open_session()
        return self._engine.get(ident)

    def query_rows(
        self,
        predicate: Callable[[Mapping[str, Any]], bool] | None = None,
    ) -> list[dict[str, Any]]:
        self._require_open_session()
        rows = self._engine.scan()
        if predicate is not None:
            rows = [row for row in rows if predicate(row)]
        return rows

    async def _tx_begin_impl(self) -> None:
        self._require_open_session()

    async def _tx_commit_impl(self) -> None:
        self._require_open_session()

    async def _tx_rollback_impl(self) -> None:
        self._require_open_session()
        for obj, snapshot in self._tracked.values():
            for name, value in snapshot.items():
                setattr(obj, name, deepcopy(value))

    def _add_impl(self, obj: Any) -> None:
        raise RuntimeError(READ_ONLY_ERROR)

    async def _delete_impl(self, obj: Any) -> None:
        raise RuntimeError(READ_ONLY_ERROR)

    async def _flush_impl(self) -> None:
        self._require_open_session()
        for obj, snapshot in self._tracked.values():
            if self._snapshot(obj) != snapshot:
                raise RuntimeError(READ_ONLY_ERROR)

    async def _refresh_impl(self, obj: Any) -> None:
        self._require_open_session()
        row = self._engine.get(getattr(obj, self._engine.primary_key))
        if row is None:
            return
        for name, value in row.items():
            setattr(obj, name, value)
        self._track(obj)

    async def _get_impl(self, model: type, ident: Any) -> Any | None:
        self._require_open_session()
        row = self._engine.get(ident)
        return None if row is None else self._inflate(model, row)

    async def _execute_impl(self, stmt: Any) -> ROMResult:
        self._require_open_session()
        if type(stmt).__name__.lower() != "select":
            raise RuntimeError(READ_ONLY_ERROR)
        model = self._extract_model(stmt)
        items = [self._inflate(model, row) for row in self._engine.scan()]
        for name, operator, value in self._extract_predicates(stmt):
            if operator == "eq":
                items = [item for item in items if getattr(item, name, None) == value]
            elif operator == "in":
                accepted = set(value)
                items = [
                    item for item in items if getattr(item, name, None) in accepted
                ]
            else:  # pragma: no cover - protected by extraction
                raise NotImplementedError(f"unsupported ROM predicate: {operator}")
        for name, descending in reversed(self._extract_ordering(stmt)):
            items.sort(key=lambda item: getattr(item, name, None), reverse=descending)
        offset = self._clause_int(getattr(stmt, "_offset_clause", None)) or 0
        limit = self._clause_int(getattr(stmt, "_limit_clause", None))
        items = items[max(0, offset) :]
        if limit is not None:
            items = items[: max(0, limit)]
        return ROMResult(items)

    async def _executeloop_impl(self, statements: Iterable[Any]) -> list[ROMResult]:
        return [await self._execute_impl(statement) for statement in statements]

    async def _executemany_impl(self, stmt: Any, parameter_sets: Any) -> Any:
        raise RuntimeError(
            "parameterized batch execution is unavailable on read-only memory engine"
        )

    async def _close_impl(self) -> None:
        self._closed = True
        self._open = False
        self._dirty = False
        self._tracked.clear()

    def _require_open_session(self) -> None:
        if self._closed:
            raise RuntimeError("ROM session is closed")

    def _inflate(self, model: type, row: Mapping[str, Any]) -> Any:
        try:
            obj = model(**row)
        except TypeError:
            obj = model()
            for name, value in row.items():
                setattr(obj, name, value)
        self._track(obj)
        return obj

    def _track(self, obj: Any) -> None:
        self._tracked[id(obj)] = (obj, self._snapshot(obj))

    @staticmethod
    def _snapshot(obj: Any) -> dict[str, Any]:
        return {
            name: deepcopy(value)
            for name, value in vars(obj).items()
            if not name.startswith("_sa_")
        }

    @staticmethod
    def _extract_model(stmt: Any) -> type:
        for description in getattr(stmt, "column_descriptions", ()):
            entity = description.get("entity")
            if isinstance(entity, type):
                return entity
        raise NotImplementedError("ROM selects must target one mapped model")

    @classmethod
    def _extract_predicates(cls, stmt: Any) -> list[tuple[str, str, Any]]:
        predicates: list[tuple[str, str, Any]] = []
        for criterion in getattr(stmt, "_where_criteria", ()):
            clauses = getattr(criterion, "clauses", None)
            if clauses is not None:
                boolean_operator = getattr(
                    getattr(criterion, "operator", None), "__name__", ""
                )
                if boolean_operator != "and_":
                    raise NotImplementedError(
                        "ROM supports conjunctions of equality and IN predicates only"
                    )
                for clause in clauses:
                    predicates.extend(cls._extract_binary_predicate(clause))
            else:
                predicates.extend(cls._extract_binary_predicate(criterion))
        return predicates

    @staticmethod
    def _extract_binary_predicate(expr: Any) -> list[tuple[str, str, Any]]:
        name = getattr(getattr(expr, "left", None), "key", None)
        operator_name = getattr(getattr(expr, "operator", None), "__name__", "")
        right = getattr(expr, "right", None)
        value = getattr(right, "effective_value", getattr(right, "value", None))
        if not name or operator_name not in {"eq", "in_op"}:
            raise NotImplementedError("ROM supports equality and IN predicates only")
        return [(name, "in" if operator_name == "in_op" else "eq", value)]

    @staticmethod
    def _extract_ordering(stmt: Any) -> list[tuple[str, bool]]:
        ordering: list[tuple[str, bool]] = []
        for clause in getattr(stmt, "_order_by_clauses", ()):
            element = getattr(clause, "element", clause)
            name = getattr(element, "key", None)
            if not name:
                raise NotImplementedError("ROM ordering must target mapped columns")
            modifier = getattr(getattr(clause, "modifier", None), "__name__", "")
            ordering.append((name, modifier == "desc_op"))
        return ordering

    @staticmethod
    def _clause_int(clause: Any) -> int | None:
        if clause is None:
            return None
        value = getattr(clause, "effective_value", getattr(clause, "value", clause))
        return int(value)


__all__ = ["READ_ONLY_ERROR", "ROMResult", "ROMSession"]
