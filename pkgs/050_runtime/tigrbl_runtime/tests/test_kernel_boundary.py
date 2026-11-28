from __future__ import annotations

import pytest

from tigrbl_runtime import runtime as runtime_api
from tigrbl_runtime.executors.kernel_executor import (
    _run,
    _run_phase_chain,
    invoke_op,
    resolve_phase_chains,
)


def test_runtime_api_does_not_export_kernel_planning_shims() -> None:
    for name in ("Kernel", "build_phase_chains", "get_cached_specs", "_default_kernel"):
        with pytest.raises(AttributeError):
            getattr(runtime_api, name)


def test_runtime_executor_methods_remain_runtime_owned() -> None:
    assert _run.__module__ == "tigrbl_runtime.executors.kernel_executor"
    assert _run_phase_chain.__module__ == "tigrbl_runtime.executors.kernel_executor"
    assert invoke_op.__module__ == "tigrbl_runtime.executors.kernel_executor"
    assert resolve_phase_chains.__module__ == "tigrbl_runtime.executors.kernel_executor"


def test_lowering_services_preserve_kernel_function_identity() -> None:
    from tigrbl_runtime.lowering_services import (
        compile_opview_from_specs,
        build_websocket_jsonrpc_session_handler,
    )
    from tigrbl_kernel.opview_compiler import compile_opview_from_specs as compile_owner
    from tigrbl_kernel.protocol_chains.websocket import build_websocket_jsonrpc_session_handler as websocket_owner

    assert compile_opview_from_specs is compile_owner
    assert build_websocket_jsonrpc_session_handler is websocket_owner


def test_lowering_services_reject_unknown_names() -> None:
    from tigrbl_runtime import lowering_services

    with pytest.raises(AttributeError):
        getattr(lowering_services, "unknown_lowering_service")


def test_runtime_requires_published_webtransport_kernel_and_atom_apis():
    from pathlib import Path
    try:
        import tomllib
    except ModuleNotFoundError:
        import tomli as tomllib
    from packaging.requirements import Requirement
    from packaging.version import Version

    manifest = tomllib.loads((Path(__file__).parents[1] / "pyproject.toml").read_text())
    requirements = {item.name: item for item in map(Requirement, manifest["project"]["dependencies"])}
    for name in ("tigrbl-kernel", "tigrbl-atoms"):
        assert Version("0.4.5.dev4") not in requirements[name].specifier
        assert Version("0.4.5.dev5") in requirements[name].specifier
