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


def test_pure_ingress_dispatch_schema_and_egress_shape_atoms_may_fuse() -> None:
    fuse = _require("tigrbl_kernel.segment_fusion", "fuse_segments")

    fused = fuse(
        [
            {"segment_id": "ingress", "class": "pure_ingress", "atoms": ("ingress.parse",)},
            {"segment_id": "dispatch", "class": "pure_dispatch", "atoms": ("dispatch.exchange.select",)},
            {"segment_id": "schema", "class": "pure_schema", "atoms": ("schema.validate",)},
            {"segment_id": "shape", "class": "pure_egress_shape", "atoms": ("response.shape",)},
        ]
    )

    assert [segment["segment_id"] for segment in fused] == ["ingress+dispatch+schema+shape"]
    assert fused[0]["atoms"] == (
        "ingress.parse",
        "dispatch.exchange.select",
        "schema.validate",
        "response.shape",
    )


def test_default_fusion_splits_at_hard_barriers_without_crossing_them() -> None:
    fuse = _require("tigrbl_kernel.segment_fusion", "fuse_segments")

    fused = fuse(
        [
            {"segment_id": "ingress", "class": "pure_ingress", "atoms": ("ingress.parse",)},
            {"segment_id": "tx", "class": "tx", "atoms": ("tx.begin",)},
            {"segment_id": "schema", "class": "pure_schema", "atoms": ("schema.validate",)},
        ]
    )

    assert [segment["segment_id"] for segment in fused] == ["ingress", "tx", "schema"]
    assert fused[1]["class"] == "tx"


@pytest.mark.parametrize(
    "barrier_class",
    (
        "deps",
        "tx",
        "rollback",
        "handler",
        "transport.accept",
        "transport.emit",
        "transport.close",
        "completion_fence",
    ),
)
def test_hard_barriers_are_never_crossed_by_segment_fusion(barrier_class: str) -> None:
    fuse = _require("tigrbl_kernel.segment_fusion", "fuse_segments")

    with pytest.raises(ValueError, match="barrier|fusion|transport|handler|tx|completion"):
        fuse(
            [
                {"segment_id": "before", "class": "pure_dispatch", "atoms": ("dispatch.exchange.select",)},
                {"segment_id": "barrier", "class": barrier_class, "atoms": (barrier_class,)},
                {"segment_id": "after", "class": "pure_schema", "atoms": ("schema.validate",)},
            ],
            force=True,
        )


def test_fusion_preserves_atom_order_across_multiple_fusible_runs() -> None:
    fuse = _require("tigrbl_kernel.segment_fusion", "fuse_segments")

    fused = fuse(
        [
            {"segment_id": "ingress", "class": "pure_ingress", "atoms": ("ingress.parse",)},
            {"segment_id": "dispatch", "class": "pure_dispatch", "atoms": ("dispatch.select",)},
            {"segment_id": "handler", "class": "handler", "atoms": ("handler.call",)},
            {"segment_id": "shape", "class": "pure_egress_shape", "atoms": ("response.shape",)},
            {"segment_id": "serialize", "class": "pure_egress_shape", "atoms": ("response.serialize",)},
        ]
    )

    assert [segment["segment_id"] for segment in fused] == [
        "ingress+dispatch",
        "handler",
        "shape+serialize",
    ]
    assert fused[0]["atoms"] == ("ingress.parse", "dispatch.select")
    assert fused[2]["atoms"] == ("response.shape", "response.serialize")


def test_completion_fence_remains_after_transport_emit_barrier() -> None:
    fuse = _require("tigrbl_kernel.segment_fusion", "fuse_segments")

    fused = fuse(
        [
            {"segment_id": "shape", "class": "pure_egress_shape", "atoms": ("response.shape",)},
            {"segment_id": "emit", "class": "transport.emit", "atoms": ("transport.emit",)},
            {"segment_id": "complete", "class": "completion_fence", "atoms": ("transport.emit_complete",)},
        ]
    )

    assert [segment["segment_id"] for segment in fused] == ["shape", "emit", "complete"]
    assert fused[-1]["atoms"] == ("transport.emit_complete",)
