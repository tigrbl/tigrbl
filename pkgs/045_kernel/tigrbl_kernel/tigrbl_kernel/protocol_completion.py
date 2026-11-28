from __future__ import annotations

from typing import Any


def compile_completion_fence(binding: dict[str, Any]) -> dict[str, Any]:
    transport = binding.get("transport")
    needs_fence = transport in {"stream", "websocket", "webtransport", "datagram"} or binding.get("phase") == "EMIT"
    if not needs_fence and binding.get("send_completion") == "synchronous":
        return {
            "completion_fence": None,
            "runtime_owned": True,
            "public_hook_phase": False,
            "after_phase": binding.get("phase", "EMIT"),
            "explicit_ack_required": False,
        }
    return {
        "completion_fence": "POST_EMIT",
        "runtime_owned": True,
        "public_hook_phase": False,
        "after_phase": binding.get("phase", "EMIT"),
        "explicit_ack_required": True,
    }


def validate_completion_hook_phase(phase: str) -> None:
    if phase == "POST_EMIT":
        raise ValueError("POST_EMIT is a runtime-owned completion fence hook phase")


__all__ = ["compile_completion_fence", "validate_completion_hook_phase"]
