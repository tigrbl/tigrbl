from tigrbl_kernel.identity_rollup import rollup_identity_records


def test_rollup_retains_recipient_and_transaction_participation_without_double_counting():
    tx = {"engine_session_id": "engine", "transaction_id": "tx"}
    records = [
        {"transport_session_id": "wt1", "correlation_id": "c1", "datagram_id": "d1"},
        {"transport_session_id": "wt1", "correlation_id": "c1", "stream_correlation_id": "sc1", "invocation_id": "i1"},
        {"transport_session_id": "wt2", "correlation_id": "c2", "subscription_id": "sub"},
        {"transport_session_id": "wt1", "correlation_id": "c1", "subscription_id": "sub"},
        {**tx, "outcome": "begin"},
        {**tx, "outcome": "committed"},
        {**tx, "invocation_id": "i1"},
        {**tx, "invocation_id": "i2"},
    ]
    result = rollup_identity_records(records)
    assert result["sessions"]["c1"] == {"streams": {"sc1": ["i1"]}, "datagrams": ["d1"]}
    assert result["subscriptions"] == {"sub": ["wt1", "wt2"]}
    assert result["transactions"] == [
        {**tx, "invocations": ["i1", "i2"], "outcomes": ["begin", "committed"]}
    ]
