from __future__ import annotations

from tigrbl_kernel.protocol_chains.websocket import (
    CORE_REALTIME_ATOMS,
    compile_websocket_chain,
)


def test_websocket_realtime_required_atoms_contract() -> None:
    chain = compile_websocket_chain({"path": "/ws/thread/{thread_id}", "scheme": "ws"})

    assert chain["realtime_atoms"] == CORE_REALTIME_ATOMS
    assert set(chain["realtime_atoms"]) == {
        "transport.accept",
        "transport.receive",
        "transport.emit",
        "transport.close",
        "framing.decode",
        "framing.encode",
        "dispatch.binding.match",
        "dispatch.binding.parse",
        "subscription.register",
        "subscription.unregister",
        "publish.prepare",
        "publish.enqueue",
        "publish.fanout",
    }


def test_websocket_realtime_atom_phase_placement_contract() -> None:
    placement = compile_websocket_chain({"path": "/ws/thread/{thread_id}", "scheme": "ws"})[
        "atom_phase_placement"
    ]

    assert placement["transport.accept"] == "SESSION_OPEN"
    assert placement["transport.receive"] == "MESSAGE_RECEIVE"
    assert placement["framing.decode"] == "INGRESS_PARSE"
    assert placement["dispatch.binding.match"] == "INGRESS_DISPATCH"
    assert placement["subscription.register"] == "POST_COMMIT"
    assert placement["subscription.unregister"] == "PRE_SESSION_CLOSE"
    assert placement["publish.prepare"] == "POST_COMMIT"
    assert placement["publish.enqueue"] == "POST_COMMIT"
    assert placement["publish.fanout"] == "EGRESS_FINALIZE"
    assert placement["framing.encode"] == "EGRESS_FINALIZE"
    assert placement["transport.emit"] == "EGRESS_FINALIZE"
    assert placement["transport.close"] == "SESSION_CLOSE"
