from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


RESUME_CAPABLE_BINDINGS = frozenset(
    {"http.stream", "https.stream", "http.sse", "https.sse", "ws", "wss", "webtransport"}
)
RESUME_MODES = frozenset({"disabled", "cursor", "stateful", "replay"})


@dataclass(frozen=True, slots=True)
class ResumePolicy:
    mode: str = "disabled"
    token_field: str = "resume_token"
    offset_field: str = "requested_offset"
    replay_window: int = 0
    ttl_seconds: int | None = None

    def __post_init__(self) -> None:
        if self.mode not in RESUME_MODES:
            raise ValueError(f"unsupported resume mode {self.mode!r}")
        if not self.token_field:
            raise ValueError("resume token_field is required")
        if not self.offset_field:
            raise ValueError("resume offset_field is required")
        if self.replay_window < 0:
            raise ValueError("resume replay_window must be non-negative")
        if self.ttl_seconds is not None and self.ttl_seconds <= 0:
            raise ValueError("resume ttl_seconds must be positive")

    @property
    def enabled(self) -> bool:
        return self.mode != "disabled"

    def as_dict(self) -> dict[str, object]:
        return {
            "mode": self.mode,
            "token_field": self.token_field,
            "offset_field": self.offset_field,
            "replay_window": self.replay_window,
            "ttl_seconds": self.ttl_seconds,
        }


def compile_resume_policy(binding_kind: str, binding: Mapping[str, Any]) -> ResumePolicy:
    raw = binding.get("resume") or binding.get("resume_policy")
    if raw in (None, False):
        return ResumePolicy()
    if raw is True:
        raw = {"mode": "stateful"}
    if not isinstance(raw, Mapping):
        raise ValueError("resume policy must be a mapping or boolean")
    if binding_kind not in RESUME_CAPABLE_BINDINGS:
        raise ValueError(f"{binding_kind} does not support stream resume policy")

    mode = str(raw.get("mode", "stateful"))
    policy = ResumePolicy(
        mode=mode,
        token_field=str(raw.get("token_field", "resume_token")),
        offset_field=str(raw.get("offset_field", "requested_offset")),
        replay_window=int(raw.get("replay_window", 0)),
        ttl_seconds=(
            int(raw["ttl_seconds"])
            if raw.get("ttl_seconds") is not None
            else None
        ),
    )
    if policy.enabled and binding_kind in {"http.stream", "https.stream"} and mode == "cursor":
        raise ValueError("HTTP stream resume cursor mode is reserved for SSE")
    return policy


__all__ = ["RESUME_CAPABLE_BINDINGS", "RESUME_MODES", "ResumePolicy", "compile_resume_policy"]
