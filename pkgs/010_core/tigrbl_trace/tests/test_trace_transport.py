from tigrbl_trace import project_event, projection_context, summarize
from tigrbl_trace.wire import Batch


def test_existing_wire_v1_preserves_identity_and_excludes_payload():
    batch = Batch.model_validate(
        {
            "version": 1,
            "service": "notes",
            "environment": "local",
            "worker_boot_id": "a" * 32,
            "events": [
                {
                    "sequence": 1,
                    "captured_at": "2026-01-01T00:00:00Z",
                    "kind": "Transaction",
                    "transport": "REST",
                    "fields": {"transaction_id": "tx", "payload": "discard"},
                }
            ],
        }
    )
    assert batch.version == 1
    assert batch.events[0].fields == {"transaction_id": "tx"}


def test_project_http_uses_dispatch_evidence_then_legacy_path():
    incoming = {
        "sequence": 1,
        "at": "2026-01-01T00:00:00+00:00",
        "kind": "Scope opened",
        "transport": "HTTP",
        "correlation_id": "request",
    }
    invocation = {**incoming, "kind": "Invocation", "transport": "JSON-RPC"}
    context = projection_context([incoming, invocation])
    assert project_event(incoming, context)["transport"] == "http_jsonrpc"
    assert (
        project_event({**incoming, "path": "/rpc"}, projection_context([]))["transport"]
        == "http_jsonrpc"
    )


def test_project_and_summarize_existing_database_capture():
    native = {
        "sequence": 1,
        "at": "2026-01-01T00:00:00+00:00",
        "kind": "Transaction",
        "transport": "REST",
        "outcome": "committed",
        "engine_session_id": "session",
        "transaction_id": "tx",
        "measured_duration_ms": 2.5,
        "timing_boundary": "db_tx_begin_to_commit",
        "clock_domain": "engine_monotonic",
    }
    event = project_event(native, projection_context([native]))
    assert event["kind"] == "db.tx.commit"
    assert event["measured_duration_ms"] == 2.5
    assert event["timing_boundary"] == "db_tx_begin_to_commit"
    assert summarize([event])["transactions"] == 1
