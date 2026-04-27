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


def test_wildcard_hook_selectors_expand_to_concrete_eventkey_buckets() -> None:
    compile_buckets = _require("tigrbl_kernel.eventkey_hooks", "compile_hook_buckets")

    buckets = compile_buckets(
        hooks=[
            {
                "hook_id": "socket-any",
                "phase": "HANDLER",
                "family": "socket",
                "subevent": "*",
            }
        ],
        event_catalog=[
            {"family": "socket", "subevent": "message.received"},
            {"family": "socket", "subevent": "session.close"},
            {"family": "event_stream", "subevent": "message.emit"},
        ],
    )

    assert set(buckets) == {"message.received", "session.close"}
    assert all(bucket["hook_ids"] == ("socket-any",) for bucket in buckets.values())
    assert all(isinstance(bucket["event_key"], int) for bucket in buckets.values())


def test_hook_bucket_compilation_detects_bucket_collisions() -> None:
    compile_buckets = _require("tigrbl_kernel.eventkey_hooks", "compile_hook_buckets")

    with pytest.raises(ValueError, match="bucket|collision|ambiguous"):
        compile_buckets(
            hooks=[
                {"hook_id": "first", "phase": "HANDLER", "family": "socket", "subevent": "message.received"},
                {"hook_id": "second", "phase": "HANDLER", "family": "socket", "subevent": "message.received"},
            ],
            event_catalog=[{"family": "socket", "subevent": "message.received"}],
        )


def test_hook_bucket_runtime_lookup_is_direct_by_eventkey() -> None:
    lookup = _require("tigrbl_kernel.eventkey_hooks", "lookup_hook_bucket")

    bucket = lookup(0x01020304, {0x01020304: ("hook-a", "hook-b")})

    assert bucket == ("hook-a", "hook-b")

