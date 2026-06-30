from __future__ import annotations

from types import SimpleNamespace

from tigrbl_atoms.atoms.hot.slots import (
    SlotMappingView,
    capture_slot_payload,
    project_present_dict,
    project_row_tuple,
)


def test_slot_mapping_view_reads_present_values_without_materializing_dict() -> None:
    view = SlotMappingView(
        ("id", "name", "missing"),
        {"id": 0, "name": 1, "missing": 2},
        [1, "Ada", None],
        bytearray([1, 1, 0]),
    )

    assert view["id"] == 1
    assert view.get("name") == "Ada"
    assert list(view) == ["id", "name"]
    assert len(view) == 2


def test_project_row_tuple_uses_column_order_and_present_bits() -> None:
    row = project_row_tuple(
        ("id", "name", "email"),
        {"id": 0, "name": 1, "email": 2},
        [1, "Ada", "ada@example.test"],
        bytearray([1, 1, 0]),
        columns=("name", "email", "id"),
    )

    assert row == ("Ada", None, 1)


def test_capture_slot_payload_prefers_assembled_slots() -> None:
    hot = SimpleNamespace(
        slot_field_names=("id", "name"),
        slot_field_index={"id": 0, "name": 1},
        slot_values=[0, "raw"],
        slot_present=bytearray([1, 1]),
        assembled_slot_values=[1, "Ada"],
        assembled_slot_present=bytearray([1, 1]),
        body_view=memoryview(b'{"id":1,"name":"Ada"}'),
    )
    ctx = SimpleNamespace(temp={"hot_ctx": hot})

    payload = capture_slot_payload(ctx)

    assert payload is not None
    assert payload.row_tuple(("id", "name")) == (1, "Ada")
    assert project_present_dict(payload) == {"id": 1, "name": "Ada"}
