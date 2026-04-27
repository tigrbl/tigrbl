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


def test_callback_registration_produces_first_class_runtime_descriptor() -> None:
    register = _require("tigrbl_runtime.callbacks", "register_callback")

    descriptor = register(
        name="inventory.after_emit",
        kind="hook",
        language="python",
        phase="POST_EMIT",
    )

    assert descriptor == {
        "name": "inventory.after_emit",
        "kind": "hook",
        "language": "python",
        "phase": "POST_EMIT",
        "callback_fence": "required",
    }


def test_callback_metadata_compiles_into_kernelplan_without_callable_object() -> None:
    compile_callbacks = _require("tigrbl_kernel.callbacks", "compile_callback_metadata")

    compiled = compile_callbacks(
        [
            {
                "name": "inventory.after_emit",
                "kind": "hook",
                "language": "python",
                "phase": "POST_EMIT",
                "callback": object(),
            }
        ]
    )

    assert compiled[0]["name"] == "inventory.after_emit"
    assert compiled[0]["callback_ref"] == "inventory.after_emit"
    assert "callback" not in compiled[0]
    assert compiled[0]["ffi_boundary"] == "python"


def test_callback_fence_records_enter_and_exit_in_order() -> None:
    run_fence = _require("tigrbl_runtime.callbacks", "run_callback_fence")
    trace: list[str] = []

    result = run_fence(
        {"name": "inventory.after_emit", "kind": "hook"},
        callback=lambda ctx: {"ok": True, "ctx": ctx["op"]},
        ctx={"op": "Inventory.read"},
        trace=trace.append,
    )

    assert trace == [
        "callback_fence_enter:inventory.after_emit",
        "callback_fence_exit:inventory.after_emit",
    ]
    assert result == {"ok": True, "ctx": "Inventory.read"}


def test_missing_callback_fails_before_invocation_with_typed_error_context() -> None:
    run_fence = _require("tigrbl_runtime.callbacks", "run_callback_fence")

    with pytest.raises(ValueError) as exc_info:
        run_fence(
            {"name": "inventory.missing", "kind": "handler"},
            callback=None,
            ctx={"op": "Inventory.read"},
        )

    metadata = getattr(exc_info.value, "metadata", {})
    assert metadata["callback"] == "inventory.missing"
    assert metadata["kind"] == "handler"
    assert metadata["error"] == "callback_missing"


def test_callback_exception_is_wrapped_with_phase_and_callback_metadata() -> None:
    run_fence = _require("tigrbl_runtime.callbacks", "run_callback_fence")

    def failing_callback(_ctx):
        raise RuntimeError("callback exploded")

    result = run_fence(
        {"name": "inventory.after_emit", "kind": "hook", "phase": "POST_EMIT"},
        callback=failing_callback,
        ctx={"op": "Inventory.read"},
        capture_errors=True,
    )

    assert result["ok"] is False
    assert result["error_ctx"]["callback"] == "inventory.after_emit"
    assert result["error_ctx"]["phase"] == "POST_EMIT"
    assert "callback exploded" in result["error_ctx"]["message"]


def test_callback_descriptor_roundtrips_through_runtime_codec() -> None:
    encode = _require("tigrbl_runtime.callbacks", "encode_callback_descriptor")
    decode = _require("tigrbl_runtime.callbacks", "decode_callback_descriptor")
    descriptor = {
        "name": "inventory.engine",
        "kind": "engine",
        "language": "python",
        "phase": "HANDLER",
        "ffi_boundary": "python",
    }

    encoded = encode(descriptor)

    assert isinstance(encoded, dict)
    assert decode(encoded) == descriptor
