from __future__ import annotations

import pytest

from tigrbl_atoms.runtime_resume import ResumeLedger, ResumeScope
from tigrbl_kernel.protocol_bindings import compile_binding_protocol_plan


def test_stream_resume_t0_binding_plan_declares_policy_when_requested() -> None:
    plan = compile_binding_protocol_plan(
        "Events.tail",
        {
            "kind": "http.sse",
            "path": "/events",
            "resume": {
                "mode": "cursor",
                "token_field": "last_event_id",
                "offset_field": "requested_offset",
                "replay_window": 32,
                "ttl_seconds": 60,
            },
        },
    )

    assert plan["resume_policy"] == {
        "mode": "cursor",
        "token_field": "last_event_id",
        "offset_field": "requested_offset",
        "replay_window": 32,
        "ttl_seconds": 60,
    }
    assert plan["event_key_inputs"]["resume_mode"] == "cursor"


def test_stream_resume_t1_ledger_replays_matching_scope_from_offset() -> None:
    ledger = ResumeLedger(replay_window=8)
    scope = ResumeScope(
        client_id="client-a",
        session_id="session-a",
        stream_id="stream-a",
        binding="webtransport",
    )
    ledger.open(token="rt-a", scope=scope, ttl_seconds=60, now=100.0)
    ledger.record("rt-a", {"chunk": "a"})
    ledger.record("rt-a", {"chunk": "b"})
    ledger.close("rt-a")

    decision = ledger.resume(token="rt-a", scope=scope, requested_offset=1, now=120.0)

    assert decision["accepted"] is True
    assert decision["accepted_offset"] == 1
    assert decision["replay"] == ({"chunk": "b"},)
    assert decision["scope"] == scope.as_dict()


def test_stream_resume_t1_rejects_cursor_mode_for_raw_http_streams() -> None:
    with pytest.raises(ValueError, match="reserved for SSE"):
        compile_binding_protocol_plan(
            "Stream.tail",
            {
                "kind": "http.stream",
                "path": "/stream",
                "resume": {"mode": "cursor"},
            },
        )
