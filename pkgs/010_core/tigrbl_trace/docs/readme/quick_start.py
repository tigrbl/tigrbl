from tigrbl_trace import project_event, projection_context

native = {
    "sequence": 1,
    "at": "2026-01-01T00:00:00+00:00",
    "kind": "Transaction",
    "transport": "REST",
    "outcome": "begin",
    "engine_session_id": "session",
    "transaction_id": "transaction",
}
event = project_event(native, projection_context([native]))
assert event is not None and event["kind"] == "db.tx.begin"
