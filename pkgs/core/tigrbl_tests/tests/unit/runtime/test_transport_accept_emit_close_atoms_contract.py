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


def test_transport_accept_atom_runs_before_receive_and_decode() -> None:
    compile_chain = _require("tigrbl_kernel.transport_atoms", "compile_transport_atom_chain")

    chain = compile_chain(binding="websocket", subevent="message.received")

    anchors = chain["anchors"]
    assert anchors.index("transport.accept") < anchors.index("transport.receive")
    assert anchors.index("transport.receive") < anchors.index("framing.decode")
    assert chain["barriers"]["transport.accept"] is True


def test_transport_emit_atom_runs_after_framing_encode_and_before_completion() -> None:
    compile_chain = _require("tigrbl_kernel.transport_atoms", "compile_transport_atom_chain")

    chain = compile_chain(binding="http.sse", subevent="message.emit")

    anchors = chain["anchors"]
    assert anchors.index("framing.encode") < anchors.index("transport.emit")
    assert anchors.index("transport.emit") < anchors.index("transport.emit_complete")
    assert chain["barriers"]["transport.emit"] is True


def test_transport_close_atom_runs_after_loop_exit_or_error() -> None:
    compile_chain = _require("tigrbl_kernel.transport_atoms", "compile_transport_atom_chain")

    chain = compile_chain(binding="websocket", subevent="session.close")

    assert chain["anchors"][-1] == "transport.close"
    assert chain["barriers"]["transport.close"] is True
    assert chain["err_target"] == "transport.close"


def test_emit_complete_atom_requires_acknowledged_transport_send() -> None:
    run_emit = _require("tigrbl_runtime.protocol.transport_atoms", "run_transport_emit")
    trace: list[str] = []

    result = run_emit(
        {"subevent": "message.emit", "payload": b"ready"},
        send=lambda message: "ack",
        trace=trace.append,
    )

    assert trace == ["transport.emit", "transport.emit_complete"]
    assert result["completed"] is True


@pytest.mark.parametrize("send_result", ("queued", "scheduled", "buffered"))
def test_emit_complete_atom_does_not_fire_for_unacknowledged_send(send_result: str) -> None:
    run_emit = _require("tigrbl_runtime.protocol.transport_atoms", "run_transport_emit")
    trace: list[str] = []

    result = run_emit(
        {"subevent": "message.emit", "payload": b"ready"},
        send=lambda message: send_result,
        trace=trace.append,
    )

    assert trace == ["transport.emit"]
    assert result["completed"] is False


def test_transport_accept_emit_close_atoms_are_hard_fusion_barriers() -> None:
    fuse = _require("tigrbl_kernel.segment_fusion", "fuse_segments")

    with pytest.raises(ValueError, match="barrier|transport.accept|transport.emit|transport.close"):
        fuse(
            [
                {"segment_id": "accept", "class": "transport.accept", "atoms": ("transport.accept",)},
                {"segment_id": "decode", "class": "pure_framing", "atoms": ("framing.decode",)},
                {"segment_id": "emit", "class": "transport.emit", "atoms": ("transport.emit",)},
                {"segment_id": "close", "class": "transport.close", "atoms": ("transport.close",)},
            ],
            force=True,
        )
