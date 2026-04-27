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


def test_protocol_segments_fuse_only_non_barrier_adjacent_work() -> None:
    fuse = _require("tigrbl_kernel.protocol_fusion", "fuse_protocol_segments")

    fused = fuse(
        [
            {"segment_id": "dispatch", "anchors": ("dispatch.exchange.select",), "barrier": False},
            {"segment_id": "derive", "anchors": ("dispatch.family.derive", "dispatch.subevent.derive"), "barrier": False},
            {"segment_id": "emit", "anchors": ("transport.emit",), "barrier": True},
        ]
    )

    assert [segment["segment_id"] for segment in fused] == ["dispatch+derive", "emit"]
    assert fused[0]["anchors"] == (
        "dispatch.exchange.select",
        "dispatch.family.derive",
        "dispatch.subevent.derive",
    )


def test_protocol_segment_fusion_rejects_transaction_transport_and_error_barrier_crossing() -> None:
    fuse = _require("tigrbl_kernel.protocol_fusion", "fuse_protocol_segments")

    with pytest.raises(ValueError, match="barrier|transaction|transport|error"):
        fuse(
            [
                {"segment_id": "handler", "anchors": ("CALL_HANDLER",), "barrier": True},
                {"segment_id": "emit", "anchors": ("transport.emit",), "barrier": True},
            ],
            force=True,
        )

