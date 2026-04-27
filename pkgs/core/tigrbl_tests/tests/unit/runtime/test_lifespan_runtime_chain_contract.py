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


def test_lifespan_startup_chain_sets_ready_after_successful_completion() -> None:
    run = _require("tigrbl_runtime.protocol.lifespan_chain", "run_lifespan_chain")
    trace: list[str] = []

    result = run(event="startup", handlers=(lambda state: state.update({"db": "ready"}),), trace=trace.append)

    assert trace == ["lifespan.startup.received", "lifespan.startup.handler", "lifespan.startup.complete"]
    assert result["ready"] is True
    assert result["state"]["db"] == "ready"


def test_lifespan_startup_failure_prevents_ready_state() -> None:
    run = _require("tigrbl_runtime.protocol.lifespan_chain", "run_lifespan_chain")

    def fail(_state):
        raise RuntimeError("database unavailable")

    result = run(event="startup", handlers=(fail,), capture_errors=True)

    assert result["ready"] is False
    assert result["completed"] is False
    assert result["error_ctx"]["subevent"] == "lifespan.startup"
    assert "database unavailable" in result["error_ctx"]["message"]


def test_lifespan_shutdown_runs_cleanup_and_clears_ready_state() -> None:
    run = _require("tigrbl_runtime.protocol.lifespan_chain", "run_lifespan_chain")
    cleanup: list[str] = []

    result = run(
        event="shutdown",
        initial_state={"ready": True, "db": "ready"},
        handlers=(lambda state: cleanup.append(state.pop("db")),),
    )

    assert cleanup == ["ready"]
    assert result["ready"] is False
    assert result["state"].get("db") is None
    assert result["completed"] is True


def test_lifespan_chain_compiles_kernelplan_owned_event_order() -> None:
    compile_chain = _require("tigrbl_kernel.protocol_chains.lifespan", "compile_lifespan_chain")

    chain = compile_chain(event="startup")

    assert chain["owner"] == "kernelplan"
    assert chain["subevent"] == "lifespan.startup"
    assert chain["atoms"] == (
        "lifespan.receive",
        "lifespan.run_handlers",
        "state.ready.set",
        "lifespan.complete",
    )


def test_lifespan_shutdown_failure_still_reports_cleanup_error_context() -> None:
    run = _require("tigrbl_runtime.protocol.lifespan_chain", "run_lifespan_chain")

    def cleanup(_state):
        raise RuntimeError("cleanup failed")

    result = run(event="shutdown", handlers=(cleanup,), capture_errors=True)

    assert result["ready"] is False
    assert result["completed"] is False
    assert result["error_ctx"]["subevent"] == "lifespan.shutdown"
    assert result["error_ctx"]["phase"] == "HANDLER"
