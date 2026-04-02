from __future__ import annotations

from types import SimpleNamespace
from typing import Any


class _SAObject:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return _SAObject(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        value = _SAObject()
        setattr(self, name, value)
        return value

    def __iter__(self):
        return iter(())


class TypeEngine(_SAObject):
    pass


class TypeDecorator(_SAObject):
    impl = None
    cache_ok = True


class Column(_SAObject):
    pass


class Table(_SAObject):
    pass


class MetaData(_SAObject):
    pass


class ForeignKey(_SAObject):
    pass


class CheckConstraint(_SAObject):
    pass


class String(TypeEngine):
    pass


class Integer(TypeEngine):
    pass


class Float(TypeEngine):
    pass


class Numeric(TypeEngine):
    pass


class Boolean(TypeEngine):
    pass


class LargeBinary(TypeEngine):
    pass


class Date(TypeEngine):
    pass


class Time(TypeEngine):
    pass


class DateTime(TypeEngine):
    pass


class Text(TypeEngine):
    pass


class JSON(TypeEngine):
    pass


class Enum(TypeEngine):
    pass


class CHAR(TypeEngine):
    pass


class ClauseElement(_SAObject):
    pass


class StaticPool(_SAObject):
    pass


class NullPool(_SAObject):
    pass


class SQLAlchemyError(Exception):
    pass


class NoInspectionAvailable(Exception):
    pass


class OperationalError(Exception):
    pass


class IntegrityError(Exception):
    pass


class DBAPIError(Exception):
    pass


class SAWarning(Warning):
    pass


class NoResultFound(Exception):
    pass


class UnmappedInstanceError(Exception):
    pass


class InstrumentedAttribute(_SAObject):
    pass


class MappedColumn(_SAObject):
    pass


class Mapped(_SAObject):
    pass


class Session(_SAObject):
    pass


class AsyncSession(_SAObject):
    pass


class DeclarativeBase:
    registry = SimpleNamespace(map_declaratively=lambda *a, **k: None)
    metadata = MetaData()


class registry(_SAObject):
    def map_declaratively(self, *args: Any, **kwargs: Any) -> None:
        return None


def mapped_column(*args: Any, **kwargs: Any) -> MappedColumn:
    return MappedColumn(*args, **kwargs)


def declarative_base(*args: Any, **kwargs: Any):
    class _Base(DeclarativeBase):
        pass
    return _Base


def declared_attr(fn):
    return property(fn)


def relationship(*args: Any, **kwargs: Any) -> Any:
    return _SAObject(*args, **kwargs)


def sessionmaker(*args: Any, **kwargs: Any):
    def _maker(*a: Any, **k: Any) -> Session:
        return Session(*a, **k)
    return _maker


def async_sessionmaker(*args: Any, **kwargs: Any):
    def _maker(*a: Any, **k: Any) -> AsyncSession:
        return AsyncSession(*a, **k)
    return _maker


def create_engine(*args: Any, **kwargs: Any) -> Any:
    return _SAObject(*args, **kwargs)


def create_async_engine(*args: Any, **kwargs: Any) -> Any:
    return _SAObject(*args, **kwargs)


def event(*args: Any, **kwargs: Any) -> Any:
    return _SAObject(*args, **kwargs)


def text(value: str) -> ClauseElement:
    obj = ClauseElement(value)
    obj.text = value
    return obj


def inspect(obj: Any) -> Any:
    return obj


def select(*args: Any, **kwargs: Any) -> ClauseElement:
    return ClauseElement(*args, **kwargs)


def delete(*args: Any, **kwargs: Any) -> ClauseElement:
    return ClauseElement(*args, **kwargs)


def and_(*args: Any, **kwargs: Any) -> ClauseElement:
    return ClauseElement(*args, **kwargs)


def asc(value: Any) -> Any:
    return value


def desc(value: Any) -> Any:
    return value


func = _SAObject()


def hybrid_property(fn=None, *args: Any, **kwargs: Any):
    if fn is None:
        def _wrap(inner):
            return property(inner)
        return _wrap
    return property(fn)


class MutableDict(dict):
    pass


class MutableList(list):
    pass


def insert(*args: Any, **kwargs: Any) -> ClauseElement:
    return ClauseElement(*args, **kwargs)
