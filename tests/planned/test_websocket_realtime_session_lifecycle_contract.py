from __future__ import annotations

import ast
from pathlib import Path

from tigrbl_kernel.protocol_chains.websocket import compile_websocket_chain


EXPECTED_PHASES = (
    "SESSION_OPEN",
    "POST_SESSION_OPEN",
    "MESSAGE_RECEIVE",
    "INGRESS_PARSE",
    "INGRESS_DISPATCH",
    "PRE_TX_BEGIN",
    "START_TX",
    "PRE_HANDLER",
    "HANDLER",
    "POST_HANDLER",
    "PRE_COMMIT",
    "TX_COMMIT",
    "POST_COMMIT",
    "EGRESS_SHAPE",
    "EGRESS_FINALIZE",
    "POST_RESPONSE",
    "PRE_SESSION_CLOSE",
    "SESSION_CLOSE",
    "POST_SESSION_CLOSE",
)


def test_websocket_session_phase_order_contract() -> None:
    chain = compile_websocket_chain({"path": "/ws/thread/{thread_id}", "scheme": "ws"})

    assert chain["lifecycle_phases"] == EXPECTED_PHASES
    assert chain["structural_phases"] == (
        "SESSION_OPEN",
        "MESSAGE_RECEIVE",
        "SESSION_CLOSE",
    )
    assert chain["hook_phases"] == (
        "POST_SESSION_OPEN",
        "PRE_SESSION_CLOSE",
        "POST_SESSION_CLOSE",
    )


def test_websocket_session_close_cleanup_order_contract() -> None:
    chain = compile_websocket_chain({"path": "/ws/thread/{thread_id}", "scheme": "ws"})
    phases = chain["lifecycle_phases"]
    placement = chain["atom_phase_placement"]

    assert phases.index("PRE_SESSION_CLOSE") < phases.index("SESSION_CLOSE")
    assert phases.index("SESSION_CLOSE") < phases.index("POST_SESSION_CLOSE")
    assert placement["subscription.unregister"] == "PRE_SESSION_CLOSE"
    assert placement["transport.close"] == "SESSION_CLOSE"
    assert chain["loop_region"]["exit_target"] == "PRE_SESSION_CLOSE"


def test_websocket_app_handler_does_not_own_loop_contract() -> None:
    source = Path("examples/websocket_realtime_ops/app.py").read_text()
    tree = ast.parse(source)
    assigned_names = {
        target.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    }
    constructor_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }

    assert not any(
        isinstance(node, ast.AsyncFunctionDef)
        and node.name == "websocket_realtime_kernel_owned"
        for node in ast.walk(tree)
    )
    assert not any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "websocket"
        for node in ast.walk(tree)
    )
    assert {"APP_SPEC", "REALTIME_PATH"}.issubset(assigned_names)
    assert {"AppSpec", "PathSpec"}.issubset(constructor_names)
