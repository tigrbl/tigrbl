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


def test_eventkey_dispatch_table_uses_integer_lookup_not_string_selectors() -> None:
    pack = _require("tigrbl_kernel.eventkey", "pack_event_key")
    build_table = _require("tigrbl_kernel.eventkey", "build_dispatch_table")

    key = pack(op=1, binding=2, exchange=1, family=3, subevent=4, framing=1)
    table = build_table({key: "chain:read"})

    assert table[key] == "chain:read"
    assert all(isinstance(item, int) for item in table)


@pytest.mark.parametrize(
    "fields",
    (
        {"op": -1, "binding": 1, "exchange": 1, "family": 1, "subevent": 1, "framing": 1},
        {"op": 1 << 32, "binding": 1, "exchange": 1, "family": 1, "subevent": 1, "framing": 1},
        {"op": 1, "binding": 1, "exchange": 1, "family": 1, "subevent": 1, "framing": 1, "reserved": 1},
    ),
)
def test_eventkey_decode_fails_closed_for_overflow_or_reserved_bits(
    fields: dict[str, int],
) -> None:
    pack = _require("tigrbl_kernel.eventkey", "pack_event_key")

    with pytest.raises(ValueError, match="EventKey|width|reserved|overflow|code"):
        pack(**fields)

