from trace_lab_demo.capture import RETENTION, Capture


def test_native_capture_preserves_identity_and_counts_transactions_once(buffer):
    capture = Capture(buffer)
    capture.active_run = "demo"
    capture.add(
        "Invocation", "WebSocket", {"invocation_id": "publish", "payload": "secret"}
    )
    capture.add(
        "Publication",
        "Realtime",
        {"origin_invocation_id": "publish", "publication_id": "publication"},
    )
    fields = {"engine_session_id": "engine", "transaction_id": "tx"}
    capture.add("Transaction", "REST", {**fields, "outcome": "begin"})
    capture.add("Transaction", "REST", {**fields, "outcome": "committed"})
    capture.add(
        "webtransport.stream.receive",
        "WebTransport",
        {"stream_id": 2**59 + 1, "stream_correlation_id": "stream-correlation"},
    )
    data = capture.snapshot()
    assert data["running"]
    assert data["rollup"]["transactions"] == 1
    assert data["rollup"]["publications"] == 1
    assert data["events"][1]["transport"] == "websocket"
    assert data["events"][3]["kind"] == "db.tx.commit"
    assert data["events"][4]["stream_id"] == str(2**59 + 1)
    assert all(row["scenario_run_id"] == "demo" for row in data["events"])
    assert "payload" not in data["events"][0]


def test_capture_reports_when_the_retention_window_has_moved(buffer):
    capture = Capture(buffer)
    assert capture.snapshot()["retained_range"]["max_sequence"] == 0
    for _ in range(RETENTION + 1):
        capture.add("Scope opened", "HTTP", {"path": "/notes"})
    data = capture.snapshot()
    assert len(data["events"]) == RETENTION
    assert data["retained_range"]["min_sequence"] == 2
    assert data["retained_range"]["evicted_count"] == 1
