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
    assert fused[0]["source_segments"] == ("dispatch", "derive")


def test_protocol_segment_fusion_preserves_atom_order_and_diagnostics_anchors() -> None:
    fuse = _require("tigrbl_kernel.protocol_fusion", "fuse_protocol_segments")

    fused = fuse(
        [
            {
                "segment_id": "shape",
                "atoms": ("response.shape",),
                "anchors": ("egress.shape",),
                "barrier": False,
            },
            {
                "segment_id": "serialize",
                "atoms": ("response.serialize",),
                "anchors": ("egress.serialize",),
                "barrier": False,
            },
        ]
    )

    assert [segment["segment_id"] for segment in fused] == ["shape+serialize"]
    assert fused[0]["atoms"] == ("response.shape", "response.serialize")
    assert fused[0]["anchors"] == ("egress.shape", "egress.serialize")


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


@pytest.mark.parametrize(
    "barrier_segment",
    (
        {"segment_id": "tx", "anchors": ("TX_COMMIT",), "barrier": True, "barrier_kind": "transaction"},
        {"segment_id": "emit", "anchors": ("transport.emit",), "barrier": True, "barrier_kind": "transport"},
        {"segment_id": "error", "anchors": ("ON_HANDLER_ERROR",), "barrier": True, "barrier_kind": "error"},
        {"segment_id": "complete", "anchors": ("transport.emit_complete",), "barrier": True, "barrier_kind": "completion"},
    ),
)
def test_protocol_segment_fusion_keeps_barrier_segments_unfused(
    barrier_segment: dict[str, object]
) -> None:
    fuse = _require("tigrbl_kernel.protocol_fusion", "fuse_protocol_segments")

    fused = fuse(
        [
            {"segment_id": "before", "anchors": ("dispatch.select",), "barrier": False},
            barrier_segment,
            {"segment_id": "after", "anchors": ("response.shape",), "barrier": False},
        ]
    )

    assert [segment["segment_id"] for segment in fused] == [
        "before",
        barrier_segment["segment_id"],
        "after",
    ]


def test_protocol_segment_fusion_preserves_error_edge_metadata() -> None:
    fuse = _require("tigrbl_kernel.protocol_fusion", "fuse_protocol_segments")

    fused = fuse(
        [
            {
                "segment_id": "decode",
                "anchors": ("request.decode",),
                "barrier": False,
                "err_target": "transport.close",
            },
            {
                "segment_id": "validate",
                "anchors": ("request.validate",),
                "barrier": False,
                "err_target": "ON_VALIDATION_ERROR",
            },
        ]
    )

    assert fused[0]["err_targets"] == ("transport.close", "ON_VALIDATION_ERROR")


def test_fused_and_unfused_protocol_segments_have_equivalent_anchor_projection() -> None:
    fuse = _require("tigrbl_kernel.protocol_fusion", "fuse_protocol_segments")
    linearize = _require("tigrbl_kernel.protocol_fusion", "linearize_segment_anchors")

    segments = [
        {"segment_id": "dispatch", "anchors": ("dispatch.select",), "barrier": False},
        {"segment_id": "derive", "anchors": ("family.derive", "subevent.derive"), "barrier": False},
        {"segment_id": "emit", "anchors": ("transport.emit",), "barrier": True},
    ]

    assert linearize(fuse(segments)) == linearize(segments)
