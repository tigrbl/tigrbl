from types import SimpleNamespace

from tigrbl_core.config.constants import TIGRBL_SCHEMA_DECLS_ATTR

from tigrbl_base._base._schema_base import SchemaBase


class WithSchemas:
    schemas = {"req": {"name": str}}


class WithoutSchemas:
    pass


def test_schema_base_collect() -> None:
    assert SchemaBase.collect(WithSchemas) == {"req": {"name": str}}
    assert SchemaBase.collect(WithoutSchemas) == {}


def test_schema_base_collect_merges_explicit_mapping_and_schemas() -> None:
    class Model:
        pass

    setattr(Model, TIGRBL_SCHEMA_DECLS_ATTR, {"item": {"in": int}})
    Model.schemas = {"item": {"out": str}, "other": {"in": bytes}}

    assert SchemaBase.collect(Model) == {
        "item": {"in": int, "out": str},
        "other": {"in": bytes},
    }


def test_schema_base_collect_supports_namespace_declarations() -> None:
    class InSchema:
        pass

    class OutSchema:
        pass

    class Model:
        schemas = SimpleNamespace(
            item=SimpleNamespace(in_=InSchema, out=OutSchema),
            ignored=object(),
        )

    assert SchemaBase.collect(Model) == {"item": {"in": InSchema, "out": OutSchema}}
