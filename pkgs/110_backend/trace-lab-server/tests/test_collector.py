import httpx
import pytest
from trace_lab.gateway import FAVICON_PATH


@pytest.mark.asyncio
async def test_persists_deduplicates_and_filters_timeline(tmp_path):
    from tigrbl.factories.engine import sqlitef
    from tigrbl_engine_sqlite.plugin import register
    from trace_lab.collector import build_collector, collector_gateway

    register()
    (tmp_path / "index.html").write_text('<div id="root"></div>')
    engine = sqlitef(str(tmp_path / "timeline.sqlite3"))
    app = await build_collector(engine)
    gateway = collector_gateway(app, tmp_path, "ingest", "operator", "password")
    batch = {
        "version": 1,
        "service": "primary",
        "environment": "test",
        "worker_boot_id": "a" * 32,
        "events": [
            {
                "sequence": sequence,
                "captured_at": "2026-11-25T12:00:00Z",
                "kind": "Invocation",
                "transport": "REST",
                "fields": {
                    "correlation_id": correlation,
                    "invocation_id": f"invocation-{sequence}",
                    "request_id": f"request-{sequence}",
                    "payload": "private",
                },
            }
            for sequence, correlation in enumerate(("one", "two"), start=1)
        ],
    }
    path = "/internal/trace/batches"
    ingest = {"Authorization": "Bearer ingest"}
    operator = ("operator", "password")
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=gateway), base_url="http://test"
    ) as client:
        favicon = await client.get("/favicon.svg")
        assert favicon.is_success
        assert favicon.headers["content-type"].startswith("image/svg+xml")
        assert favicon.content == FAVICON_PATH.read_bytes()
        assert (await client.get("/api/timeline")).status_code == 401
        assert (await client.post(path, auth=operator, json=batch)).status_code == 401
        invalid = {**batch, "events": [*batch["events"], {"sequence": 3}]}
        rejected = await client.post(path, headers=ingest, json=invalid)
        assert rejected.status_code == 422, rejected.text
        assert (await client.get("/api/timeline", auth=operator)).json()["events"] == []
        first = await client.post(path, headers=ingest, json=batch)
        assert first.is_success, first.text
        assert first.json() == {"received": 2, "inserted": 2}
        assert (await client.post(path, headers=ingest, json=batch)).json()[
            "inserted"
        ] == 0
        page = (await client.get("/api/timeline?limit=1", auth=operator)).json()
        assert page["events"][0]["correlation_id"] == "two"
        older = await client.get(
            "/api/timeline", params={"before": page["next_before"]}, auth=operator
        )
        assert older.json()["events"][0]["correlation_id"] == "one"
        selected = await client.get("/api/timeline?correlation_id=one", auth=operator)
        assert len(selected.json()["events"]) == 1
        assert "private" not in selected.text
        assert "data-trace-monitor" in (await client.get("/", auth=operator)).text
        distribution = await client.get("/distributions", auth=operator)
        assert distribution.is_success and "data-trace-monitor" in distribution.text
        detail = await client.get(
            "/correlations/collector%7Chttp_request%7Cone", auth=operator
        )
        assert detail.is_success and "data-trace-monitor" in detail.text
        latest = await client.get("/api/correlations", auth=operator)
        assert latest.is_success, latest.text
        assert len(latest.json()["events"]) == 2
        for field, value in (("correlation_id", "one"), ("request_id", "request-1")):
            match = await client.get(
                "/api/correlations",
                params={"id_type": field, "id": value},
                auth=operator,
            )
            assert match.is_success, match.text
            assert [event["correlation_id"] for event in match.json()["events"]] == [
                "one"
            ]

        peer_batch = {**batch, "service": "peer", "events": [batch["events"][0]]}
        assert (await client.post(path, headers=ingest, json=peer_batch)).is_success
        reused = await client.get(
            "/api/correlations", params={"id": "one"}, auth=operator
        )
        assert reused.is_success, reused.text
        assert {row["metadata"]["service"] for row in reused.json()["events"]} == {
            "primary",
            "peer",
        }

        operation = {
            "correlation_id": "timed",
            "invocation_id": "timed-operation",
            "op_model": "PilotNote",
            "op_alias": "create",
            "clock_domain": "server_monotonic",
            "source_started_at": "2026-11-25T12:00:00.001Z",
            "source_ended_at": "2026-11-25T12:00:00.025Z",
            "outcome": "ok",
        }
        timed_batch = {
            **batch,
            "events": [
                {
                    **batch["events"][0],
                    "sequence": 3,
                    "fields": {
                        **operation,
                        "timing_boundary": "invocation_monotonic",
                        "measured_duration_ms": 24.0,
                    },
                },
                {
                    **batch["events"][0],
                    "sequence": 4,
                    "kind": "Hook",
                    "fields": {
                        **operation,
                        "hook_name": "validate_note",
                        "hook_phase": "PRE_COMMIT",
                        "timing_boundary": "hook_monotonic",
                        "measured_duration_ms": 0.023,
                        "payload": "private",
                    },
                },
                {
                    **batch["events"][0],
                    "sequence": 5,
                    "kind": "Response",
                    "transport": "HTTP",
                    "fields": {
                        "correlation_id": "timed",
                        "status": 201,
                        "timing_boundary": "ingress_to_egress_monotonic",
                        "clock_domain": "server_monotonic",
                        "measured_duration_ms": 27.0,
                    },
                },
                *(
                    {
                        **batch["events"][0],
                        "sequence": sequence,
                        "kind": "Transaction",
                        "fields": {
                            "correlation_id": "timed",
                            "engine_session_id": "engine",
                            "transaction_id": f"tx-{sequence}",
                            "outcome": outcome,
                            "timing_boundary": boundary,
                            "clock_domain": "engine_monotonic",
                            "measured_duration_ms": 21.0,
                        },
                    }
                    for sequence, outcome, boundary in (
                        (6, "committed", "db_tx_begin_to_commit"),
                        (7, "rolled_back", "db_tx_begin_to_rollback"),
                    )
                ),
                *(
                    {
                        **batch["events"][0],
                        "sequence": sequence,
                        "kind": "Flush",
                        "fields": {
                            "correlation_id": "timed",
                            "invocation_id": "timed-operation",
                            "engine_session_id": "engine",
                            "transaction_id": "tx-6",
                            "flush_id": f"flush-{sequence}",
                            "outcome": outcome,
                            "timing_boundary": "db_flush_monotonic",
                            "clock_domain": "engine_monotonic",
                            "measured_duration_ms": 1.0,
                        },
                    }
                    for sequence, outcome in ((8, "ok"), (9, "failed"))
                ),
            ],
        }
        assert (await client.post(path, headers=ingest, json=timed_batch)).is_success
        timed = await client.get(
            "/api/correlations", params={"id": "timed"}, auth=operator
        )
        assert timed.is_success, timed.text
        events = {event["kind"]: event for event in timed.json()["events"]}
        invocation = events["invocation.completed"]
        hook = events["hook.completed"]
        assert invocation["op_model"] == "PilotNote"
        assert invocation["op_alias"] == "create"
        assert invocation["measured_duration_ms"] == 24.0
        assert hook["invocation_id"] == invocation["invocation_id"]
        assert hook["hook_name"] == "validate_note"
        assert hook["hook_phase"] == "PRE_COMMIT"
        assert hook["measured_duration_ms"] == 0.023
        assert hook["source_started_at"] == operation["source_started_at"]
        response = events["http.response.sent"]
        assert response["measured_duration_ms"] == 27.0
        assert response["timing_boundary"] == "ingress_to_egress_monotonic"
        assert response["clock_domain"] == "server_monotonic"
        for terminal in ("commit", "rollback"):
            transaction = events[f"db.tx.{terminal}"]
            assert transaction["measured_duration_ms"] == 21.0
            assert transaction["timing_boundary"] == f"db_tx_begin_to_{terminal}"
            assert transaction["clock_domain"] == "engine_monotonic"
        for kind, sequence in (("completed", 8), ("failed", 9)):
            flush = events[f"db.flush.{kind}"]
            assert flush["flush_id"] == f"flush-{sequence}"
            assert flush["transaction_id"] == events["db.tx.commit"]["transaction_id"]
            assert flush["invocation_id"] == invocation["invocation_id"]
            assert flush["measured_duration_ms"] == 1.0
        assert "private" not in timed.text
