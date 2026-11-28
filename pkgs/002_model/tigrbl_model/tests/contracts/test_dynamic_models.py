from __future__ import annotations

from tigrbl_model import ConfigDict, Field, Model, RootModel, create_model


def test_create_model_builds_required_constrained_fields() -> None:
    Dynamic = create_model(
        "Dynamic",
        __config__=ConfigDict(extra="forbid"),
        name=(str, Field(..., min_length=1)),
        count=(int, Field(default=0, ge=0)),
    )

    value = Dynamic(name="widget", count="2")
    assert value.model_dump() == {"name": "widget", "count": 2}
    assert Dynamic.model_fields["name"].is_required()
    assert Dynamic.model_config["extra"] == "forbid"


def test_root_model_validates_and_dumps_collection_root() -> None:
    class Item(Model):
        value: int

    Items = RootModel[list[Item]]
    value = Items([{"value": "3"}])

    assert value.root == [Item(value=3)]
    assert value.model_dump() == [{"value": 3}]
    assert value.model_validate_json('[{"value":4}]').root == [Item(value=4)]


def test_model_rebuild_resolves_forward_references() -> None:
    class Node(Model):
        name: str
        child: "Node | None" = None

    assert Node.model_rebuild(force=True, _types_namespace={"Node": Node}) is True
    value = Node(name="root", child={"name": "leaf"})
    assert isinstance(value.child, Node)
    assert value.child.name == "leaf"


def test_dynamic_model_can_extend_a_model_base() -> None:
    class Identified(Model):
        id: int

    Extended = create_model("Extended", __base__=Identified, name=(str, ...))
    value = Extended(id="1", name="widget")
    assert value.model_dump() == {"id": 1, "name": "widget"}
