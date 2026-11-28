from __future__ import annotations

import pytest

from tigrbl_core._spec.app_spec import AppSpec


def test_collect_reads_scalar_and_sequence_attributes() -> None:
    class DemoApp:
        TITLE = "Demo"
        DESCRIPTION = "desc"
        VERSION = "1.0.0"
        EXECUTION_BACKEND = "python"
        JSONRPC_PREFIX = "/r"
        SYSTEM_PREFIX = "/s"
        ROUTERS = ("router",)
        OPS = ("op",)

    spec = AppSpec.collect(DemoApp)

    assert spec.title == "Demo"
    assert spec.description == "desc"
    assert spec.version == "1.0.0"
    assert spec.execution_backend == "python"
    assert spec.jsonrpc_prefix == "/r"
    assert spec.system_prefix == "/s"
    assert spec.routers == ("router",)
    assert spec.ops == ("op",)


def test_collect_falls_back_to_defaults() -> None:
    class EmptyApp:
        pass

    spec = AppSpec.collect(EmptyApp)

    assert spec.title == "Tigrbl"
    assert spec.version == "0.1.0"
    assert spec.execution_backend == "auto"
    assert spec.jsonrpc_prefix == "/rpc"
    assert spec.system_prefix == "/system"


def test_collect_rejects_unknown_execution_backend() -> None:
    class DemoApp:
        EXECUTION_BACKEND = "native"

    with pytest.raises(ValueError, match="unsupported execution backend"):
        AppSpec.collect(DemoApp)
