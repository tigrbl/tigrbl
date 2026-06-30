from __future__ import annotations

import pytest

from tigrbl_atoms.runtime_resume import ResumeLedger, ResumeScope
from tigrbl_kernel.protocol_bindings import compile_binding_protocol_plan


def _scope(**overrides: str) -> ResumeScope:
    values = {
        "client_id": "client-a",
        "session_id": "session-a",
        "stream_id": "stream-a",
        "binding": "webtransport",
    }
    values.update(overrides)
    return ResumeScope(**values)


def test_stream_resume_t2_rejects_expired_and_identity_mismatch() -> None:
    ledger = ResumeLedger(replay_window=2)
    scope = _scope()
    ledger.open(token="rt-a", scope=scope, ttl_seconds=10, now=100.0)

    expired = ledger.resume(token="rt-a", scope=scope, now=111.0)
    mismatch = ledger.resume(token="rt-a", scope=_scope(client_id="client-b"), now=105.0)

    assert expired == {"accepted": False, "reason": "expired"}
    assert mismatch == {"accepted": False, "reason": "identity_mismatch"}


def test_stream_resume_t2_rejects_stale_offsets_after_replay_window_trim() -> None:
    ledger = ResumeLedger(replay_window=2)
    scope = _scope(binding="ws")
    ledger.open(token="rt-a", scope=scope)
    ledger.record("rt-a", {"chunk": "first"})
    ledger.record("rt-a", {"chunk": "second"})
    ledger.record("rt-a", {"chunk": "third"})

    assert ledger.resume(token="rt-a", scope=scope, requested_offset=0) == {
        "accepted": False,
        "reason": "out_of_window",
    }
    assert ledger.resume(token="rt-a", scope=scope, requested_offset=1)["replay"] == (
        {"chunk": "second"},
        {"chunk": "third"},
    )


def test_stream_resume_t2_rejects_invalid_scope_ttl_offset_and_closed_recording() -> None:
    ledger = ResumeLedger()
    scope = _scope(binding="http.sse")

    with pytest.raises(ValueError, match="not resumable"):
        _scope(binding="http.rest")
    with pytest.raises(ValueError, match="ttl_seconds"):
        ledger.open(token="rt-a", scope=scope, ttl_seconds=0)

    ledger.open(token="rt-a", scope=scope)
    ledger.close("rt-a")
    with pytest.raises(ValueError, match="after close"):
        ledger.record("rt-a", {"chunk": "late"})
    assert ledger.resume(token="rt-a", scope=scope, requested_offset=-1) == {
        "accepted": False,
        "reason": "out_of_window",
    }


def test_stream_resume_t2_requires_window_for_cursor_and_replay_modes() -> None:
    with pytest.raises(ValueError, match="replay_window"):
        compile_binding_protocol_plan(
            "Events.tail",
            {"kind": "http.sse", "path": "/events", "resume": {"mode": "cursor"}},
        )
    with pytest.raises(ValueError, match="replay_window"):
        compile_binding_protocol_plan(
            "Events.tail",
            {"kind": "webtransport", "path": "/wt", "resume": {"mode": "replay"}},
        )
