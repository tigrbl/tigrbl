from tigrbl_kernel.trace import Timeline
from tigrbl_typing.trace import emit_trace


def test_timeline_filters_fields_and_keeps_the_latest_records():
    timeline = Timeline(max_events=2)
    emit_trace(timeline.add, "Invocation", "REST", {"invocation_id": "evicted"})
    timeline.add("Invocation", "REST", {"invocation_id": "retained", "body": "private"})
    emit_trace(
        timeline.add,
        "Delivery",
        "WebSocket",
        {
            "subscription_id": "sub",
            "rpc_id": {"invalid": True},
            "payload": "private",
        },
    )
    snapshot = timeline.data()
    assert snapshot["revision"] == 3
    first, second = snapshot["events"]
    assert first["invocation_id"] == "retained" and "body" not in first
    assert (
        second["subscription_id"] == "sub"
        and "payload" not in second
        and "rpc_id" not in second
    )
    first["invocation_id"] = "modified"
    assert timeline.data()["events"][0]["invocation_id"] == "retained"


def test_failing_trace_sink_does_not_fail_dispatch(caplog):
    def fail(*args):
        raise RuntimeError("backend unavailable")

    emit_trace(fail, "Response", "HTTP", {"status": 200})
    assert "Trace sink rejected a diagnostic event" in caplog.text


def test_owned_session_lifecycle_fallback_excludes_past_transactions():
    from types import SimpleNamespace

    from tigrbl_kernel.trace import record_execution

    past = {
        "engine_session_id": "engine",
        "transaction_id": "past",
        "outcome": "committed",
    }
    begin = {
        "engine_session_id": "engine",
        "transaction_id": "current",
        "outcome": "begin",
    }
    commit = {**begin, "outcome": "committed"}
    provider = SimpleNamespace(transaction_events=lambda: (past, begin, commit))
    ctx = SimpleNamespace(
        temp={
            "identity": {"invocation_id": "invocation"},
            "_trace_transaction_baseline": (past,),
        }
    )
    timeline = Timeline()
    record_execution(
        timeline.add, {"type": "http"}, ctx, jsonrpc=False, owned_session=provider
    )
    transactions = timeline.data()["rollup"]["transactions"]
    assert transactions == [
        {
            "engine_session_id": "engine",
            "transaction_id": "current",
            "invocations": ["invocation"],
            "outcomes": ["begin", "committed"],
        }
    ]
