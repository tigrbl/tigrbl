from __future__ import annotations

import importlib
from pathlib import Path

import pytest


REMOVED_RUNTIME_SHIMS = (
    "tigrbl_runtime.callbacks",
    "tigrbl_runtime.transactions",
    "tigrbl_runtime.channel.state",
    "tigrbl_runtime.executors.helpers",
    "tigrbl_runtime.executors.loop_regions",
    "tigrbl_runtime.protocol.anchors",
    "tigrbl_runtime.protocol.app_frame_codec",
    "tigrbl_runtime.protocol.completion_fence",
    "tigrbl_runtime.protocol.dispatch_atoms",
    "tigrbl_runtime.protocol.framing_atoms",
    "tigrbl_runtime.protocol.http_stream",
    "tigrbl_runtime.protocol.http_unary",
    "tigrbl_runtime.protocol.lifespan_chain",
    "tigrbl_runtime.protocol.loop_modes",
    "tigrbl_runtime.protocol.scope_schemas",
    "tigrbl_runtime.protocol.sse",
    "tigrbl_runtime.protocol.static_files",
    "tigrbl_runtime.protocol.transport_atoms",
    "tigrbl_runtime.protocol.webtransport",
    "tigrbl_runtime.protocol.websocket",
    "tigrbl_runtime.runtime.events",
    "tigrbl_runtime.runtime.kernel",
    "tigrbl_runtime.runtime.labels",
    "tigrbl_runtime.runtime.executor",
)


@pytest.mark.parametrize("module_name", REMOVED_RUNTIME_SHIMS)
def test_runtime_shim_modules_are_removed(module_name: str) -> None:
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module(module_name)


def test_runtime_package_source_does_not_consume_runtime_shims() -> None:
    runtime_module = importlib.import_module("tigrbl_runtime")
    runtime_root = Path(runtime_module.__file__).parent
    forbidden = (
        "from tigrbl_runtime.protocol",
        "import tigrbl_runtime.protocol",
        "from tigrbl_runtime.callbacks",
        "import tigrbl_runtime.callbacks",
        "from tigrbl_runtime.transactions",
        "import tigrbl_runtime.transactions",
        "from tigrbl_runtime.channel.state",
        "import tigrbl_runtime.channel.state",
        "from tigrbl_runtime.executors.helpers",
        "import tigrbl_runtime.executors.helpers",
        "from tigrbl_runtime.executors.loop_regions",
        "import tigrbl_runtime.executors.loop_regions",
        "from tigrbl_runtime.runtime.kernel",
        "import tigrbl_runtime.runtime.kernel",
        "from tigrbl_runtime.runtime.executor",
        "import tigrbl_runtime.runtime.executor",
        "from tigrbl_runtime.runtime.events",
        "import tigrbl_runtime.runtime.events",
        "from tigrbl_runtime.runtime.labels",
        "import tigrbl_runtime.runtime.labels",
        "from tigrbl_runtime.runtime.status",
        "import tigrbl_runtime.runtime.status",
    )

    offenders: list[tuple[str, str]] = []
    for path in runtime_root.rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        for needle in forbidden:
            if needle in source:
                offenders.append((path.relative_to(runtime_root).as_posix(), needle))

    assert offenders == []


def test_packed_executor_private_helpers_delegate_to_owner_packages() -> None:
    from tigrbl_atoms.atoms.transport.websocket_unary import DirectWebSocketUnary
    from tigrbl_kernel.packed_access import http_method_id, stable_name_hash64
    from tigrbl_runtime.executors import packed
    from tigrbl_runtime.executors.packed import PackedPlanExecutor

    assert packed._DirectWebSocketUnary is DirectWebSocketUnary
    assert PackedPlanExecutor._http_method_id("POST") == http_method_id("POST")
    assert PackedPlanExecutor._stable_name_hash64("/items") == stable_name_hash64(
        "/items"
    )
