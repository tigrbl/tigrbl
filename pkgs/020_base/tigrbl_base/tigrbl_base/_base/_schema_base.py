from __future__ import annotations

import inspect
from types import SimpleNamespace

from tigrbl_core.config.constants import TIGRBL_SCHEMA_DECLS_ATTR


class SchemaBase:
    """Shared schema helpers used by concrete schema wrappers."""

    @staticmethod
    def bind_declared_schema(
        model: type, alias: str, kind: str, schema_cls: type
    ) -> None:
        """Expose a declared schema on ``model.schemas.<alias>`` immediately."""

        if kind not in ("in", "out"):
            raise ValueError("schema_ctx(kind=...) must be 'in' or 'out'")

        schemas = getattr(model, "schemas", None)
        if not isinstance(schemas, SimpleNamespace):
            schemas = SimpleNamespace()
            setattr(model, "schemas", schemas)

        alias_ns = getattr(schemas, alias, None)
        if not isinstance(alias_ns, SimpleNamespace):
            alias_ns = SimpleNamespace()
            setattr(schemas, alias, alias_ns)

        setattr(alias_ns, "in_" if kind == "in" else "out", schema_cls)

    @classmethod
    def bind_nested_declarations(cls, model: type) -> None:
        """Bind nested ``schema_ctx`` declarations onto a table/model class."""

        for obj in tuple(model.__dict__.values()):
            if not inspect.isclass(obj):
                continue
            decl = getattr(obj, "__tigrbl_schema_decl__", None)
            if decl is None:
                continue
            cls.bind_declared_schema(model, decl.alias, decl.kind, obj)

    @classmethod
    def collect(cls, model: type) -> dict[str, dict[str, type]]:
        """Collect schema declarations from explicit mappings and decorator metadata."""

        collected: dict[str, dict[str, type]] = {}

        explicit = getattr(model, TIGRBL_SCHEMA_DECLS_ATTR, None) or {}
        if isinstance(explicit, dict):
            for alias, kinds in explicit.items():
                if isinstance(kinds, dict):
                    collected[alias] = dict(kinds)

        schemas = getattr(model, "schemas", None)
        if isinstance(schemas, dict):
            for alias, kinds in schemas.items():
                if isinstance(kinds, dict):
                    collected[alias] = {**collected.get(alias, {}), **kinds}

        for _, obj in model.__dict__.items():
            if not inspect.isclass(obj):
                continue
            decl = getattr(obj, "__tigrbl_schema_decl__", None)
            if decl is None:
                continue
            bucket = collected.setdefault(decl.alias, {})
            bucket[decl.kind] = obj

        if isinstance(schemas, SimpleNamespace):
            for alias, ns in vars(schemas).items():
                if not isinstance(ns, SimpleNamespace):
                    continue
                bucket = collected.setdefault(alias, {})
                if getattr(ns, "in_", None) is not None:
                    bucket.setdefault("in", ns.in_)
                if getattr(ns, "out", None) is not None:
                    bucket.setdefault("out", ns.out)

        return collected


__all__ = ["SchemaBase"]
