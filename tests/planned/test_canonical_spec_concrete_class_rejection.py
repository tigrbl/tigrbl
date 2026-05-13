import pytest

from tigrbl_core._spec import PathSpec, TableSpec


class Widget:
    pass


def test_pathspec_rejects_concrete_model_class_as_canonical_table_identity() -> None:
    with pytest.raises(TypeError, match="concrete model classes"):
        PathSpec(path="/widgets", tables=(TableSpec(model=Widget),))


def test_pathspec_accepts_spec_native_table_identity() -> None:
    path = PathSpec(
        path="/widgets",
        tables=(
            TableSpec(name="Widget", resource="widget", model_ref="app.models:Widget"),
        ),
    )

    assert path.tables[0].name == "Widget"
    assert path.tables[0].resource == "widget"
    assert path.tables[0].model_ref == "app.models:Widget"
