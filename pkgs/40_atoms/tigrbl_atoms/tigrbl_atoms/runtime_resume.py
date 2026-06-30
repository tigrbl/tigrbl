from __future__ import annotations

from dataclasses import dataclass, field
from time import monotonic
from typing import Any


RESUMABLE_SCOPE_BINDINGS = frozenset(
    {"http.stream", "https.stream", "http.sse", "https.sse", "ws", "wss", "webtransport"}
)


@dataclass(frozen=True, slots=True)
class ResumeScope:
    client_id: str
    session_id: str
    stream_id: str
    binding: str

    def __post_init__(self) -> None:
        for name, value in (
            ("client_id", self.client_id),
            ("session_id", self.session_id),
            ("stream_id", self.stream_id),
            ("binding", self.binding),
        ):
            if not isinstance(value, str) or not value:
                raise ValueError(f"{name} is required")
        if self.binding not in RESUMABLE_SCOPE_BINDINGS:
            raise ValueError(f"binding {self.binding!r} is not resumable")

    def as_dict(self) -> dict[str, str]:
        return {
            "client_id": self.client_id,
            "session_id": self.session_id,
            "stream_id": self.stream_id,
            "binding": self.binding,
        }


@dataclass(slots=True)
class ResumeLedgerEntry:
    scope: ResumeScope
    token: str
    ttl_seconds: int | None = None
    opened_at: float = field(default_factory=monotonic)
    next_offset: int = 0
    events: list[dict[str, Any]] = field(default_factory=list)
    closed: bool = False

    def expired(self, *, now: float | None = None) -> bool:
        if self.ttl_seconds is None:
            return False
        return (now if now is not None else monotonic()) >= self.opened_at + self.ttl_seconds


class ResumeLedger:
    def __init__(self, *, replay_window: int = 128) -> None:
        if replay_window < 1:
            raise ValueError("replay_window must be positive")
        self.replay_window = replay_window
        self._entries: dict[str, ResumeLedgerEntry] = {}

    def open(
        self,
        *,
        token: str,
        scope: ResumeScope,
        ttl_seconds: int | None = None,
        now: float | None = None,
    ) -> ResumeLedgerEntry:
        if not token:
            raise ValueError("resume token is required")
        if ttl_seconds is not None and ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        entry = ResumeLedgerEntry(
            scope=scope,
            token=token,
            ttl_seconds=ttl_seconds,
            opened_at=now if now is not None else monotonic(),
        )
        self._entries[token] = entry
        return entry

    def record(self, token: str, payload: dict[str, Any]) -> int:
        entry = self._entries[token]
        if entry.closed:
            raise ValueError("cannot record resume payload after close")
        if not isinstance(payload, dict):
            raise ValueError("resume payload must be a dict")
        entry.events.append(dict(payload))
        if len(entry.events) > self.replay_window:
            entry.events.pop(0)
        entry.next_offset += 1
        return entry.next_offset

    def close(self, token: str) -> None:
        self._entries[token].closed = True

    def resume(
        self,
        *,
        token: str,
        scope: ResumeScope,
        requested_offset: int = 0,
        now: float | None = None,
    ) -> dict[str, Any]:
        entry = self._entries.get(token)
        if entry is None:
            return {"accepted": False, "reason": "not_found"}
        if entry.expired(now=now):
            return {"accepted": False, "reason": "expired"}
        if entry.scope != scope:
            return {"accepted": False, "reason": "identity_mismatch"}
        oldest_offset = max(0, entry.next_offset - len(entry.events))
        if (
            not isinstance(requested_offset, int)
            or requested_offset < oldest_offset
            or requested_offset > entry.next_offset
        ):
            return {"accepted": False, "reason": "out_of_window"}
        replay_index = requested_offset - oldest_offset
        return {
            "accepted": True,
            "accepted_offset": requested_offset,
            "replay": tuple(entry.events[replay_index:]),
            "scope": entry.scope.as_dict(),
        }


__all__ = ["RESUMABLE_SCOPE_BINDINGS", "ResumeLedger", "ResumeLedgerEntry", "ResumeScope"]
