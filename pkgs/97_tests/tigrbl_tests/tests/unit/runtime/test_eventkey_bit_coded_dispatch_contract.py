from __future__ import annotations

import importlib

import pytest


def _require(module_name: str, attr_name: str):
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        pytest.xfail(f"{module_name} is not implemented")
    value = getattr(module, attr_name, None)
    if value is None:
        pytest.xfail(f"{module_name}.{attr_name} is not implemented")
    return value


def test_eventkey_packs_and_unpacks_hot_dispatch_integer_fields() -> None:
    pack = _require("tigrbl_kernel.eventkey", "pack_event_key")
    unpack = _require("tigrbl_kernel.eventkey", "unpack_event_key")

    key = pack(
        op=17,
        binding=3,
        exchange=1,
        family=4,
        subevent=22,
        framing=2,
    )
    decoded = unpack(key)

    assert isinstance(key, int)
    assert decoded == {
        "op": 17,
        "binding": 3,
        "exchange": 1,
        "family": 4,
        "subevent": 22,
        "framing": 2,
    }


def test_eventkey_roundtrip_is_stable_for_boundary_field_values() -> None:
    pack = _require("tigrbl_kernel.eventkey", "pack_event_key")
    unpack = _require("tigrbl_kernel.eventkey", "unpack_event_key")

    fields = {
        "op": (1 << 20) - 1,
        "binding": (1 << 8) - 1,
        "exchange": (1 << 6) - 1,
        "family": (1 << 8) - 1,
        "subevent": (1 << 10) - 1,
        "framing": (1 << 6) - 1,
    }

    key = pack(**fields)

    assert isinstance(key, int)
    assert unpack(key) == fields
    assert pack(**unpack(key)) == key


def test_eventkey_dispatch_table_uses_integer_lookup_not_string_selectors() -> None:
    pack = _require("tigrbl_kernel.eventkey", "pack_event_key")
    build_table = _require("tigrbl_kernel.eventkey", "build_dispatch_table")

    key = pack(op=1, binding=2, exchange=1, family=3, subevent=4, framing=1)
    table = build_table({key: "chain:read"})

    assert table[key] == "chain:read"
    assert all(isinstance(item, int) for item in table)
    assert "socket.message.received" not in table


def test_eventkey_dispatch_table_rejects_string_selector_keys() -> None:
    build_table = _require("tigrbl_kernel.eventkey", "build_dispatch_table")

    with pytest.raises(TypeError, match="EventKey|integer|selector|string"):
        build_table({"socket.message.received": "chain:message"})


def test_eventkey_dispatch_table_rejects_duplicate_compiled_keys() -> None:
    pack = _require("tigrbl_kernel.eventkey", "pack_event_key")
    build_table = _require("tigrbl_kernel.eventkey", "build_dispatch_table")
    key = pack(op=7, binding=1, exchange=1, family=2, subevent=3, framing=1)

    with pytest.raises(ValueError, match="EventKey|duplicate|collision"):
        build_table([(key, "chain:first"), (key, "chain:second")])


@pytest.mark.parametrize(
    "fields",
    (
        {"op": -1, "binding": 1, "exchange": 1, "family": 1, "subevent": 1, "framing": 1},
        {"op": 1 << 20, "binding": 1, "exchange": 1, "family": 1, "subevent": 1, "framing": 1},
        {"op": 1, "binding": 1 << 8, "exchange": 1, "family": 1, "subevent": 1, "framing": 1},
        {"op": 1, "binding": 1, "exchange": 1 << 6, "family": 1, "subevent": 1, "framing": 1},
        {"op": 1, "binding": 1, "exchange": 1, "family": 1 << 8, "subevent": 1, "framing": 1},
        {"op": 1, "binding": 1, "exchange": 1, "family": 1, "subevent": 1 << 10, "framing": 1},
        {"op": 1, "binding": 1, "exchange": 1, "family": 1, "subevent": 1, "framing": 1 << 6},
        {"op": 1, "binding": 1, "exchange": 1, "family": 1, "subevent": 1, "framing": 1, "reserved": 1},
    ),
)
def test_eventkey_decode_fails_closed_for_overflow_or_reserved_bits(
    fields: dict[str, int],
) -> None:
    pack = _require("tigrbl_kernel.eventkey", "pack_event_key")

    with pytest.raises(ValueError, match="EventKey|width|reserved|overflow|code"):
        pack(**fields)


def test_eventkey_unpack_rejects_reserved_bits() -> None:
    unpack = _require("tigrbl_kernel.eventkey", "unpack_event_key")

    with pytest.raises(ValueError, match="EventKey|reserved|overflow|code"):
        unpack(1 << 63)
