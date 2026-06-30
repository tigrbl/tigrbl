from __future__ import annotations

import importlib

import pytest


@pytest.mark.parametrize(
    "name",
    (
        "RestJsonRpcTable",
        "RestOltpTable",
        "JsonRpcOltpTable",
        "RestJsonRpcOltpTable",
        "RestOlapTable",
        "JsonRpcOlapTable",
        "RestJsonRpcOlapTable",
    ),
)
def test_protocol_table_profiles_are_exported_from_public_and_concrete_facades(
    name: str,
) -> None:
    public = importlib.import_module("tigrbl")
    concrete = importlib.import_module("tigrbl_concrete._concrete")

    public_value = getattr(public, name)
    concrete_value = getattr(concrete, name)

    assert public_value is concrete_value
    assert public_value.__name__ == name
