from tigrbl_concrete._mapping.model import bind
from tigrbl.orm.tables import TableBase
from tigrbl.orm.mixins import GUIDPk, Replaceable
from tigrbl.types import Column, String


class Gadget(TableBase, GUIDPk, Replaceable):
    __tablename__ = "gadgets_schemas_binding"
    name = Column(String, nullable=False)


def test_bind_generates_request_response_and_persisted_schemas():
    bind(Gadget)

    # create/update/replace should have request, response, and persisted schemas
    for alias in ("create", "update", "replace"):
        ns = getattr(Gadget.schemas, alias)
        assert getattr(ns, "in_", None) is not None
        assert getattr(ns, "persisted", None) is not None
        assert getattr(ns, "out", None) is not None

    delete_ns = Gadget.schemas.delete
    assert getattr(delete_ns, "in_", None) is not None
    assert not hasattr(delete_ns, "persisted")
    assert getattr(delete_ns, "out", None) is not None

    # list should expose request and response schemas, but not persisted
    list_ns = Gadget.schemas.list
    assert getattr(list_ns, "in_", None) is not None
    assert not hasattr(list_ns, "persisted")
    assert getattr(list_ns, "out", None) is not None
    assert not hasattr(list_ns, "list")

    # read should expose a response schema but not persisted
    read_ns = Gadget.schemas.read
    assert not hasattr(read_ns, "persisted")
    assert getattr(read_ns, "out", None) is not None
